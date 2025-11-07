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
from .rag import retrieve_rag_context

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-pro"

try:  # pragma: no cover - optional dependency during import
    from google import genai  # type: ignore
    from google.genai import types as genai_types  # type: ignore
except ImportError:  # pragma: no cover - handled at runtime when API invoked
    genai = None
    genai_types = None

_CLIENT: Optional["genai.Client"] = None


class GeminiConfigurationError(RuntimeError):
    """Raised when the Gemini client cannot be configured."""


class GeminiInvocationError(RuntimeError):
    """Raised when a Gemini request fails."""


def _ensure_client() -> "genai.Client":
    global _CLIENT
    if genai is None or genai_types is None:  # pragma: no cover - environment dependent
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
    max_output_tokens: int = 1024,
) -> str:
    client = _ensure_client()
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=genai_types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                response_modalities=["TEXT"],
            ),
        )
    except Exception as exc:  # pragma: no cover - network/client dependent
        raise GeminiInvocationError(f"Gemini request failed: {exc!s}") from exc

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
) -> Tuple[str, List[str]]:
    """Return an answer and the supporting sources for an AI chat query."""

    context = retrieve_rag_context(db, query, limit=context_limit)
    if not context:
        logger.info("No RAG context available for query; rebuilding cache")
        context = retrieve_rag_context(db, query, limit=context_limit)

    prompt_context = _format_context_for_prompt(context)
    prompt = (
        "You are StaffAlloc AI, assisting resource managers with staffing insights. "
        "Use ONLY the provided context to answer the user's question accurately. "
        "List specific projects, employees, and hours when relevant. If the context does not contain the answer, "
        "state that you cannot find the requested information. Keep the response concise and actionable.\n\n"
        f"Context:\n{prompt_context}\n\n"
        f"Question: {query}\n"
        "Answer:"
    )

    answer = _call_gemini(prompt)
    sources = [source for source, _ in context]
    return answer, sources


def _monthly_totals_for(db: Session, year: int, month: int) -> Dict[int, int]:
    totals = crud.get_monthly_user_allocation_totals(db)
    return {
        int(row["user_id"]): int(row.get("total_hours") or 0)
        for row in totals
        if int(row["year"]) == year and int(row["month"]) == month
    }


def _user_assignments(db: Session, cache: Dict[int, List[models.ProjectAssignment]], user_id: int) -> List[models.ProjectAssignment]:
    if user_id not in cache:
        cache[user_id] = crud.get_assignments_for_user(db, user_id)
    return cache[user_id]


def recommend_staffing_options(
    db: Session,
    *,
    project_id: int,
    year: int,
    month: int,
    required_hours: int,
    role_id: Optional[int] = None,
    lcat_id: Optional[int] = None,
) -> Tuple[List[Dict[str, object]], str]:
    project = crud.get_project(db, project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    target_role = crud.get_role(db, role_id) if role_id else None
    target_lcat = crud.get_lcat(db, lcat_id) if lcat_id else None

    standard_hours = max(standard_month_hours(year, month), 1)
    month_totals = _monthly_totals_for(db, year, month)

    assignments_cache: Dict[int, List[models.ProjectAssignment]] = {}
    existing_assignments = crud.get_assignments_for_project(db, project_id=project_id)
    existing_user_ids = {assignment.user_id for assignment in existing_assignments}

    employees = crud.get_users(
        db,
        limit=2000,
        system_role=models.SystemRole.EMPLOYEE,
        include_global=False,
    )

    candidates: List[Dict[str, object]] = []
    for employee in employees:
        if employee.id in existing_user_ids:
            continue

        employee_assignments = _user_assignments(db, assignments_cache, employee.id)

        if role_id is not None and not any(a.role_id == role_id for a in employee_assignments):
            continue

        if lcat_id is not None and not any(a.lcat_id == lcat_id for a in employee_assignments):
            continue

        allocated_hours = month_totals.get(employee.id, 0)
        current_fte = allocated_hours / standard_hours
        available_hours = max(standard_hours - allocated_hours, 0)

        candidates.append(
            {
                "user_id": employee.id,
                "full_name": employee.full_name,
                "email": employee.email,
                "manager_id": employee.manager_id,
                "current_fte": round(current_fte, 3),
                "allocated_hours": allocated_hours,
                "available_hours": available_hours,
            }
        )

    candidates.sort(key=lambda item: (-(item["available_hours"] or 0), item["current_fte"]))
    top_candidates = candidates[: min(5, len(candidates))]

    if not top_candidates:
        reasoning = (
            "No employees meet the requested role/LCAT criteria with sufficient capacity in "
            f"{month_label(year, month)}. Consider broadening the requirements or adjusting allocations."
        )
        return [], reasoning

    context_lines = [
        f"Project: {project.name} ({project.code})",  # type: ignore[arg-type]
        f"Timeframe: {month_label(year, month)}",
        f"Required hours: {required_hours}",
        f"Target role: {target_role.name if target_role else 'Any'}, LCAT: {target_lcat.name if target_lcat else 'Any'}",
        "Candidate availability:",
    ]
    for candidate in top_candidates:
        context_lines.append(
            f"- {candidate['full_name']} · current FTE {candidate['current_fte'] * 100:.1f}% "
            f"· available {candidate['available_hours']}h"
        )

    prompt = (
        "You are assisting a project manager in selecting staff. Using the candidate data provided, "
        "recommend who should be staffed to cover the required hours. Reference the best-matched candidates "
        "and note any risks or follow-up actions."
        f"\n\n{os.linesep.join(context_lines)}\n\nRecommendation:"
    )

    reasoning = _call_gemini(prompt, temperature=0.1)
    return top_candidates, reasoning


def _collect_conflict_data(db: Session) -> Tuple[Dict[Tuple[int, int], Dict[int, int]], Dict[int, models.User]]:
    monthly_totals = crud.get_monthly_user_project_allocations(db)
    totals: Dict[Tuple[int, int], Dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for row in monthly_totals:
        key = (int(row["year"]), int(row["month"]))
        user_totals = totals[key]
        user_totals[int(row["user_id"])] += int(row.get("allocated_hours") or 0)

    users = crud.get_users(
        db, limit=2000, system_role=models.SystemRole.EMPLOYEE, include_global=False
    )
    return totals, {user.id: user for user in users}


def scan_allocation_conflicts(db: Session) -> Tuple[List[Dict[str, object]], str]:
    monthly_totals, user_lookup = _collect_conflict_data(db)

    project_breakdown_rows = crud.get_monthly_user_project_allocations(db)
    breakdown: Dict[Tuple[int, int, int], List[Dict[str, object]]] = defaultdict(list)
    for row in project_breakdown_rows:
        key = (int(row["user_id"]), int(row["year"]), int(row["month"]))
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


def generate_forecast_insights(db: Session, *, months_ahead: int = 3) -> Tuple[List[Dict[str, object]], str]:
    today = date.today()
    employees = crud.get_users(
        db, limit=2000, system_role=models.SystemRole.EMPLOYEE, include_global=False
    )
    employee_count = len(employees) or 1

    allocations = crud.get_monthly_user_project_allocations(db)
    allocations_by_month: Dict[Tuple[int, int], int] = defaultdict(int)
    for row in allocations:
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
) -> Tuple[List[Dict[str, object]], str]:
    today = date.today()
    standard_hours = max(standard_month_hours(today.year, today.month), 1)

    monthly_totals = _monthly_totals_for(db, today.year, today.month)

    employees = crud.get_users(
        db, limit=2000, system_role=models.SystemRole.EMPLOYEE, include_global=False
    )
    employee_lookup = {employee.id: employee for employee in employees}

    if project_id is not None:
        assignments = crud.get_assignments_for_project(db, project_id=project_id)
        relevant_user_ids = {assignment.user_id for assignment in assignments}
    else:
        relevant_user_ids = set(employee_lookup.keys())

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
            suggestions.append(
                {
                    "action": "rebalance_allocation",
                    "from_employee": overloaded_user.full_name,
                    "to_employee": idle_user.full_name,
                    "recommended_hours": int(shift_hours),
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

