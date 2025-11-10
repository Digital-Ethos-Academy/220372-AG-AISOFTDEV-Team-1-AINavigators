"""AI-powered features API endpoints for StaffAlloc."""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.services.ai import (
    GeminiConfigurationError,
    GeminiInvocationError,
    generate_chat_response,
    generate_forecast_insights,
    generate_workload_balance_suggestions,
    reindex_rag_cache,
    scan_allocation_conflicts,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
    responses={404: {"description": "Not found"}},
)


class ChatQueryRequest(BaseModel):
    query: str = Field(..., description="The user's question", min_length=3)
    manager_id: Optional[int] = Field(None, description="Manager ID for data isolation (optional)")
    context_limit: int = Field(
        5,
        description="Number of context documents to retrieve",
        ge=1,
        le=20,
    )


class ChatQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str] = Field(default_factory=list)


class ConflictProjectBreakdown(BaseModel):
    project_id: Optional[int]
    project_name: str
    hours: int


class ConflictDetail(BaseModel):
    user_id: int
    employee: str
    month: str
    total_hours: int
    fte: float
    projects: List[ConflictProjectBreakdown] = Field(default_factory=list)


class ConflictsResponse(BaseModel):
    conflicts: List[ConflictDetail] = Field(default_factory=list)
    message: str


class ForecastPrediction(BaseModel):
    month: str
    projected_capacity_hours: int
    projected_allocated_hours: int
    surplus_hours: int
    risk: str


class ForecastResponse(BaseModel):
    forecast_period_months: int
    predictions: List[ForecastPrediction] = Field(default_factory=list)
    message: str


class ProjectInfo(BaseModel):
    project_id: int
    project_name: str
    assignment_id: int


class BalanceSuggestion(BaseModel):
    action: str
    from_employee: Optional[str] = None
    from_employee_id: Optional[int] = None
    from_employee_current_fte: Optional[float] = None
    from_employee_current_hours: Optional[int] = None
    from_employee_projects: List[ProjectInfo] = Field(default_factory=list)
    to_employee: Optional[str] = None
    to_employee_id: Optional[int] = None
    to_employee_current_fte: Optional[float] = None
    to_employee_current_hours: Optional[int] = None
    to_employee_projects: List[ProjectInfo] = Field(default_factory=list)
    recommended_hours: int
    project_name: Optional[str] = None
    project_id: Optional[int] = None
    reasoning: Optional[str] = None


class BalanceSuggestionsResponse(BaseModel):
    suggestions: List[BalanceSuggestion] = Field(default_factory=list)
    message: str


class ReindexResponse(BaseModel):
    status: str
    message: str


def _raise_from_ai_error(exc: Exception) -> None:
    if isinstance(exc, GeminiConfigurationError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if isinstance(exc, GeminiInvocationError):
        logger.exception("Gemini invocation failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable. Try again shortly.",
        ) from exc
    raise exc


@router.post(
    "/chat",
    response_model=ChatQueryResponse,
    summary="Query the AI assistant using RAG",
)
def chat_query(request: ChatQueryRequest, db: Session = Depends(get_db)) -> ChatQueryResponse:
    logger.info("AI chat query received", extra={"query": request.query, "manager_id": request.manager_id})
    try:
        answer, sources = generate_chat_response(
            db, 
            query=request.query, 
            context_limit=request.context_limit,
            manager_id=request.manager_id
        )
    except (GeminiConfigurationError, GeminiInvocationError) as exc:  # pragma: no cover - error paths
        _raise_from_ai_error(exc)
    return ChatQueryResponse(query=request.query, answer=answer, sources=sources)


@router.get(
    "/conflicts",
    response_model=ConflictsResponse,
    summary="Detect resource allocation conflicts",
)
def detect_conflicts(
    manager_id: Optional[int] = Query(None, description="Manager ID for data isolation"),
    db: Session = Depends(get_db)
) -> ConflictsResponse:
    try:
        conflicts, message = scan_allocation_conflicts(db, manager_id=manager_id)
    except (GeminiConfigurationError, GeminiInvocationError) as exc:  # pragma: no cover
        _raise_from_ai_error(exc)

    conflict_models = [
        ConflictDetail(
            user_id=conflict["user_id"],
            employee=conflict["employee"],
            month=conflict["month"],
            total_hours=conflict["total_hours"],
            fte=conflict["fte"],
            projects=[
                ConflictProjectBreakdown(
                    project_id=item.get("project_id"),
                    project_name=item.get("project_name") or "Unknown",
                    hours=item.get("hours", 0),
                )
                for item in conflict.get("projects", [])
            ],
        )
        for conflict in conflicts
    ]
    return ConflictsResponse(conflicts=conflict_models, message=message)


@router.get(
    "/forecast",
    response_model=ForecastResponse,
    summary="Get predictive resource forecasts",
)
def get_forecast(
    months_ahead: int = 3,
    manager_id: Optional[int] = Query(None, description="Manager ID for data isolation"),
    db: Session = Depends(get_db)
) -> ForecastResponse:
    try:
        predictions, message = generate_forecast_insights(
            db, months_ahead=months_ahead, manager_id=manager_id
        )
    except (GeminiConfigurationError, GeminiInvocationError) as exc:  # pragma: no cover
        _raise_from_ai_error(exc)

    prediction_models = [
        ForecastPrediction(**prediction) for prediction in predictions
    ]
    return ForecastResponse(
        forecast_period_months=months_ahead,
        predictions=prediction_models,
        message=message,
    )


@router.get(
    "/balance-suggestions",
    response_model=BalanceSuggestionsResponse,
    summary="Get workload balance suggestions",
)
def get_balance_suggestions(
    project_id: Optional[int] = None,
    manager_id: Optional[int] = Query(None, description="Manager ID for data isolation"),
    db: Session = Depends(get_db),
) -> BalanceSuggestionsResponse:
    try:
        suggestions, message = generate_workload_balance_suggestions(
            db, project_id=project_id, manager_id=manager_id
        )
    except (GeminiConfigurationError, GeminiInvocationError) as exc:  # pragma: no cover
        _raise_from_ai_error(exc)

    suggestion_models = [
        BalanceSuggestion(**suggestion) for suggestion in suggestions
    ]
    return BalanceSuggestionsResponse(suggestions=suggestion_models, message=message)


@router.post(
    "/reindex",
    response_model=ReindexResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger RAG cache reindexing",
)
def trigger_reindex(db: Session = Depends(get_db)) -> ReindexResponse:
    documents_created = reindex_rag_cache(db, manager_id=None)
    message = f"RAG cache refreshed with {documents_created} documents."
    return ReindexResponse(status="accepted", message=message)

