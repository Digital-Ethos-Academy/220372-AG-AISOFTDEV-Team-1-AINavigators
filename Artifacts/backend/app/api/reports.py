"""
Reporting and dashboard API endpoints.

This module provides endpoints for:
- Portfolio-level dashboards - US011
- Employee timeline views - US012
- Project-specific dashboards - US019
- Excel export functionality - US016

These endpoints aggregate data across projects and employees to provide
high-level insights for directors and resource managers.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    responses={404: {"description": "Not found"}},
)


# ======================================================================================
# Response Models for Dashboards
# ======================================================================================

class PortfolioDashboardResponse(BaseModel):
    """Response model for portfolio-level dashboard data."""
    total_projects: int
    total_employees: int
    overall_utilization_pct: float = Field(description="Overall FTE utilization percentage")
    fte_by_role: dict = Field(default_factory=dict, description="FTE breakdown by role")
    over_allocated_employees: List[dict] = Field(default_factory=list)
    bench_employees: List[dict] = Field(default_factory=list, description="Employees with <25% FTE")


class ProjectDashboardResponse(BaseModel):
    """Response model for project-specific dashboard data."""
    project_id: int
    project_name: str
    total_funded_hours: int
    total_allocated_hours: int
    utilization_pct: float
    burn_down_data: List[dict] = Field(default_factory=list)


class EmployeeTimelineResponse(BaseModel):
    """Response model for an employee's timeline across all projects."""
    employee_id: int
    employee_name: str
    timeline: List[dict] = Field(
        default_factory=list,
        description="Monthly breakdown of allocations across all projects"
    )


# ======================================================================================
# Portfolio Dashboard - US011
# ======================================================================================

@router.get(
    "/portfolio-dashboard",
    response_model=PortfolioDashboardResponse,
    summary="Get organization-wide portfolio dashboard",
)
def get_portfolio_dashboard(db: Session = Depends(get_db)):
    """
    Retrieve an organization-wide dashboard with key metrics.
    
    Provides:
    - Total FTE by role
    - List of over-allocated employees (>100% FTE)
    - List of employees on the bench (<25% FTE)
    - Overall utilization rates
    
    Supports US011: Portfolio-level roll-up dashboard for Directors.
    
    NOTE: This is a basic implementation. Enhanced analytics can be added.
    """
    logger.info("Generating portfolio dashboard")
    
    # Get basic counts
    all_projects = crud.get_projects(db, skip=0, limit=1000)
    all_users = crud.get_users(db, skip=0, limit=1000)
    
    # Placeholder for more complex calculations
    # TODO: Implement actual aggregation logic:
    # 1. Calculate FTE by role across all projects
    # 2. Identify over-allocated employees
    # 3. Identify bench employees
    # 4. Calculate overall utilization percentage
    
    return PortfolioDashboardResponse(
        total_projects=len(all_projects),
        total_employees=len(all_users),
        overall_utilization_pct=0.0,
        fte_by_role={},
        over_allocated_employees=[],
        bench_employees=[]
    )


# ======================================================================================
# Project Dashboard - US019
# ======================================================================================

@router.get(
    "/project-dashboard/{project_id}",
    response_model=ProjectDashboardResponse,
    summary="Get project-specific dashboard",
)
def get_project_dashboard(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a dashboard for a specific project showing staffing health.
    
    Provides:
    - Funded vs. allocated hours summary
    - FTE burn-down chart data
    - Budget utilization percentage
    
    Supports US019: Project-specific dashboard for PMs.
    """
    # Validate project exists
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    # Get all assignments for the project
    assignments = crud.get_assignments_for_project(db, project_id=project_id)
    
    # Calculate totals
    total_funded = sum(a.funded_hours for a in assignments)
    total_allocated = 0
    
    for assignment in assignments:
        allocations = crud.get_allocations_for_assignment(db, assignment_id=assignment.id)
        total_allocated += sum(alloc.allocated_hours for alloc in allocations)
    
    utilization = (total_allocated / total_funded * 100) if total_funded > 0 else 0
    
    logger.info(f"Generating project dashboard for project {project_id}")
    
    # TODO: Generate burn-down chart data
    # This would show planned vs actual FTE over the project timeline
    
    return ProjectDashboardResponse(
        project_id=project_id,
        project_name=db_project.name,
        total_funded_hours=total_funded,
        total_allocated_hours=total_allocated,
        utilization_pct=round(utilization, 2),
        burn_down_data=[]
    )


# ======================================================================================
# Employee Timeline - US012
# ======================================================================================

@router.get(
    "/employee-timeline/{employee_id}",
    response_model=EmployeeTimelineResponse,
    summary="Get an employee's timeline across all projects",
)
def get_employee_timeline(
    employee_id: int,
    start_year: Optional[int] = Query(None, description="Start year for timeline"),
    start_month: Optional[int] = Query(None, ge=1, le=12, description="Start month for timeline"),
    end_year: Optional[int] = Query(None, description="End year for timeline"),
    end_month: Optional[int] = Query(None, ge=1, le=12, description="End month for timeline"),
    db: Session = Depends(get_db)
):
    """
    Get a single employee's timeline showing all project commitments.
    
    This provides a unified view of where an employee is allocated across
    all their projects, making it easy to identify availability and conflicts.
    
    Supports US012: Employee timeline view for resource optimization.
    """
    # Validate employee exists
    db_user = crud.get_user(db, employee_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    # Get employee's allocation summary
    summary = crud.get_user_allocation_summary(db, user_id=employee_id)
    
    # Filter by date range if provided
    if start_year and start_month:
        summary = [
            s for s in summary 
            if (s['year'] > start_year) or (s['year'] == start_year and s['month'] >= start_month)
        ]
    
    if end_year and end_month:
        summary = [
            s for s in summary 
            if (s['year'] < end_year) or (s['year'] == end_year and s['month'] <= end_month)
        ]
    
    logger.info(f"Generating employee timeline for user {employee_id}")
    
    # TODO: Enhance to show project-by-project breakdown for each month
    # Currently just shows total hours per month across all projects
    
    return EmployeeTimelineResponse(
        employee_id=employee_id,
        employee_name=db_user.full_name,
        timeline=summary
    )


# ======================================================================================
# Excel Export - US016
# ======================================================================================

@router.get(
    "/export/portfolio",
    summary="Export portfolio data to Excel",
    responses={
        200: {
            "content": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}},
            "description": "Excel file download",
        }
    },
)
def export_portfolio_to_excel(db: Session = Depends(get_db)):
    """
    Export the portfolio roll-up view to an Excel file.
    
    The Excel file will contain:
    - Projects as rows
    - Months as columns
    - FTE data in cells
    - Summary statistics
    
    Supports US016: Export data for executive reporting and custom analysis.
    
    NOTE: This is a placeholder. Full implementation will use openpyxl or xlsxwriter
    to generate the Excel file.
    """
    logger.info("Exporting portfolio data to Excel (placeholder)")
    
    # TODO: Implement actual Excel generation:
    # 1. Query all projects and allocations
    # 2. Aggregate data by project and month
    # 3. Use openpyxl to create workbook
    # 4. Format cells, add headers, apply styling
    # 5. Return as streaming response
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Excel export functionality is not yet implemented."
    )


@router.get(
    "/export/project/{project_id}",
    summary="Export project data to Excel",
    responses={
        200: {
            "content": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}},
            "description": "Excel file download",
        }
    },
)
def export_project_to_excel(project_id: int, db: Session = Depends(get_db)):
    """
    Export a specific project's allocation data to an Excel file.
    
    Supports US016: Export project data for sharing with stakeholders.
    """
    # Validate project exists
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    logger.info(f"Exporting project {project_id} data to Excel (placeholder)")
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Excel export functionality is not yet implemented."
    )


# ======================================================================================
# Utilization Reports
# ======================================================================================

@router.get(
    "/utilization-by-role",
    summary="Get utilization statistics by role",
)
def get_utilization_by_role(
    year: int = Query(..., description="Year for the report"),
    month: int = Query(..., ge=1, le=12, description="Month for the report"),
    db: Session = Depends(get_db)
):
    """
    Get utilization statistics grouped by role for a specific month.
    
    Useful for identifying which roles are over/under-utilized.
    Supports US011 and US020 (workload balancing).
    """
    logger.info(f"Generating utilization report by role for {year}-{month:02d}")
    
    # TODO: Implement actual calculation:
    # 1. Query all allocations for the specified month
    # 2. Group by role (via project_assignments)
    # 3. Calculate total hours and average FTE by role
    # 4. Compare against full-time equivalent for the month
    
    return {
        "year": year,
        "month": month,
        "utilization_by_role": [],
        "message": "Utilization reporting is not yet fully implemented."
    }

