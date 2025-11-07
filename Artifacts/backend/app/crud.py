# crud.py
"""
CRUD (Create, Read, Update, Delete) operations for the StaffAlloc application.

This module provides database access functions for all models. It uses the
Repository pattern to abstract SQLAlchemy query logic from the service and
API layers.

All functions accept a SQLAlchemy Session and return model instances or lists.
These functions are called by the API routers via dependency injection.
"""
import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from . import models, schemas


# --------------------------------------------------------------------------------
# User CRUD
# --------------------------------------------------------------------------------


def create_user(db: Session, user: schemas.UserCreate, password_hash: str) -> models.User:
    """
    Creates a new user in the database.
    Note: Password hashing should be done in the service layer before calling this.
    """
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        system_role=user.system_role,
        is_active=user.is_active,
        password_hash=password_hash,
        manager_id=user.manager_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Retrieves a single user by their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Retrieves a single user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    *,
    manager_id: Optional[int] = None,
    system_role: Optional[models.SystemRole] = None,
    include_global: bool = False,
) -> List[models.User]:
    """Retrieves a list of users with optional manager and role filtering."""
    query = db.query(models.User)

    if system_role:
        query = query.filter(models.User.system_role == system_role)

    if manager_id is not None:
        if include_global:
            query = query.filter(
                or_(
                    models.User.manager_id == manager_id,
                    models.User.system_role != models.SystemRole.EMPLOYEE,
                )
            )
        else:
            query = query.filter(models.User.manager_id == manager_id)

    return (
        query.order_by(models.User.full_name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_user(
    db: Session, user_id: int, user_update: schemas.UserUpdate
) -> Optional[models.User]:
    """Updates an existing user."""
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Deletes a user from the database."""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# --------------------------------------------------------------------------------
# Role CRUD
# --------------------------------------------------------------------------------


def create_role(
    db: Session, role: schemas.RoleCreate, *, owner_id: Optional[int] = None
) -> models.Role:
    """Creates a new role scoped to an owner when provided."""
    payload = role.model_dump()
    if owner_id is not None:
        payload["owner_id"] = owner_id
    db_role = models.Role(**payload)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_role(db: Session, role_id: int) -> Optional[models.Role]:
    """Retrieves a single role by its ID."""
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_role_by_name(db: Session, name: str, owner_id: Optional[int]) -> Optional[models.Role]:
    """Retrieve a role by name scoped to an owner (or shared role)."""
    query = db.query(models.Role).filter(models.Role.name == name)
    if owner_id is not None:
        query = query.filter(
            (models.Role.owner_id == owner_id) | (models.Role.owner_id.is_(None))
        )
    return query.first()


def get_roles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    *,
    owner_id: Optional[int] = None,
    include_global: bool = True,
) -> List[models.Role]:
    """Retrieves a list of roles with optional owner filtering."""
    query = db.query(models.Role)
    if owner_id is not None:
        if include_global:
            query = query.filter(
                or_(
                    models.Role.owner_id == owner_id,
                    models.Role.owner_id.is_(None),
                )
            )
        else:
            query = query.filter(models.Role.owner_id == owner_id)

    return query.order_by(models.Role.name).offset(skip).limit(limit).all()


def update_role(
    db: Session, role_id: int, role_update: schemas.RoleUpdate
) -> Optional[models.Role]:
    """Updates an existing role."""
    db_role = get_role(db, role_id)
    if db_role:
        update_data = role_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_role, key, value)
        db.commit()
        db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int) -> bool:
    """Deletes a role."""
    db_role = get_role(db, role_id)
    if db_role:
        db.delete(db_role)
        db.commit()
        return True
    return False


# --------------------------------------------------------------------------------
# LCAT CRUD
# --------------------------------------------------------------------------------


def create_lcat(
    db: Session, lcat: schemas.LCATCreate, *, owner_id: Optional[int] = None
) -> models.LCAT:
    """Creates a new LCAT scoped to an owner when provided."""
    payload = lcat.model_dump()
    if owner_id is not None:
        payload["owner_id"] = owner_id
    db_lcat = models.LCAT(**payload)
    db.add(db_lcat)
    db.commit()
    db.refresh(db_lcat)
    return db_lcat


def get_lcat(db: Session, lcat_id: int) -> Optional[models.LCAT]:
    """Retrieves a single LCAT by its ID."""
    return db.query(models.LCAT).filter(models.LCAT.id == lcat_id).first()


def get_lcat_by_name(db: Session, name: str, owner_id: Optional[int]) -> Optional[models.LCAT]:
    """Retrieve an LCAT by name scoped to an owner (or shared)."""
    query = db.query(models.LCAT).filter(models.LCAT.name == name)
    if owner_id is not None:
        query = query.filter(
            (models.LCAT.owner_id == owner_id) | (models.LCAT.owner_id.is_(None))
        )
    return query.first()


def get_lcats(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    *,
    owner_id: Optional[int] = None,
    include_global: bool = True,
) -> List[models.LCAT]:
    """Retrieves a list of LCATs with optional owner filtering."""
    query = db.query(models.LCAT)
    if owner_id is not None:
        if include_global:
            query = query.filter(
                or_(
                    models.LCAT.owner_id == owner_id,
                    models.LCAT.owner_id.is_(None),
                )
            )
        else:
            query = query.filter(models.LCAT.owner_id == owner_id)

    return query.order_by(models.LCAT.name).offset(skip).limit(limit).all()


def update_lcat(
    db: Session, lcat_id: int, lcat_update: schemas.LCATUpdate
) -> Optional[models.LCAT]:
    """Updates an existing LCAT."""
    db_lcat = get_lcat(db, lcat_id)
    if db_lcat:
        update_data = lcat_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_lcat, key, value)
        db.commit()
        db.refresh(db_lcat)
    return db_lcat


def delete_lcat(db: Session, lcat_id: int) -> bool:
    """Deletes an LCAT."""
    db_lcat = get_lcat(db, lcat_id)
    if db_lcat:
        db.delete(db_lcat)
        db.commit()
        return True
    return False


# --------------------------------------------------------------------------------
# Project CRUD
# --------------------------------------------------------------------------------


def create_project(db: Session, project: schemas.ProjectCreate) -> models.Project:
    """Creates a new project."""
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: int) -> Optional[models.Project]:
    """Retrieves a single project by its ID."""
    return (
        db.query(models.Project)
        .options(
            joinedload(models.Project.viewer_links).joinedload(models.ProjectViewer.user),
            joinedload(models.Project.manager),
        )
        .filter(models.Project.id == project_id)
        .first()
    )


def get_project_by_code(
    db: Session, code: str, *, manager_id: Optional[int] = None
) -> Optional[models.Project]:
    """Retrieves a single project by its code, optionally scoped to a manager."""
    query = db.query(models.Project).filter(models.Project.code == code)
    if manager_id is not None:
        query = query.filter(models.Project.manager_id == manager_id)
    return query.first()


def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    *,
    manager_id: Optional[int] = None,
    viewer_user_id: Optional[int] = None,
) -> List[models.Project]:
    """Retrieves a list of projects with optional manager/viewer filtering."""
    query = db.query(models.Project)

    if manager_id is not None:
        query = query.filter(models.Project.manager_id == manager_id)

    if viewer_user_id is not None:
        query = (
            query.join(models.ProjectViewer)
            .filter(models.ProjectViewer.user_id == viewer_user_id)
            .distinct()
        )

    return query.order_by(models.Project.name).offset(skip).limit(limit).all()


def update_project(
    db: Session, project_id: int, project_update: schemas.ProjectUpdate
) -> Optional[models.Project]:
    """Updates an existing project."""
    db_project = get_project(db, project_id)
    if db_project:
        update_data = project_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int) -> bool:
    """Deletes a project."""
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False


# --- Project Specialized Queries ---


def get_projects_for_user(db: Session, user_id: int) -> List[models.Project]:
    """Retrieves all projects a user is assigned to."""
    return (
        db.query(models.Project)
        .join(models.ProjectAssignment)
        .filter(models.ProjectAssignment.user_id == user_id)
        .distinct()
        .all()
    )


def get_projects_managed_by_user(db: Session, manager_id: int) -> List[models.Project]:
    """Retrieves all projects managed by a specific user."""
    return db.query(models.Project).filter(models.Project.manager_id == manager_id).all()


def add_project_viewer(
    db: Session,
    *,
    project_id: int,
    user_id: int,
    granted_by_id: Optional[int] = None,
) -> models.ProjectViewer:
    """Adds a viewer to a project."""
    db_viewer = models.ProjectViewer(
        project_id=project_id,
        user_id=user_id,
        granted_by_id=granted_by_id,
    )
    db.add(db_viewer)
    db.commit()
    db.refresh(db_viewer)
    return db_viewer


def get_project_viewer(
    db: Session, *, project_id: int, user_id: int
) -> Optional[models.ProjectViewer]:
    """Fetches a specific project viewer link."""
    return (
        db.query(models.ProjectViewer)
        .filter(
            models.ProjectViewer.project_id == project_id,
            models.ProjectViewer.user_id == user_id,
        )
        .first()
    )


def get_project_viewers(
    db: Session, project_id: int
) -> List[models.ProjectViewer]:
    """Retrieves all viewer links for a project."""
    return (
        db.query(models.ProjectViewer)
        .filter(models.ProjectViewer.project_id == project_id)
        .options(joinedload(models.ProjectViewer.user))
        .order_by(models.ProjectViewer.created_at.desc())
        .all()
    )


def remove_project_viewer(
    db: Session, *, project_id: int, user_id: int
) -> bool:
    """Removes a viewer from a project."""
    db_viewer = get_project_viewer(db, project_id=project_id, user_id=user_id)
    if not db_viewer:
        return False
    db.delete(db_viewer)
    db.commit()
    return True


# --------------------------------------------------------------------------------
# ProjectAssignment CRUD
# --------------------------------------------------------------------------------


def create_project_assignment(
    db: Session, assignment: schemas.ProjectAssignmentCreate
) -> models.ProjectAssignment:
    """Creates a new project assignment."""
    db_assignment = models.ProjectAssignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def get_project_assignment(
    db: Session, assignment_id: int
) -> Optional[models.ProjectAssignment]:
    """Retrieves a single project assignment by its ID."""
    return (
        db.query(models.ProjectAssignment)
        .filter(models.ProjectAssignment.id == assignment_id)
        .first()
    )


def get_project_assignments(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.ProjectAssignment]:
    """Retrieves a list of project assignments with pagination."""
    return db.query(models.ProjectAssignment).offset(skip).limit(limit).all()


def update_project_assignment(
    db: Session, assignment_id: int, assignment_update: schemas.ProjectAssignmentUpdate
) -> Optional[models.ProjectAssignment]:
    """Updates an existing project assignment."""
    db_assignment = get_project_assignment(db, assignment_id)
    if db_assignment:
        update_data = assignment_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_assignment, key, value)
        db.commit()
        db.refresh(db_assignment)
    return db_assignment


def delete_project_assignment(db: Session, assignment_id: int) -> bool:
    """Deletes a project assignment."""
    db_assignment = get_project_assignment(db, assignment_id)
    if db_assignment:
        db.delete(db_assignment)
        db.commit()
        return True
    return False


# --- ProjectAssignment Specialized Queries ---


def get_assignments_for_project(
    db: Session, project_id: int
) -> List[models.ProjectAssignment]:
    """Retrieves all assignments for a specific project, with related user/role data."""
    return (
        db.query(models.ProjectAssignment)
        .filter(models.ProjectAssignment.project_id == project_id)
        .options(
            joinedload(models.ProjectAssignment.user),
            joinedload(models.ProjectAssignment.role),
            joinedload(models.ProjectAssignment.lcat),
            joinedload(models.ProjectAssignment.project),
        )
        .all()
    )


def get_assignments_for_user(
    db: Session, user_id: int
) -> List[models.ProjectAssignment]:
    """Retrieves all assignments for a specific user, with related project/role data."""
    return (
        db.query(models.ProjectAssignment)
        .filter(models.ProjectAssignment.user_id == user_id)
        .options(
            joinedload(models.ProjectAssignment.project),
            joinedload(models.ProjectAssignment.role),
            joinedload(models.ProjectAssignment.lcat),
            joinedload(models.ProjectAssignment.allocations),
        )
        .all()
    )


def get_assignment_by_user_and_project(
    db: Session, user_id: int, project_id: int
) -> Optional[models.ProjectAssignment]:
    """Retrieves a specific assignment by user and project IDs."""
    return (
        db.query(models.ProjectAssignment)
        .filter(
            models.ProjectAssignment.user_id == user_id,
            models.ProjectAssignment.project_id == project_id,
        )
        .first()
    )


# --------------------------------------------------------------------------------
# Allocation CRUD
# --------------------------------------------------------------------------------


def create_allocation(db: Session, allocation: schemas.AllocationCreate) -> models.Allocation:
    """Creates a new allocation."""
    db_allocation = models.Allocation(**allocation.model_dump())
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    return db_allocation


def get_allocation(db: Session, allocation_id: int) -> Optional[models.Allocation]:
    """Retrieves a single allocation by its ID."""
    return (
        db.query(models.Allocation).filter(models.Allocation.id == allocation_id).first()
    )


def get_allocations(
    db: Session, skip: int = 0, limit: int = 1000
) -> List[models.Allocation]:
    """Retrieves a list of allocations with pagination."""
    return db.query(models.Allocation).offset(skip).limit(limit).all()


def update_allocation(
    db: Session, allocation_id: int, allocation_update: schemas.AllocationUpdate
) -> Optional[models.Allocation]:
    """Updates an existing allocation."""
    db_allocation = get_allocation(db, allocation_id)
    if db_allocation:
        update_data = allocation_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_allocation, key, value)
        db.commit()
        db.refresh(db_allocation)
    return db_allocation


def delete_allocation(db: Session, allocation_id: int) -> bool:
    """Deletes an allocation."""
    db_allocation = get_allocation(db, allocation_id)
    if db_allocation:
        db.delete(db_allocation)
        db.commit()
        return True
    return False


# --- Allocation Specialized Queries ---


def get_allocations_for_assignment(
    db: Session, assignment_id: int
) -> List[models.Allocation]:
    """Retrieves all allocations for a specific project assignment."""
    return (
        db.query(models.Allocation)
        .filter(models.Allocation.project_assignment_id == assignment_id)
        .order_by(models.Allocation.year, models.Allocation.month)
        .all()
    )


def get_user_allocation_summary(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Calculates the total allocated hours per month for a given user across all projects.
    Returns a list of dicts, e.g., [{'year': 2023, 'month': 10, 'total_hours': 160}, ...]
    """
    summary = (
        db.query(
            models.Allocation.year,
            models.Allocation.month,
            func.sum(models.Allocation.allocated_hours).label("total_hours"),
        )
        .join(models.ProjectAssignment)
        .filter(models.ProjectAssignment.user_id == user_id)
        .group_by(models.Allocation.year, models.Allocation.month)
        .order_by(models.Allocation.year, models.Allocation.month)
        .all()
    )
    return [row._asdict() for row in summary]


# --------------------------------------------------------------------------------
# Reporting / Analytics Helpers
# --------------------------------------------------------------------------------


def get_role_capacity_summary(db: Session) -> List[Dict[str, Any]]:
    """Aggregate funded vs allocated hours per role across all assignments."""

    assignments_sq = (
        db.query(
            models.ProjectAssignment.id.label("assignment_id"),
            models.ProjectAssignment.role_id.label("role_id"),
            models.ProjectAssignment.funded_hours.label("funded_hours"),
        ).subquery()
    )

    allocations_sq = (
        db.query(
            models.Allocation.project_assignment_id.label("assignment_id"),
            func.sum(models.Allocation.allocated_hours).label("allocated_hours"),
        )
        .group_by(models.Allocation.project_assignment_id)
        .subquery()
    )

    rows = (
        db.query(
            models.Role.id.label("role_id"),
            models.Role.name.label("role_name"),
            func.coalesce(func.sum(assignments_sq.c.funded_hours), 0).label(
                "funded_hours"
            ),
            func.coalesce(
                func.sum(func.coalesce(allocations_sq.c.allocated_hours, 0)), 0
            ).label("allocated_hours"),
        )
        .join(assignments_sq, assignments_sq.c.role_id == models.Role.id)
        .outerjoin(
            allocations_sq,
            allocations_sq.c.assignment_id == assignments_sq.c.assignment_id,
        )
        .group_by(models.Role.id, models.Role.name)
        .all()
    )

    return [dict(row._mapping) for row in rows]


def get_monthly_user_allocation_totals(db: Session) -> List[Dict[str, Any]]:
    """Return total allocated hours per user/month across all assignments."""

    rows = (
        db.query(
            models.ProjectAssignment.user_id.label("user_id"),
            models.Allocation.year.label("year"),
            models.Allocation.month.label("month"),
            func.sum(models.Allocation.allocated_hours).label("total_hours"),
        )
        .join(
            models.Allocation,
            models.Allocation.project_assignment_id == models.ProjectAssignment.id,
        )
        .group_by(
            models.ProjectAssignment.user_id, models.Allocation.year, models.Allocation.month
        )
        .all()
    )

    return [dict(row._mapping) for row in rows]


def get_monthly_user_project_allocations(
    db: Session, *, user_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Return allocated hours per user/project/month for detailed breakdowns."""

    query = (
        db.query(
            models.ProjectAssignment.user_id.label("user_id"),
            models.ProjectAssignment.project_id.label("project_id"),
            models.Project.name.label("project_name"),
            models.Allocation.year.label("year"),
            models.Allocation.month.label("month"),
            func.sum(models.Allocation.allocated_hours).label("allocated_hours"),
        )
        .join(
            models.Allocation,
            models.Allocation.project_assignment_id == models.ProjectAssignment.id,
        )
        .join(models.Project, models.Project.id == models.ProjectAssignment.project_id)
    )

    if user_id is not None:
        query = query.filter(models.ProjectAssignment.user_id == user_id)

    rows = query.group_by(
        models.ProjectAssignment.user_id,
        models.ProjectAssignment.project_id,
        models.Project.name,
        models.Allocation.year,
        models.Allocation.month,
    ).all()

    return [dict(row._mapping) for row in rows]


def get_user_role_funding_totals(db: Session) -> List[Dict[str, Any]]:
    """Return funded hour totals per user/role pair to infer primary roles."""

    rows = (
        db.query(
            models.ProjectAssignment.user_id.label("user_id"),
            models.Role.name.label("role_name"),
            func.sum(models.ProjectAssignment.funded_hours).label("funded_hours"),
        )
        .join(models.Role, models.Role.id == models.ProjectAssignment.role_id)
        .group_by(models.ProjectAssignment.user_id, models.Role.name)
        .all()
    )

    return [dict(row._mapping) for row in rows]


def get_project_monthly_allocations(
    db: Session, project_id: int
) -> List[Dict[str, Any]]:
    """Return monthly allocated hours for a given project."""

    rows = (
        db.query(
            models.Allocation.year.label("year"),
            models.Allocation.month.label("month"),
            func.sum(models.Allocation.allocated_hours).label("allocated_hours"),
        )
        .join(
            models.ProjectAssignment,
            models.ProjectAssignment.id == models.Allocation.project_assignment_id,
        )
        .filter(models.ProjectAssignment.project_id == project_id)
        .group_by(models.Allocation.year, models.Allocation.month)
        .order_by(models.Allocation.year, models.Allocation.month)
        .all()
    )

    return [dict(row._mapping) for row in rows]


def get_project_funded_and_allocated_totals(db: Session, project_id: int) -> Dict[str, int]:
    """Return funded vs allocated totals for a project."""

    funded = (
        db.query(func.coalesce(func.sum(models.ProjectAssignment.funded_hours), 0))
        .filter(models.ProjectAssignment.project_id == project_id)
        .scalar()
    ) or 0

    allocated = (
        db.query(func.coalesce(func.sum(models.Allocation.allocated_hours), 0))
        .join(
            models.ProjectAssignment,
            models.ProjectAssignment.id == models.Allocation.project_assignment_id,
        )
        .filter(models.ProjectAssignment.project_id == project_id)
        .scalar()
    ) or 0

    return {"funded_hours": int(funded), "allocated_hours": int(allocated)}


def get_role_utilization_snapshot(
    db: Session, *, year: int, month: int
) -> List[Dict[str, Any]]:
    """Return allocated vs funded snapshots per role for a specific month."""

    monthly_allocations_sq = (
        db.query(
            models.ProjectAssignment.role_id.label("role_id"),
            func.sum(models.Allocation.allocated_hours).label("allocated_hours"),
        )
        .join(
            models.Allocation,
            and_(
                models.Allocation.project_assignment_id
                == models.ProjectAssignment.id,
                models.Allocation.year == year,
                models.Allocation.month == month,
            ),
        )
        .group_by(models.ProjectAssignment.role_id)
        .subquery()
    )

    assignment_totals_sq = (
        db.query(
            models.ProjectAssignment.role_id.label("role_id"),
            func.sum(models.ProjectAssignment.funded_hours).label("funded_hours"),
            func.count(models.ProjectAssignment.id).label("assignment_count"),
        )
        .group_by(models.ProjectAssignment.role_id)
        .subquery()
    )

    rows = (
        db.query(
            models.Role.id.label("role_id"),
            models.Role.name.label("role_name"),
            func.coalesce(monthly_allocations_sq.c.allocated_hours, 0).label(
                "allocated_hours"
            ),
            func.coalesce(assignment_totals_sq.c.funded_hours, 0).label(
                "funded_hours"
            ),
            func.coalesce(assignment_totals_sq.c.assignment_count, 0).label(
                "assignment_count"
            ),
        )
        .join(
            assignment_totals_sq,
            assignment_totals_sq.c.role_id == models.Role.id,
            isouter=True,
        )
        .join(
            monthly_allocations_sq,
            monthly_allocations_sq.c.role_id == models.Role.id,
            isouter=True,
        )
        .filter(
            or_(
                assignment_totals_sq.c.role_id.isnot(None),
                monthly_allocations_sq.c.role_id.isnot(None),
            )
        )
        .all()
    )

    return [dict(row._mapping) for row in rows]


# --------------------------------------------------------------------------------
# MonthlyHourOverride CRUD
# --------------------------------------------------------------------------------


def create_monthly_hour_override(
    db: Session, override: schemas.MonthlyHourOverrideCreate
) -> models.MonthlyHourOverride:
    """Creates a new monthly hour override."""
    db_override = models.MonthlyHourOverride(**override.model_dump())
    db.add(db_override)
    db.commit()
    db.refresh(db_override)
    return db_override


def get_monthly_hour_override(
    db: Session, override_id: int
) -> Optional[models.MonthlyHourOverride]:
    """Retrieves a single monthly hour override by its ID."""
    return (
        db.query(models.MonthlyHourOverride)
        .filter(models.MonthlyHourOverride.id == override_id)
        .first()
    )


def get_monthly_hour_overrides(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.MonthlyHourOverride]:
    """Retrieves a list of monthly hour overrides with pagination."""
    return db.query(models.MonthlyHourOverride).offset(skip).limit(limit).all()


def update_monthly_hour_override(
    db: Session, override_id: int, override_update: schemas.MonthlyHourOverrideUpdate
) -> Optional[models.MonthlyHourOverride]:
    """Updates an existing monthly hour override."""
    db_override = get_monthly_hour_override(db, override_id)
    if db_override:
        update_data = override_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_override, key, value)
        db.commit()
        db.refresh(db_override)
    return db_override


def delete_monthly_hour_override(db: Session, override_id: int) -> bool:
    """Deletes a monthly hour override."""
    db_override = get_monthly_hour_override(db, override_id)
    if db_override:
        db.delete(db_override)
        db.commit()
        return True
    return False


# --- MonthlyHourOverride Specialized Queries ---


def get_overrides_for_project(
    db: Session, project_id: int
) -> List[models.MonthlyHourOverride]:
    """Retrieves all monthly hour overrides for a specific project."""
    return (
        db.query(models.MonthlyHourOverride)
        .filter(models.MonthlyHourOverride.project_id == project_id)
        .order_by(models.MonthlyHourOverride.year, models.MonthlyHourOverride.month)
        .all()
    )


# --------------------------------------------------------------------------------
# AIRecommendation CRUD
# --------------------------------------------------------------------------------


def create_ai_recommendation(
    db: Session, recommendation: schemas.AIRecommendationCreate
) -> models.AIRecommendation:
    """Creates a new AI recommendation."""
    db_recommendation = models.AIRecommendation(**recommendation.model_dump())
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation


def get_ai_recommendation(
    db: Session, recommendation_id: int
) -> Optional[models.AIRecommendation]:
    """Retrieves a single AI recommendation by its ID."""
    return (
        db.query(models.AIRecommendation)
        .filter(models.AIRecommendation.id == recommendation_id)
        .first()
    )


def get_ai_recommendations(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.AIRecommendation]:
    """Retrieves a list of AI recommendations with pagination."""
    return (
        db.query(models.AIRecommendation)
        .order_by(models.AIRecommendation.generated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_ai_recommendation(
    db: Session, recommendation_id: int, recommendation_update: schemas.AIRecommendationUpdate
) -> Optional[models.AIRecommendation]:
    """Updates an existing AI recommendation."""
    db_recommendation = get_ai_recommendation(db, recommendation_id)
    if db_recommendation:
        update_data = recommendation_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_recommendation, key, value)
        db.commit()
        db.refresh(db_recommendation)
    return db_recommendation


def delete_ai_recommendation(db: Session, recommendation_id: int) -> bool:
    """Deletes an AI recommendation."""
    db_recommendation = get_ai_recommendation(db, recommendation_id)
    if db_recommendation:
        db.delete(db_recommendation)
        db.commit()
        return True
    return False


# --------------------------------------------------------------------------------
# AIRagCache CRUD
# --------------------------------------------------------------------------------


def create_or_update_rag_cache(
    db: Session, cache_item: schemas.AIRagCacheCreate
) -> models.AIRagCache:
    """Creates a new RAG cache item or updates it if it already exists."""
    db_item = (
        db.query(models.AIRagCache)
        .filter_by(
            source_entity=cache_item.source_entity, source_id=cache_item.source_id
        )
        .first()
    )
    if db_item:
        # Update existing
        db_item.document_text = cache_item.document_text
        db_item.last_indexed_at = func.now()
    else:
        # Create new
        db_item = models.AIRagCache(**cache_item.model_dump())
        db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_rag_cache(db: Session, cache_id: int) -> Optional[models.AIRagCache]:
    """Retrieves a single RAG cache item by its ID."""
    return db.query(models.AIRagCache).filter(models.AIRagCache.id == cache_id).first()


def get_all_rag_cache_documents(db: Session) -> List[models.AIRagCache]:
    """Retrieves all documents from the RAG cache."""
    return db.query(models.AIRagCache).all()


def delete_rag_cache(db: Session, cache_id: int) -> bool:
    """Deletes a RAG cache item."""
    db_item = get_rag_cache(db, cache_id)
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False


# --------------------------------------------------------------------------------
# AuditLog CRUD (Create and Get only)
# --------------------------------------------------------------------------------


def create_audit_log(db: Session, log_entry: schemas.AuditLogCreate) -> models.AuditLog:
    """Creates a new audit log entry."""
    db_log = models.AuditLog(**log_entry.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_audit_logs(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.AuditLog]:
    """Retrieves a list of audit logs with pagination, most recent first."""
    return (
        db.query(models.AuditLog)
        .order_by(models.AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_audit_logs_for_entity(
    db: Session, entity_type: str, entity_id: int, skip: int = 0, limit: int = 100
) -> List[models.AuditLog]:
    """Retrieves audit logs for a specific entity."""
    return (
        db.query(models.AuditLog)
        .filter_by(entity_type=entity_type, entity_id=entity_id)
        .order_by(models.AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )