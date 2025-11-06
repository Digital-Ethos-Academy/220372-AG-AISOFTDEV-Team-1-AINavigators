"""
Allocation management API endpoints.

This module provides RESTful endpoints for managing:
- Project assignments (linking employees to projects with roles and funded hours)
- Hour allocations (monthly hour allocations for each assignment)

This is the core of the allocation grid functionality, supporting user stories:
- US002: Add employees to projects
- US003: Allocate hours in the grid
- US004: Automatic FTE calculation
- US005: Over-budget warnings
- US006: Cross-project over-allocation detection
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/allocations",
    tags=["Allocations"],
    responses={404: {"description": "Not found"}},
)


# ======================================================================================
# Project Assignment Endpoints
# ======================================================================================

@router.post(
    "/assignments",
    response_model=schemas.ProjectAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project assignment",
)
def create_project_assignment(
    assignment: schemas.ProjectAssignmentCreate, db: Session = Depends(get_db)
):
    """
    Assign a user to a project with a specific role, LCAT, and funded hours.
    A user can only be assigned to a project once.
    
    Supports US002: Add an employee to a project.
    """
    # Check for existing assignment for this user on this project
    existing_assignment = crud.get_assignment_by_user_and_project(
        db, user_id=assignment.user_id, project_id=assignment.project_id
    )
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user is already assigned to this project.",
        )
    
    # Validate that related entities exist
    if not crud.get_project(db, assignment.project_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Project with ID {assignment.project_id} not found")
    if not crud.get_user(db, assignment.user_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"User with ID {assignment.user_id} not found")
    if not crud.get_role(db, assignment.role_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Role with ID {assignment.role_id} not found")
    if not crud.get_lcat(db, assignment.lcat_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"LCAT with ID {assignment.lcat_id} not found")

    created_assignment = crud.create_project_assignment(db=db, assignment=assignment)
    logger.info(f"Project assignment created with ID: {created_assignment.id}")
    return created_assignment


@router.get(
    "/assignments/{assignment_id}",
    response_model=schemas.ProjectAssignmentWithAllocationsResponse,
    summary="Get assignment details by ID",
)
def read_project_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single project assignment by its ID, including all its
    monthly hour allocations.
    """
    db_assignment = crud.get_project_assignment(db, assignment_id=assignment_id)
    if db_assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project assignment not found"
        )

    allocations = crud.get_allocations_for_assignment(db, assignment_id=assignment_id)

    assignment_response = schemas.ProjectAssignmentWithAllocationsResponse.model_validate(db_assignment)
    assignment_response.allocations = allocations
    
    return assignment_response


@router.put(
    "/assignments/{assignment_id}",
    response_model=schemas.ProjectAssignmentResponse,
    summary="Update a project assignment",
)
def update_project_assignment(
    assignment_id: int,
    assignment_update: schemas.ProjectAssignmentUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing project assignment.
    Note: `project_id` and `user_id` cannot be changed.
    You can update role, LCAT, and funded hours.
    """
    updated_assignment = crud.update_project_assignment(
        db, assignment_id=assignment_id, assignment_update=assignment_update
    )
    if updated_assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project assignment not found"
        )
    logger.info(f"Project assignment with ID {assignment_id} was updated.")
    return updated_assignment


@router.delete(
    "/assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project assignment",
)
def delete_project_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """
    Delete a project assignment. This will also delete all associated allocations.
    """
    success = crud.delete_project_assignment(db, assignment_id=assignment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project assignment not found"
        )
    logger.info(f"Project assignment with ID {assignment_id} was deleted.")
    return None


# ======================================================================================
# Allocation (Monthly Hours) Endpoints
# ======================================================================================

@router.get(
    "/",
    response_model=List[schemas.AllocationWithDetailsResponse],
    summary="Get all allocations",
)
def list_all_allocations(db: Session = Depends(get_db)):
    """
    Retrieve all allocations with related details (project, user, role, lcat).
    
    This endpoint provides a comprehensive view of all allocations across
    all projects and employees, useful for the allocations overview page.
    """
    allocations = crud.get_all_allocations_with_details(db)
    return allocations


@router.post(
    "/",
    response_model=schemas.AllocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new allocation",
)
def create_allocation(
    allocation: schemas.AllocationCreate, db: Session = Depends(get_db)
):
    """
    Create a new monthly hour allocation for a project assignment.
    
    Supports US003: Allocate hours to an employee for a specific month.
    
    This endpoint will be used by the allocation grid to create new hour entries.
    The frontend should also implement validations for:
    - US005: Budget overrun detection (remaining hours)
    - US006: Cross-project over-allocation (>100% FTE)
    """
    # Validate that the parent assignment exists
    if not crud.get_project_assignment(db, allocation.project_assignment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID {allocation.project_assignment_id} not found.",
        )
    
    created_allocation = crud.create_allocation(db=db, allocation=allocation)
    logger.info(f"Allocation created with ID: {created_allocation.id}")
    return created_allocation


@router.get(
    "/{allocation_id}",
    response_model=schemas.AllocationResponse,
    summary="Get a specific allocation",
)
def read_allocation(allocation_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single allocation by its ID.
    """
    db_allocation = crud.get_allocation(db, allocation_id=allocation_id)
    if db_allocation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Allocation not found"
        )
    return db_allocation


@router.put(
    "/{allocation_id}",
    response_model=schemas.AllocationResponse,
    summary="Update an allocation",
)
def update_allocation(
    allocation_id: int,
    allocation_update: schemas.AllocationUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the `allocated_hours` for an existing allocation.
    
    This is the primary endpoint for the allocation grid's cell updates.
    Supports US003: Modify hours in the grid.
    """
    updated_allocation = crud.update_allocation(
        db, allocation_id=allocation_id, allocation_update=allocation_update
    )
    if updated_allocation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Allocation not found"
        )
    logger.info(f"Allocation with ID {allocation_id} was updated.")
    return updated_allocation


@router.delete(
    "/{allocation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an allocation",
)
def delete_allocation(allocation_id: int, db: Session = Depends(get_db)):
    """
    Delete a monthly allocation.
    """
    success = crud.delete_allocation(db, allocation_id=allocation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Allocation not found"
        )
    logger.info(f"Allocation with ID {allocation_id} was deleted.")
    return None


# ======================================================================================
# Helper Endpoints for Validation and Reporting
# ======================================================================================

@router.get(
    "/users/{user_id}/summary",
    summary="Get user's monthly allocation summary",
)
def get_user_allocation_summary(user_id: int, db: Session = Depends(get_db)):
    """
    Get a summary of a user's total allocated hours per month across all projects.
    
    This supports US006: Cross-project over-allocation detection.
    Returns data like: [{'year': 2025, 'month': 1, 'total_hours': 160}, ...]
    """
    # Validate user exists
    if not crud.get_user(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    summary = crud.get_user_allocation_summary(db, user_id=user_id)
    return summary

