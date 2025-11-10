"""Gemini-powered AI helpers for StaffAlloc."""

from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app import crud, models
from app.utils.reporting import month_label, standard_month_hours

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.0-flash-lite"  # Fast experimental model, better availability

# Defer genai import to avoid hanging during module import
# The import will happen in _ensure_client() when actually needed
genai = None
genai_types = None

_CLIENT: Optional["genai.Client"] = None


class GeminiConfigurationError(RuntimeError):
    """Raised when the Gemini client cannot be configured."""


class GeminiInvocationError(RuntimeError):
    """Raised when a Gemini request fails."""


def _ensure_client() -> "genai.Client":
    global _CLIENT, genai, genai_types
    
    # Lazy import of genai to avoid hanging during module import
    if genai is None or genai_types is None:
        try:
            from google import genai as _genai  # type: ignore
            from google.genai import types as _genai_types  # type: ignore
            genai = _genai
            genai_types = _genai_types
        except ImportError:  # pragma: no cover - environment dependent
            raise GeminiConfigurationError(
                "google-genai is not installed. Install it with 'pip install google-genai'."
            )

    if _CLIENT is not None:
        return _CLIENT

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise GeminiConfigurationError(
            "GOOGLE_API_KEY is not configured. Add it to the backend .env file so the AI features can access Gemini."
        )

    try:
        _CLIENT = genai.Client(api_key=api_key)
    except Exception as exc:  # pragma: no cover - network/client dependent
        raise GeminiConfigurationError(f"Failed to initialise Gemini client: {exc!s}") from exc

    return _CLIENT


def _call_gemini(
    prompt: str,
    *,
    temperature: float = 0.25,
    max_output_tokens: int = 2048,
) -> str:
    client = _ensure_client()
    
    max_retries = 1  # Reduced retries to fail faster
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            logger.info(f"Calling Gemini API: model={GEMINI_MODEL}, max_tokens={max_output_tokens}, attempt={retry_count+1}")
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt],
                config=genai_types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    response_modalities=["TEXT"],
                ),
            )
            logger.info("Gemini API call successful")
            break
        except Exception as exc:  # pragma: no cover - network/client dependent
            retry_count += 1
            error_str = str(exc).lower()
            logger.error(f"Gemini API call failed: {exc} (attempt {retry_count}/{max_retries+1})")
            
            # Don't retry on certain errors
            if 'rate limit' in error_str or 'quota' in error_str:
                raise GeminiInvocationError(f"API quota exceeded: {exc!s}. Please wait a moment before trying again.") from exc
            
            # If we've exhausted retries, raise the error
            if retry_count > max_retries:
                raise GeminiInvocationError(f"Gemini request failed: {exc!s}. Try a simpler question or wait a moment.") from exc
            
            # Wait before retrying
            import time
            wait_time = 1  # Quick retry for Flash model
            logger.info(f"Retrying in {wait_time} second...")
            time.sleep(wait_time)

    if hasattr(response, "text") and response.text:
        return response.text.strip()

    if getattr(response, "candidates", None):
        fragments: List[str] = []
        for candidate in response.candidates:
            if getattr(candidate, "content", None) and getattr(candidate.content, "parts", None):
                for part in candidate.content.parts:
                    text = getattr(part, "text", None)
                    if text:
                        fragments.append(text)
        if fragments:
            return "\n".join(fragments).strip()

    raise GeminiInvocationError("Gemini did not return any text output.")


def _format_context_for_prompt(context: Iterable[Tuple[str, str]]) -> str:
    sections = []
    for source, chunk in context:
        sections.append(f"Source {source}:\n{chunk}")
    return "\n\n".join(sections)


def suggest_header_mapping(
    *, headers: Sequence[str], required_fields: Sequence[str], sheet_name: str
) -> Dict[str, str]:
    """Use Gemini to map spreadsheet headers to expected field names."""

    prompt = (
        "You are assisting with importing a staffing spreadsheet. "
        "Map each required field to the most appropriate header name from the sheet. "
        "Return a JSON object where keys are the required field codes and values are the exact header text. "
        "If a match cannot be found, use an empty string."
        f"\n\nSheet: {sheet_name}\nHeaders: {headers}\nRequired fields: {required_fields}\n\nJSON mapping:"
    )

    response_text = _call_gemini(prompt, temperature=0.1, max_output_tokens=256)
    try:
        mapping = json.loads(response_text)
    except json.JSONDecodeError as exc:  # pragma: no cover - depends on model output
        raise GeminiInvocationError("Gemini returned an invalid header mapping JSON.") from exc

    if not isinstance(mapping, dict):
        raise GeminiInvocationError("Gemini returned an unexpected header mapping structure.")

    cleaned: Dict[str, str] = {}
    for field in required_fields:
        value = mapping.get(field)
        if isinstance(value, str):
            cleaned[field] = value.strip()
    return cleaned


def generate_chat_response(
    db: Session,
    *,
    query: str,
    context_limit: int,
    manager_id: Optional[int] = None,
) -> Tuple[str, List[str]]:
    """Return an answer and the supporting sources for an AI chat query."""
    from .rag import retrieve_rag_context

    context = retrieve_rag_context(db, query, limit=context_limit, manager_id=manager_id)
    if not context:
        logger.info("No RAG context available for query; rebuilding cache for manager %s", manager_id)
        from .rag import reindex_rag_cache
        reindex_rag_cache(db, manager_id=manager_id)
        context = retrieve_rag_context(db, query, limit=context_limit, manager_id=manager_id)

    prompt_context = _format_context_for_prompt(context)
    
    # Add current date context to help with relative time queries
    from datetime import date
    today = date.today()
    current_month_year = f"{today.strftime('%B %Y')}"
    
    prompt = (
        "You are StaffAlloc AI, assisting resource managers with staffing insights. "
        f"Today is {today.isoformat()} ({current_month_year}). "
        "Standard monthly work hours: 160-176h (depending on the month). 100% FTE = full capacity.\n\n"
        "IMPORTANT: When asked about employee availability or capacity:\n"
        "1. Calculate FTE% from their monthly allocations (total_hours / 176)\n"
        "2. Available hours = 176 - total_hours\n"
        "3. Show who has capacity (FTE < 80%) vs who is overloaded (FTE > 100%)\n"
        "4. List specific numbers: hours, FTE%, and available capacity\n\n"
        "Use the provided context to answer accurately. "
        "List specific employees, projects, hours, and FTE%. "
        "Use markdown: **bold** for names, bullet lists for clarity. "
        "Be concise but complete.\n\n"
        f"Context:\n{prompt_context}\n\n"
        f"Question: {query}\n"
        "Answer:"
    )

    answer = _call_gemini(prompt, max_output_tokens=1024, temperature=0.3)
    sources = [source for source, _ in context]
    return answer, sources


def _monthly_totals_for(db: Session, year: int, month: int) -> Dict[int, int]:
    totals = crud.get_monthly_user_allocation_totals(db)
    return {
        int(row["user_id"]): int(row.get("total_hours") or 0)
        for row in totals
        if int(row["year"]) == year and int(row["month"]) == month
    }


def _collect_conflict_data(db: Session, *, manager_id: Optional[int] = None) -> Tuple[Dict[Tuple[int, int], Dict[int, int]], Dict[int, models.User]]:
    monthly_totals = crud.get_monthly_user_project_allocations(db)
    
    # Get users filtered by manager if specified
    users = crud.get_users(
        db, limit=2000, system_role=models.SystemRole.EMPLOYEE, manager_id=manager_id
    )
    user_ids = {user.id for user in users}
    
    # Filter monthly totals to only include users belonging to this manager
    totals: Dict[Tuple[int, int], Dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for row in monthly_totals:
        user_id = int(row["user_id"])
        if manager_id is None or user_id in user_ids:
            key = (int(row["year"]), int(row["month"]))
            user_totals = totals[key]
            user_totals[user_id] += int(row.get("allocated_hours") or 0)

    return totals, {user.id: user for user in users}


def scan_allocation_conflicts(db: Session, *, manager_id: Optional[int] = None) -> Tuple[List[Dict[str, object]], str]:
    monthly_totals, user_lookup = _collect_conflict_data(db, manager_id=manager_id)
    
    # Get user IDs for filtering
    user_ids = set(user_lookup.keys())

    project_breakdown_rows = crud.get_monthly_user_project_allocations(db)
    breakdown: Dict[Tuple[int, int, int], List[Dict[str, object]]] = defaultdict(list)
    for row in project_breakdown_rows:
        user_id = int(row["user_id"])
        # Only include breakdown for manager's employees
        if manager_id is None or user_id in user_ids:
            key = (user_id, int(row["year"]), int(row["month"]))
            breakdown[key].append(row)

    conflicts: List[Dict[str, object]] = []
    today = date.today()
    for (year, month), totals in monthly_totals.items():
        standard_hours = max(standard_month_hours(year, month), 1)
        for user_id, total_hours in totals.items():
            if total_hours <= standard_hours:
                continue
            user = user_lookup.get(user_id)
            if not user:
                continue

            conflict_key = (user_id, year, month)
            project_rows = breakdown.get(conflict_key, [])
            project_rows.sort(key=lambda row: int(row.get("allocated_hours") or 0), reverse=True)
            project_details = [
                {
                    "project_id": int(row.get("project_id") or 0),
                    "project_name": row.get("project_name") or "Unknown",
                    "hours": int(row.get("allocated_hours") or 0),
                }
                for row in project_rows
            ]

            conflicts.append(
                {
                    "user_id": user_id,
                    "employee": user.full_name,
                    "month": month_label(year, month),
                    "total_hours": total_hours,
                    "fte": round(total_hours / standard_hours, 3),
                    "projects": project_details,
                }
            )

    if not conflicts:
        message = "No over-allocations detected across active projects."
        return [], message

    conflicts.sort(key=lambda item: item["fte"], reverse=True)

    # Generate basic message even without AI
    conflict_count = len(conflicts)
    max_fte = max(c["fte"] for c in conflicts) * 100
    message = f"Found {conflict_count} over-allocation{'s' if conflict_count != 1 else ''} (max {max_fte:.1f}% FTE). "

    # Try to get AI reasoning, but don't fail if unavailable
    try:
        prompt_lines = [
            "The following employees exceed 100% FTE. Provide actionable remediation steps, "
            "suggesting which project allocations to reduce or shift, and highlight any follow-up required.",
            "Conflicts:",
        ]
        for conflict in conflicts[:5]:
            projects = ", ".join(
                f"{proj['project_name']} ({proj['hours']}h)" for proj in conflict["projects"]
            )
            prompt_lines.append(
                f"- {conflict['employee']} · {conflict['month']} · {conflict['fte'] * 100:.1f}% FTE · {projects}"
            )

        prompt = "\n".join(prompt_lines) + "\n\nMitigation guidance:"
        reasoning = _call_gemini(prompt, temperature=0.2)
        message += reasoning
    except (GeminiConfigurationError, GeminiInvocationError):
        # Provide basic guidance without AI
        message += "Review allocations and consider: (1) Reducing hours on lower-priority projects, (2) Redistributing work to available team members, or (3) Adjusting project timelines."

    return conflicts, message


def generate_forecast_insights(db: Session, *, months_ahead: int = 3, manager_id: Optional[int] = None) -> Tuple[List[Dict[str, object]], str]:
    today = date.today()
    employees = crud.get_users(
        db, limit=2000, system_role=models.SystemRole.EMPLOYEE, manager_id=manager_id
    )
    employee_count = len(employees) or 1
    user_ids = {employee.id for employee in employees}

    allocations = crud.get_monthly_user_project_allocations(db)
    allocations_by_month: Dict[Tuple[int, int], int] = defaultdict(int)
    for row in allocations:
        user_id = int(row["user_id"])
        # Only include allocations for manager's employees
        if manager_id is None or user_id in user_ids:
            key = (int(row["year"]), int(row["month"]))
            allocations_by_month[key] += int(row.get("allocated_hours") or 0)

    predictions: List[Dict[str, object]] = []
    current_year = today.year
    current_month = today.month
    for offset in range(months_ahead):
        year = current_year + (current_month + offset - 1) // 12
        month = ((current_month + offset - 1) % 12) + 1
        month_key = (year, month)
        allocated = allocations_by_month.get(month_key, 0)
        capacity = employee_count * standard_month_hours(year, month)
        variance = capacity - allocated
        predictions.append(
            {
                "month": month_label(year, month),
                "projected_capacity_hours": capacity,
                "projected_allocated_hours": allocated,
                "surplus_hours": variance,
                "risk": "shortage" if variance < 0 else ("underutilized" if variance > capacity * 0.25 else "balanced"),
            }
        )

    # Generate basic message
    shortages = [p for p in predictions if p["risk"] == "shortage"]
    underutilized = [p for p in predictions if p["risk"] == "underutilized"]
    
    if shortages:
        message = f"Warning: {len(shortages)} month(s) show capacity shortage. "
    elif underutilized:
        message = f"Notice: {len(underutilized)} month(s) show underutilization. "
    else:
        message = "Forecast shows balanced capacity for the next months. "

    # Try to get AI reasoning
    try:
        context = [
            "Provide staffing forecast guidance based on capacity vs projected allocation.",
            f"Total employees considered: {employee_count}",
        ]
        for item in predictions:
            context.append(
                f"- {item['month']}: capacity {item['projected_capacity_hours']}h, allocations {item['projected_allocated_hours']}h, surplus {item['surplus_hours']}h ({item['risk']})"
            )

        prompt = (
            "You are advising a portfolio manager on staffing outlook. Summarise the key risks for the upcoming months, "
            "highlight shortages or underutilisation, and recommend proactive steps (hiring, reassignments, etc.).\n\n"
            + "\n".join(context)
            + "\n\nOutlook:"
        )

        reasoning = _call_gemini(prompt, temperature=0.3)
        message += reasoning
    except (GeminiConfigurationError, GeminiInvocationError):
        # Provide basic guidance without AI
        if shortages:
            message += "Consider hiring additional staff or adjusting project timelines to meet demand."
        elif underutilized:
            message += "Consider taking on new projects or reassigning staff to higher-priority work."
        else:
            message += "Continue monitoring allocations and adjust as new projects are added."

    return predictions, message


def generate_workload_balance_suggestions(
    db: Session,
    *,
    project_id: Optional[int] = None,
    manager_id: Optional[int] = None,
) -> Tuple[List[Dict[str, object]], str]:
    today = date.today()
    standard_hours = max(standard_month_hours(today.year, today.month), 1)

    all_monthly_totals = _monthly_totals_for(db, today.year, today.month)

    employees = crud.get_users(
        db, limit=2000, system_role=models.SystemRole.EMPLOYEE, manager_id=manager_id
    )
    employee_lookup = {employee.id: employee for employee in employees}
    user_ids = set(employee_lookup.keys())
    
    # Filter monthly totals to only include manager's employees
    monthly_totals = {user_id: hours for user_id, hours in all_monthly_totals.items() if manager_id is None or user_id in user_ids}

    if project_id is not None:
        assignments = crud.get_assignments_for_project(db, project_id=project_id)
        # Filter to only include manager's employees
        relevant_user_ids = {assignment.user_id for assignment in assignments if assignment.user_id in user_ids}
    else:
        relevant_user_ids = user_ids

    over_allocated: List[Tuple[models.User, int, float]] = []
    under_allocated: List[Tuple[models.User, int, float]] = []

    for user_id in relevant_user_ids:
        user = employee_lookup.get(user_id)
        if not user:
            continue
        hours = monthly_totals.get(user_id, 0)
        fte = hours / standard_hours
        if fte > 1.0:
            over_allocated.append((user, hours, fte))
        elif fte < 0.5:
            under_allocated.append((user, hours, fte))

    # Get project assignments for overloaded and underutilized users to provide context
    from_user_ids = [user.id for user, _, _ in over_allocated]
    to_user_ids = [user.id for user, _, _ in under_allocated]
    
    # Fetch all relevant assignments
    from_assignments_map = {}
    to_assignments_map = {}
    
    for user_id in from_user_ids:
        assignments = crud.get_assignments_for_user(db, user_id)
        # Get allocations for current month
        from_assignments_map[user_id] = []
        for assignment in assignments:
            project = crud.get_project(db, assignment.project_id)
            if project:
                # Check if there are allocations for this month
                current_month_allocs = [a for a in assignment.allocations if a.year == today.year and a.month == today.month and a.allocated_hours > 0]
                if current_month_allocs:
                    from_assignments_map[user_id].append({
                        'project_id': project.id,
                        'project_name': project.name,
                        'assignment_id': assignment.id
                    })
    
    for user_id in to_user_ids:
        assignments = crud.get_assignments_for_user(db, user_id)
        to_assignments_map[user_id] = []
        for assignment in assignments:
            project = crud.get_project(db, assignment.project_id)
            if project:
                to_assignments_map[user_id].append({
                    'project_id': project.id,
                    'project_name': project.name,
                    'assignment_id': assignment.id
                })
    
    suggestions: List[Dict[str, object]] = []
    for overloaded_user, overloaded_hours, fte in sorted(over_allocated, key=lambda item: item[2], reverse=True):
        overload_amount = overloaded_hours - standard_hours
        if overload_amount <= 0:
            continue
        for idle_user, idle_hours, idle_fte in sorted(under_allocated, key=lambda item: item[2]):
            available = standard_hours - idle_hours
            if available <= 0:
                continue
            shift_hours = min(overload_amount, available, standard_hours // 2)
            if shift_hours <= 0:
                continue
            # Calculate FTE percentages
            from_fte = round(overloaded_hours / standard_hours, 2)
            to_fte = round(idle_hours / standard_hours, 2)
            from_fte_after = round((overloaded_hours - shift_hours) / standard_hours, 2)
            to_fte_after = round((idle_hours + shift_hours) / standard_hours, 2)
            
            reasoning = f"Transfer {int(shift_hours)}h to balance workload. {overloaded_user.full_name} will go from {int(from_fte * 100)}% to {int(from_fte_after * 100)}% FTE, while {idle_user.full_name} will go from {int(to_fte * 100)}% to {int(to_fte_after * 100)}% FTE."
            
            # Get projects for both employees
            from_projects = from_assignments_map.get(overloaded_user.id, [])
            to_projects = to_assignments_map.get(idle_user.id, [])
            
            suggestions.append(
                {
                    "action": "rebalance_allocation",
                    "from_employee": overloaded_user.full_name,
                    "from_employee_id": overloaded_user.id,
                    "from_employee_current_fte": from_fte,
                    "from_employee_current_hours": int(overloaded_hours),
                    "from_employee_projects": from_projects,
                    "to_employee": idle_user.full_name,
                    "to_employee_id": idle_user.id,
                    "to_employee_current_fte": to_fte,
                    "to_employee_current_hours": int(idle_hours),
                    "to_employee_projects": to_projects,
                    "recommended_hours": int(shift_hours),
                    "reasoning": reasoning,
                }
            )
            overload_amount -= shift_hours
            idle_hours += shift_hours
            if overload_amount <= 0:
                break

    if not suggestions:
        message = "No obvious workload imbalances detected for the selected scope."
        return [], message

    scope_label = "project" if project_id is not None else "portfolio"
    suggestion_count = len(suggestions)
    message = f"Found {suggestion_count} workload balancing opportunit{'ies' if suggestion_count != 1 else 'y'} in the {scope_label}. "

    # Try to get AI reasoning, but provide basic guidance if unavailable
    try:
        prompt_lines = [
            f"Workload balancing opportunities detected within the {scope_label}.",
            "Recommendations:",
        ]
        for suggestion in suggestions[:5]:
            prompt_lines.append(
                f"- Shift {suggestion['recommended_hours']}h from {suggestion['from_employee']} to {suggestion['to_employee']}"
            )

        prompt = "\n".join(prompt_lines) + "\n\nRationale:"
        reasoning = _call_gemini(prompt, temperature=0.2)
        message += reasoning
    except (GeminiConfigurationError, GeminiInvocationError):
        # Provide basic guidance without AI
        message += "Consider redistributing work from overloaded employees to those with capacity. This will improve team morale and reduce burnout risk."

    return suggestions, message

