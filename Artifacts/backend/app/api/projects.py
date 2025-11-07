"""
Project management API endpoints.

This module provides RESTful endpoints for managing projects, including:
- Creating, reading, updating, and deleting projects
- Managing monthly hour overrides for projects
- Retrieving project assignments and related data

Supports user stories: US001, US007
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.db.session import get_db
from app.services.importer import ProjectImportError, import_projects_from_workbook

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=schemas.ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project.
    - **code**: Must be a unique project code.
    """
    db_project = crud.get_project_by_code(db, code=project.code, manager_id=project.manager_id)
    if db_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with code '{project.code}' already exists.",
        )
    created_project = crud.create_project(db=db, project=project)
    logger.info(f"Project created successfully with ID: {created_project.id}")
    return created_project


@router.get(
    "/",
    response_model=List[schemas.ProjectResponse],
    summary="Get a list of all projects",
)
def read_projects(
    skip: int = 0,
    limit: int = Query(default=100, lte=200),
    manager_id: Optional[int] = Query(
        None, description="Filter projects by owning manager"
    ),
    viewer_user_id: Optional[int] = Query(
        None, description="Filter projects by viewer user ID"
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of projects with pagination.
    """
    projects = crud.get_projects(
        db,
        skip=skip,
        limit=limit,
        manager_id=manager_id,
        viewer_user_id=viewer_user_id,
    )
    return projects


@router.get(
    "/{project_id}",
    response_model=schemas.ProjectWithDetailsResponse,
    summary="Get project details by ID",
)
def read_project(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single project by its ID, including all its assignments
    and monthly hour overrides.
    """
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Use specialized CRUD functions to fetch related data
    assignments = crud.get_assignments_for_project(db, project_id=project_id)
    overrides = crud.get_overrides_for_project(db, project_id=project_id)
    viewer_links = crud.get_project_viewers(db, project_id=project_id)

    # Combine data into the detailed response schema
    project_response = schemas.ProjectWithDetailsResponse.model_validate(db_project)
    project_response.assignments = assignments
    project_response.monthly_hour_overrides = overrides
    project_response.viewers = [
        schemas.UserSummaryResponse.model_validate(link.user)
        for link in viewer_links
        if link.user
    ]

    return project_response


@router.put(
    "/{project_id}",
    response_model=schemas.ProjectResponse,
    summary="Update an existing project",
)
def update_project(
    project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db)
):
    """
    Update a project's details. Only provided fields will be updated.
    """
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # If project code is being changed, ensure it's unique
    if project_update.code and project_update.code != db_project.code:
        existing_project = crud.get_project_by_code(
            db,
            code=project_update.code,
            manager_id=db_project.manager_id,
        )
        if existing_project and existing_project.id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project code '{project_update.code}' is already in use.",
            )

    updated_project = crud.update_project(
        db, project_id=project_id, project_update=project_update
    )
    logger.info(f"Project with ID {project_id} was updated.")
    return updated_project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Permanently delete a project. This will also cascade and delete related
    assignments, allocations, and overrides if the database is configured correctly.
    """
    success = crud.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    logger.info(f"Project with ID {project_id} was deleted.")
    return None


@router.post(
    "/import",
    response_model=schemas.ProjectImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import projects from an Excel workbook",
)
async def import_projects(
    manager_id: Optional[int] = Query(None, description="Assign imported projects to this manager ID"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    try:
        created_projects, skipped = import_projects_from_workbook(
            data=contents,
            db=db,
            manager_id=manager_id,
        )
    except ProjectImportError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return schemas.ProjectImportResponse(
        created_projects=[schemas.ProjectResponse.model_validate(project) for project in created_projects],
        skipped_codes=skipped,
    )


# --- Project Viewers Sub-resource ---


def _viewer_to_response(link: models.ProjectViewer) -> schemas.ProjectViewerResponse:
    if not link.user:
        raise ValueError("ProjectViewer link is missing associated user data")

    return schemas.ProjectViewerResponse(
        id=link.id,
        project_id=link.project_id,
        user_id=link.user_id,
        granted_by_id=link.granted_by_id,
        created_at=link.created_at,
        user=schemas.UserSummaryResponse.model_validate(link.user),
    )


@router.get(
    "/{project_id}/viewers",
    response_model=List[schemas.ProjectViewerResponse],
    summary="List project viewers",
)
def list_project_viewers(project_id: int, db: Session = Depends(get_db)):
    """Return all viewers who have read-only access to the specified project."""
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    links = crud.get_project_viewers(db, project_id=project_id)
    return [_viewer_to_response(link) for link in links]


@router.post(
    "/{project_id}/viewers",
    response_model=schemas.ProjectViewerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Grant project view access",
)
def create_project_viewer(
    project_id: int,
    payload: schemas.ProjectViewerCreate,
    db: Session = Depends(get_db),
):
    """Grant a user read-only access to the project."""
    if payload.project_id and payload.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload project_id does not match path parameter.",
        )

    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    db_user = crud.get_user(db, payload.user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {payload.user_id} not found",
        )

    existing = crud.get_project_viewer(
        db, project_id=project_id, user_id=payload.user_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Viewer already exists for this project.",
        )

    viewer = crud.add_project_viewer(
        db,
        project_id=project_id,
        user_id=payload.user_id,
        granted_by_id=payload.granted_by_id,
    )
    return _viewer_to_response(viewer)


@router.delete(
    "/{project_id}/viewers/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke project view access",
)
def delete_project_viewer(project_id: int, user_id: int, db: Session = Depends(get_db)):
    """Remove a viewer from the project."""
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    removed = crud.remove_project_viewer(db, project_id=project_id, user_id=user_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viewer not found for this project.",
        )

    logger.info(
        "Viewer revoked", project_id=project_id, user_id=user_id
    )
    return None


# --- Monthly Hour Overrides Sub-resource ---

@router.post(
    "/overrides",
    response_model=schemas.MonthlyHourOverrideResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a monthly hour override",
    tags=["Monthly Hour Overrides"]
)
def create_monthly_hour_override(
    override: schemas.MonthlyHourOverrideCreate, db: Session = Depends(get_db)
):
    """
    Create a new monthly hour override for a specific project.
    This sets a fixed number of working hours for a project in a given month,
    bypassing the default calculation.
    
    Supports US007: Override system-calculated full-time hours for specific months.
    """
    # Validate that the project exists
    db_project = crud.get_project(db, project_id=override.project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {override.project_id} not found.",
        )
    
    created_override = crud.create_monthly_hour_override(db=db, override=override)
    logger.info(f"Monthly hour override created with ID: {created_override.id}")
    return created_override


@router.put(
    "/overrides/{override_id}",
    response_model=schemas.MonthlyHourOverrideResponse,
    summary="Update a monthly hour override",
    tags=["Monthly Hour Overrides"]
)
def update_monthly_hour_override(
    override_id: int,
    override_update: schemas.MonthlyHourOverrideUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the `overridden_hours` for an existing monthly hour override.
    """
    updated_override = crud.update_monthly_hour_override(
        db, override_id=override_id, override_update=override_update
    )
    if updated_override is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Override not found"
        )
    logger.info(f"Monthly hour override with ID {override_id} was updated.")
    return updated_override


@router.delete(
    "/overrides/{override_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a monthly hour override",
    tags=["Monthly Hour Overrides"]
)
def delete_monthly_hour_override(override_id: int, db: Session = Depends(get_db)):
    """
    Delete a monthly hour override.
    """
    success = crud.delete_monthly_hour_override(db, override_id=override_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Override not found"
        )
    logger.info(f"Monthly hour override with ID {override_id} was deleted.")
    return None

