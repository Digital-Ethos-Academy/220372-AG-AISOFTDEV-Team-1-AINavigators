"""
Administrative API endpoints.

This module provides endpoints for:
- Managing roles and LCATs (Labor Categories) - US018
- Viewing audit logs for traceability
- Managing AI recommendations
- Debugging RAG cache

These endpoints typically require admin-level permissions.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    # Add dependency for admin-only access here, e.g.,
    # dependencies=[Depends(get_current_admin_user)],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Permission denied"},
    },
)

# ======================================================================================
# Roles Endpoints - US018
# ======================================================================================

@router.post(
    "/roles/",
    response_model=schemas.RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """
    Create a new job role (e.g., 'Software Engineer', 'Project Manager').
    
    Supports US018: Define and manage a standardized list of Roles.
    """
    created_role = crud.create_role(db=db, role=role)
    logger.info(f"Role created with ID: {created_role.id}")
    return created_role


@router.get(
    "/roles/",
    response_model=List[schemas.RoleResponse],
    summary="Get roles for a specific manager",
)
def read_roles(
    owner_id: Optional[int] = Query(None, description="Manager ID for data isolation (optional)"),
    skip: int = 0,
    limit: int = Query(default=100, lte=200),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of job roles.
    If owner_id is provided, only returns roles created by that manager.
    If owner_id is None, returns all roles (for admins/global views).
    """
    roles = crud.get_roles(
        db,
        skip=skip,
        limit=limit,
        owner_id=owner_id,
    )
    return roles


@router.get(
    "/roles/{role_id}",
    response_model=schemas.RoleResponse,
    summary="Get a role by ID",
)
def read_role(role_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single role by its ID.
    """
    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return db_role


@router.put(
    "/roles/{role_id}",
    response_model=schemas.RoleResponse,
    summary="Update a role",
)
def update_role(
    role_id: int, role_update: schemas.RoleUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing role's name or description.
    """
    updated_role = crud.update_role(db, role_id=role_id, role_update=role_update)
    if updated_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    logger.info(f"Role with ID {role_id} was updated.")
    return updated_role


@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a role",
)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """
    Delete a role. This may fail if the role is currently in use by any project assignments.
    """
    success = crud.delete_role(db, role_id=role_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found or in use")
    logger.info(f"Role with ID {role_id} was deleted.")
    return None


# ======================================================================================
# LCATs Endpoints - US018
# ======================================================================================

@router.post(
    "/lcats/",
    response_model=schemas.LCATResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new LCAT",
)
def create_lcat(lcat: schemas.LCATCreate, db: Session = Depends(get_db)):
    """
    Create a new Labor Category (e.g., 'Level 1', 'Senior').
    
    Supports US018: Define and manage a standardized list of LCATs.
    """
    created_lcat = crud.create_lcat(db=db, lcat=lcat)
    logger.info(f"LCAT created with ID: {created_lcat.id}")
    return created_lcat


@router.get(
    "/lcats/",
    response_model=List[schemas.LCATResponse],
    summary="Get LCATs for a specific manager",
)
def read_lcats(
    owner_id: Optional[int] = Query(None, description="Manager ID for data isolation (optional)"),
    skip: int = 0,
    limit: int = Query(default=100, lte=200),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of Labor Categories.
    If owner_id is provided, only returns LCATs created by that manager.
    If owner_id is None, returns all LCATs (for admins/global views).
    """
    lcats = crud.get_lcats(
        db,
        skip=skip,
        limit=limit,
        owner_id=owner_id,
    )
    return lcats


@router.get(
    "/lcats/{lcat_id}",
    response_model=schemas.LCATResponse,
    summary="Get an LCAT by ID",
)
def read_lcat(lcat_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single LCAT by its ID.
    """
    db_lcat = crud.get_lcat(db, lcat_id=lcat_id)
    if db_lcat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LCAT not found")
    return db_lcat


@router.put(
    "/lcats/{lcat_id}",
    response_model=schemas.LCATResponse,
    summary="Update an LCAT",
)
def update_lcat(
    lcat_id: int, lcat_update: schemas.LCATUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing LCAT's name or description.
    """
    updated_lcat = crud.update_lcat(db, lcat_id=lcat_id, lcat_update=lcat_update)
    if updated_lcat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LCAT not found")
    logger.info(f"LCAT with ID {lcat_id} was updated.")
    return updated_lcat


@router.delete(
    "/lcats/{lcat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an LCAT",
)
def delete_lcat(lcat_id: int, db: Session = Depends(get_db)):
    """
    Delete an LCAT. This may fail if the LCAT is in use by any project assignments.
    """
    success = crud.delete_lcat(db, lcat_id=lcat_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LCAT not found or in use")
    logger.info(f"LCAT with ID {lcat_id} was deleted.")
    return None


# ======================================================================================
# Audit Log Endpoints
# ======================================================================================

@router.get(
    "/audit-logs/",
    response_model=List[schemas.AuditLogResponse],
    summary="Get all audit logs",
)
def read_audit_logs(
    skip: int = 0,
    limit: int = Query(default=100, lte=500),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of all audit log entries, most recent first.
    This endpoint is for administrative purposes to track system activity.
    """
    logs = crud.get_audit_logs(db, skip=skip, limit=limit)
    return logs


@router.get(
    "/audit-logs/{entity_type}/{entity_id}",
    response_model=List[schemas.AuditLogResponse],
    summary="Get audit logs for a specific entity",
)
def read_audit_logs_for_entity(
    entity_type: str,
    entity_id: int,
    skip: int = 0,
    limit: int = Query(default=100, lte=500),
    db: Session = Depends(get_db),
):
    """
    Retrieve all audit log entries related to a specific entity
    (e.g., a project, a user).

    - **entity_type**: The type of the entity (e.g., 'project', 'user').
    - **entity_id**: The ID of the entity.
    """
    logs = crud.get_audit_logs_for_entity(
        db, entity_type=entity_type, entity_id=entity_id, skip=skip, limit=limit
    )
    return logs


# ======================================================================================
# AI Recommendation Endpoints
# ======================================================================================

@router.get(
    "/recommendations/",
    response_model=List[schemas.AIRecommendationResponse],
    summary="Get all AI recommendations",
)
def read_ai_recommendations(
    status_filter: Optional[schemas.RecommendationStatus] = Query(None, alias="status"),
    skip: int = 0,
    limit: int = Query(default=50, lte=200),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of AI-generated recommendations.
    Can be filtered by status.
    """
    # Note: The provided CRUD function doesn't support filtering.
    # In a real app, you would add filtering logic to the CRUD layer.
    # For now, we fetch all and filter in memory if needed, but this is inefficient.
    recommendations = crud.get_ai_recommendations(db, skip=skip, limit=limit)
    if status_filter:
        recommendations = [r for r in recommendations if r.status == status_filter]
    return recommendations


@router.get(
    "/recommendations/{recommendation_id}",
    response_model=schemas.AIRecommendationResponse,
    summary="Get a specific AI recommendation",
)
def read_ai_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single AI recommendation by its ID.
    """
    db_rec = crud.get_ai_recommendation(db, recommendation_id=recommendation_id)
    if db_rec is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found"
        )
    return db_rec


@router.put(
    "/recommendations/{recommendation_id}",
    response_model=schemas.AIRecommendationResponse,
    summary="Update the status of an AI recommendation",
)
def update_ai_recommendation_status(
    recommendation_id: int,
    update_data: schemas.AIRecommendationUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the status of a recommendation (e.g., to 'Accepted' or 'Rejected').
    This is typically done by a user acting on the recommendation.
    """
    updated_rec = crud.update_ai_recommendation(
        db, recommendation_id=recommendation_id, recommendation_update=update_data
    )
    if updated_rec is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found"
        )
    logger.info(f"AI Recommendation {recommendation_id} status updated to {update_data.status}")
    return updated_rec


# ======================================================================================
# AI RAG Cache Endpoints (for debugging/management)
# ======================================================================================

@router.get(
    "/rag-cache/",
    response_model=List[schemas.AIRagCacheResponse],
    summary="Get all RAG cache documents",
)
def read_all_rag_cache(db: Session = Depends(get_db)):
    """
    Retrieve all documents currently in the AI RAG cache.
    Useful for debugging and management.
    """
    return crud.get_all_rag_cache_documents(db)


@router.delete(
    "/rag-cache/{cache_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a RAG cache item",
)
def delete_rag_cache_item(cache_id: int, db: Session = Depends(get_db)):
    """
    Manually delete a specific item from the RAG cache.
    """
    success = crud.delete_rag_cache(db, cache_id=cache_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="RAG cache item not found"
        )
    logger.info(f"RAG cache item with ID {cache_id} was deleted.")
    return None

