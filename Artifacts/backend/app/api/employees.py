"""
Employee/User management API endpoints.

This module provides RESTful endpoints for managing users/employees, including:
- Creating, reading, updating, and deleting users
- Retrieving user assignments across projects
- Managing user authentication and profiles

Supports the employee management aspects of the PRD.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core import security
from app.db.session import get_db
from app.models import SystemRole

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee/user",
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user/employee in the system.

    - **email**: Must be a unique email address.
    - **password**: Must be at least 8 characters long.
    - **system_role**: Defines the user's permissions (Admin, Director, PM, Employee).
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"Attempted to create user with existing email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if user.system_role == SystemRole.EMPLOYEE and not user.manager_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee accounts must specify a manager_id.",
        )

    # Hash the password before storing
    hashed_password = security.get_password_hash(user.password)

    created_user = crud.create_user(db=db, user=user, password_hash=hashed_password)
    logger.info(f"User created successfully with ID: {created_user.id}")
    return created_user


@router.get(
    "/",
    response_model=List[schemas.UserResponse],
    summary="Get a list of employees for a specific manager",
)
def read_users(
    manager_id: Optional[int] = Query(None, description="Manager ID for data isolation (optional)"),
    skip: int = 0,
    limit: int = Query(default=100, lte=200),
    system_role: Optional[SystemRole] = Query(
        None, description="Filter by system role"
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of users/employees.
    - **manager_id**: Optional manager ID for filtering. If provided, only returns employees owned by that manager. If None, returns all employees (for admins/global views).
    - **skip**: Number of records to skip.
    - **limit**: Maximum number of records to return (max 200).
    - **system_role**: Optional filter by system role.
    """
    users = crud.get_users(
        db,
        skip=skip,
        limit=limit,
        manager_id=manager_id,
        system_role=system_role,
    )
    return users


@router.get(
    "/{user_id}",
    response_model=schemas.UserWithAssignmentsResponse,
    summary="Get a specific employee by ID with their assignments",
)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single user by their ID, including all their project assignments.

    This supports US012: View a single employee's timeline across all projects.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Use the specialized CRUD function to get assignments
    assignments = crud.get_assignments_for_user(db, user_id=user_id)

    # Combine the data into the detailed response schema
    user_response = schemas.UserWithAssignmentsResponse.model_validate(db_user)
    user_response.assignments = assignments

    return user_response


@router.put(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="Update an existing employee",
)
def update_user(
    user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)
):
    """
    Update a user's details.
    - Only the fields provided in the request body will be updated.
    - To change a password, provide a new `password` field.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # If email is being changed, ensure it's not already taken
    if user_update.email and user_update.email != db_user.email:
        existing_user = crud.get_user_by_email(db, email=user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use by another account.",
            )

    update_data = user_update.model_dump(exclude_unset=True)

    # Handle password update separately
    if "password" in update_data and update_data["password"]:
        hashed_password = security.get_password_hash(update_data["password"])
        update_data["password_hash"] = hashed_password
        del update_data["password"]

    # Create the update schema for CRUD
    final_update_schema = schemas.UserUpdate(**update_data)

    updated_user = crud.update_user(db, user_id=user_id, user_update=final_update_schema)
    logger.info(f"User with ID {user_id} was updated.")
    return updated_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an employee",
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Permanently delete a user from the system. This action is irreversible.
    """
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    logger.info(f"User with ID {user_id} was deleted.")
    return None

