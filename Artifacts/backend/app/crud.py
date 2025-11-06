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

from sqlalchemy import func
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


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Retrieves a list of users with pagination."""
    return db.query(models.User).order_by(models.User.full_name).offset(skip).limit(limit).all()


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


def create_role(db: Session, role: schemas.RoleCreate) -> models.Role:
    """Creates a new role."""
    db_role = models.Role(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_role(db: Session, role_id: int) -> Optional[models.Role]:
    """Retrieves a single role by its ID."""
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Role]:
    """Retrieves a list of roles with pagination."""
    return db.query(models.Role).order_by(models.Role.name).offset(skip).limit(limit).all()


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


def create_lcat(db: Session, lcat: schemas.LCATCreate) -> models.LCAT:
    """Creates a new LCAT."""
    db_lcat = models.LCAT(**lcat.model_dump())
    db.add(db_lcat)
    db.commit()
    db.refresh(db_lcat)
    return db_lcat


def get_lcat(db: Session, lcat_id: int) -> Optional[models.LCAT]:
    """Retrieves a single LCAT by its ID."""
    return db.query(models.LCAT).filter(models.LCAT.id == lcat_id).first()


def get_lcats(db: Session, skip: int = 0, limit: int = 100) -> List[models.LCAT]:
    """Retrieves a list of LCATs with pagination."""
    return db.query(models.LCAT).order_by(models.LCAT.name).offset(skip).limit(limit).all()


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
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def get_project_by_code(db: Session, code: str) -> Optional[models.Project]:
    """Retrieves a single project by its unique code."""
    return db.query(models.Project).filter(models.Project.code == code).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[models.Project]:
    """Retrieves a list of projects with pagination."""
    return (
        db.query(models.Project).order_by(models.Project.name).offset(skip).limit(limit).all()
    )


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


def get_all_allocations_with_details(db: Session) -> List[Dict[str, Any]]:
    """
    Retrieves all allocations with denormalized details from related entities.
    Returns a list of dictionaries with allocation data plus project, user, role, and lcat info.
    """
    results = (
        db.query(
            models.Allocation.id,
            models.Allocation.project_assignment_id,
            models.Allocation.year,
            models.Allocation.month,
            models.Allocation.allocated_hours,
            models.Project.name.label("project_name"),
            models.Project.code.label("project_code"),
            models.User.full_name.label("user_name"),
            models.User.email.label("employee_email"),
            models.Role.name.label("role_name"),
            models.LCAT.name.label("lcat_name"),
        )
        .join(models.ProjectAssignment, models.Allocation.project_assignment_id == models.ProjectAssignment.id)
        .join(models.Project, models.ProjectAssignment.project_id == models.Project.id)
        .join(models.User, models.ProjectAssignment.user_id == models.User.id)
        .join(models.Role, models.ProjectAssignment.role_id == models.Role.id)
        .join(models.LCAT, models.ProjectAssignment.lcat_id == models.LCAT.id)
        .all()
    )
    
    # Convert to list of dictionaries
    return [
        {
            "id": row.id,
            "project_assignment_id": row.project_assignment_id,
            "year": row.year,
            "month": row.month,
            "allocated_hours": row.allocated_hours,
            "project_name": row.project_name,
            "project_code": row.project_code,
            "user_name": row.user_name,
            "employee_email": row.employee_email,
            "role_name": row.role_name,
            "lcat_name": row.lcat_name,
        }
        for row in results
    ]


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