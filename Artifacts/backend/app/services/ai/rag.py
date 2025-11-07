"""Lightweight RAG helpers for StaffAlloc's AI features."""

from __future__ import annotations

import logging
import math
import re
from collections import Counter, defaultdict
from typing import Iterable, List, Sequence, Tuple

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.utils.reporting import month_label

logger = logging.getLogger(__name__)

_WORD_PATTERN = re.compile(r"[A-Za-z0-9']+")


def _tokenize(text: str) -> List[str]:
    return _WORD_PATTERN.findall(text.lower())


def _truncate(text: str, max_length: int = 3800) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def _project_summary(project: models.Project, assignments: Sequence[models.ProjectAssignment]) -> str:
    funded = sum(assignment.funded_hours for assignment in assignments)
    allocated = sum(
        allocation.allocated_hours
        for assignment in assignments
        for allocation in assignment.allocations or []
    )
    utilization = (allocated / funded * 100.0) if funded else 0.0

    lines: List[str] = [
        f"Project {project.name} ({project.code}) status {project.status}.",
        f"Manager: {project.manager.full_name if project.manager else 'Unassigned'}.",
        f"Start: {project.start_date.isoformat()} · Sprints: {project.sprints}.",
        f"Funded hours: {funded} · Allocated hours: {allocated} · Utilization: {utilization:.1f}%.",
    ]

    for assignment in assignments:
        lines.append(
            f"Assignment – {assignment.user.full_name} as {assignment.role.name} / {assignment.lcat.name}, "
            f"funded {assignment.funded_hours} hours."
        )

        monthly = sorted(
            (
                (allocation.year, allocation.month, allocation.allocated_hours)
                for allocation in assignment.allocations or []
            ),
            key=lambda item: (item[0], item[1]),
        )
        if monthly:
            month_parts = ", ".join(
                f"{month_label(year, month)}: {hours}h" for year, month, hours in monthly
            )
            lines.append(f"Monthly allocations → {month_parts}.")

    if not assignments:
        lines.append("No team members have been assigned yet.")

    return "\n".join(lines)


def _employee_summary(
    user: models.User,
    monthly_allocations: Iterable[Dict[str, object]],
) -> str:
    manager_name = user.manager.full_name if user.manager else "N/A"
    role_str = user.system_role.value if hasattr(user.system_role, 'value') else str(user.system_role)
    lines = [
        f"Employee {user.full_name} ({user.email}) role {role_str}.",
        f"Manager: {manager_name}.",
    ]

    allocations = sorted(
        monthly_allocations,
        key=lambda row: (int(row["year"]), int(row["month"])),
    )

    if not allocations:
        lines.append("No allocations recorded.")
        return "\n".join(lines)

    for row in allocations:
        project_name = str(row.get("project_name") or "Unknown Project")
        year = int(row["year"])
        month = int(row["month"])
        hours = int(row.get("allocated_hours") or 0)
        lines.append(f"{project_name} · {month_label(year, month)}: {hours}h")

    return "\n".join(lines)


def reindex_rag_cache(db: Session, *, manager_id: int | None = None) -> int:
    """Populate the AI RAG cache with project and employee summaries."""

    created = 0

    projects = crud.get_projects(db, limit=500, manager_id=manager_id)
    for project in projects:
        assignments = crud.get_assignments_for_project(db, project_id=project.id)
        document_text = _truncate(_project_summary(project, assignments))
        if not document_text:
            continue
        payload = schemas.AIRagCacheCreate(
            source_entity="project",
            source_id=project.id,
            document_text=document_text,
        )
        crud.create_or_update_rag_cache(db, payload)
        created += 1

    monthly_rows = crud.get_monthly_user_project_allocations(db)
    rows_by_user: Dict[int, List[Dict[str, object]]] = defaultdict(list)
    for row in monthly_rows:
        rows_by_user[int(row["user_id"])].append(row)

    employees = crud.get_users(
        db,
        limit=2000,
        manager_id=manager_id,
        system_role=models.SystemRole.EMPLOYEE,
        include_global=False,
    )
    for employee in employees:
        document_text = _truncate(
            _employee_summary(employee, rows_by_user.get(employee.id, []))
        )
        payload = schemas.AIRagCacheCreate(
            source_entity="employee",
            source_id=employee.id,
            document_text=document_text,
        )
        crud.create_or_update_rag_cache(db, payload)
        created += 1

    logger.info("RAG reindex complete", created_documents=created)
    return created


def retrieve_rag_context(
    db: Session, query: str, limit: int = 5
) -> List[Tuple[str, str]]:
    """Return the most relevant cached documents for the supplied query."""

    documents = crud.get_all_rag_cache_documents(db)
    if not documents:
        logger.info("AI RAG cache empty; rebuilding before retrieval")
        reindex_rag_cache(db)
        documents = crud.get_all_rag_cache_documents(db)

    if not documents:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        query_tokens = query.lower().split()
    query_counts = Counter(query_tokens)

    scored: List[Tuple[float, models.AIRagCache]] = []
    for document in documents:
        doc_tokens = _tokenize(document.document_text)
        if not doc_tokens:
            continue
        doc_counts = Counter(doc_tokens)
        score = sum(query_counts[token] * doc_counts.get(token, 0) for token in query_counts)
        # bonus for entity-specific matches
        key = document.source_entity
        if key == "project" and any(project_token in document.document_text.lower() for project_token in query_tokens):
            score += 1.5
        if key == "employee" and any(employee_token in document.document_text.lower() for employee_token in query_tokens):
            score += 1.25
        # Normalize by document length to avoid bias toward long docs
        normalization = math.sqrt(sum(count * count for count in doc_counts.values())) or 1.0
        score = score / normalization
        scored.append((score, document))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    context: List[Tuple[str, str]] = []
    seen_sources: set[str] = set()
    for score, document in scored:
        source_key = f"{document.source_entity}:{document.source_id}"
        if source_key in seen_sources:
            continue
        if score <= 0 and len(context) >= max(1, limit // 2):
            break
        seen_sources.add(source_key)
        context.append((source_key, document.document_text))
        if len(context) >= limit:
            break

    if len(context) < limit:
        for _, document in scored:
            source_key = f"{document.source_entity}:{document.source_id}"
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)
            context.append((source_key, document.document_text))
            if len(context) >= limit:
                break

    return context[:limit]

