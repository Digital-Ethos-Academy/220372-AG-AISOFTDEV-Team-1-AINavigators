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
from collections import defaultdict
from datetime import date
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import crud, models
from app.db.session import get_db
from app.utils.reporting import (
    build_burn_down_series,
    default_project_end,
    iter_months,
    standard_month_hours,
)
from app.services.exporter import portfolio_workbook, project_workbook

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    responses={404: {"description": "Not found"}},
)


# ======================================================================================
# Response Models for Dashboards
# ======================================================================================

class ProjectAllocationBreakdown(BaseModel):
    project_id: int
    project_name: str
    allocated_hours: int


class EmployeeCapacitySummary(BaseModel):
    user_id: int
    full_name: str
    total_hours: int
    fte_percentage: float
    role: Optional[str] = None
    projects: List[ProjectAllocationBreakdown] = Field(default_factory=list)
    available_hours: Optional[int] = None


class PortfolioDashboardResponse(BaseModel):
    """Response model for portfolio-level dashboard data."""
    total_projects: int
    total_employees: int
    overall_utilization_pct: float = Field(description="Overall FTE utilization percentage")
    fte_by_role: dict = Field(default_factory=dict, description="FTE breakdown by role")
    over_allocated_employees: List[EmployeeCapacitySummary] = Field(default_factory=list)
    bench_employees: List[EmployeeCapacitySummary] = Field(
        default_factory=list, description="Employees with <25% FTE"
    )


class BurnDownDataPoint(BaseModel):
    label: str
    planned_hours: float
    actual_hours: float
    planned_burn_hours: float
    actual_burn_hours: float
    capacity_hours: int
    sprint_index: int
    date: str


class ProjectDashboardResponse(BaseModel):
    """Response model for project-specific dashboard data."""
    project_id: int
    project_name: str
    total_funded_hours: int
    total_allocated_hours: int
    utilization_pct: float
    burn_down_data: List[BurnDownDataPoint] = Field(default_factory=list)


class EmployeeTimelineMonth(BaseModel):
    year: int
    month: int
    total_hours: int
    standard_hours: int
    fte_percentage: float
    available_hours: int
    allocations: List[ProjectAllocationBreakdown] = Field(default_factory=list)


class EmployeeTimelineResponse(BaseModel):
    """Response model for an employee's timeline across all projects."""
    employee_id: int
    employee_name: str
    timeline: List[EmployeeTimelineMonth] = Field(
        default_factory=list,
        description="Monthly breakdown of allocations across all projects",
    )


# ======================================================================================
# Portfolio Dashboard - US011
# ======================================================================================

@router.get(
    "/portfolio-dashboard",
    response_model=PortfolioDashboardResponse,
    summary="Get manager-specific portfolio dashboard",
)
def get_portfolio_dashboard(
    manager_id: Optional[int] = Query(None, description="Manager ID for data isolation (optional)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a manager-specific dashboard with key metrics.
    
    Provides:
    - Total FTE by role
    - List of over-allocated employees (>100% FTE)
    - List of employees on the bench (<25% FTE)
    - Overall utilization rates
    
    Manager-specific isolation enforced: only shows data for this manager's projects and employees.
    
    Supports US011: Portfolio-level roll-up dashboard for PMs.
    
    NOTE: This is a basic implementation. Enhanced analytics can be added.
    """
    logger.info(f"Generating portfolio dashboard for manager {manager_id}")

    today = date.today()
    standard_hours_this_month = max(standard_month_hours(today.year, today.month), 1)

    # Filter by manager_id for data isolation
    total_projects = (
        db.query(func.count(models.Project.id))
        .filter(models.Project.manager_id == manager_id)
        .scalar() or 0
    )
    total_employees = (
        db.query(func.count(models.User.id))
        .filter(models.User.system_role == models.SystemRole.EMPLOYEE)
        .filter(models.User.manager_id == manager_id)
        .scalar()
        or 0
    )

    role_capacity = crud.get_role_capacity_summary(db, manager_id=manager_id)
    total_funded_hours = sum(int(entry.get("funded_hours") or 0) for entry in role_capacity)
    total_allocated_hours = sum(int(entry.get("allocated_hours") or 0) for entry in role_capacity)

    overall_utilization_pct = (
        (total_allocated_hours / total_funded_hours) * 100 if total_funded_hours else 0.0
    )

    fte_by_role: Dict[str, float] = {}
    for entry in role_capacity:
        role_name = entry.get("role_name")
        if not role_name:
            continue
        funded_hours = float(entry.get("funded_hours") or 0.0)
        allocated_hours = float(entry.get("allocated_hours") or 0.0)
        if funded_hours > 0:
            fte_by_role[role_name] = round((allocated_hours / funded_hours) * 100, 2)
        else:
            fte_by_role[role_name] = 0.0

    monthly_user_totals = crud.get_monthly_user_allocation_totals(db, manager_id=manager_id)
    current_hours_by_user = {
        row["user_id"]: int(row.get("total_hours") or 0)
        for row in monthly_user_totals
        if row["year"] == today.year and row["month"] == today.month
    }

    project_allocations = crud.get_monthly_user_project_allocations(db, manager_id=manager_id)
    current_project_breakdown: Dict[int, List[ProjectAllocationBreakdown]] = defaultdict(list)
    for row in project_allocations:
        if row["year"] == today.year and row["month"] == today.month:
            current_project_breakdown[row["user_id"]].append(
                ProjectAllocationBreakdown(
                    project_id=row["project_id"],
                    project_name=row["project_name"],
                    allocated_hours=int(row.get("allocated_hours") or 0),
                )
            )

    for breakdown in current_project_breakdown.values():
        breakdown.sort(key=lambda item: item.allocated_hours, reverse=True)

    primary_role_entries = crud.get_user_role_funding_totals(db, manager_id=manager_id)
    primary_role_lookup: Dict[int, str] = {}
    role_hours_tracker: Dict[int, float] = {}
    for entry in primary_role_entries:
        user_id = entry["user_id"]
        funded = float(entry.get("funded_hours") or 0.0)
        if funded <= 0:
            continue
        if user_id not in role_hours_tracker or funded > role_hours_tracker[user_id]:
            role_hours_tracker[user_id] = funded
            role_name = entry.get("role_name")
            if role_name:
                primary_role_lookup[user_id] = role_name

    employees = crud.get_users(
        db,
        skip=0,
        limit=2000,
        manager_id=manager_id,
        system_role=models.SystemRole.EMPLOYEE,
    )

    over_allocated: List[EmployeeCapacitySummary] = []
    bench: List[EmployeeCapacitySummary] = []

    for employee in employees:
        current_hours = current_hours_by_user.get(employee.id, 0)
        current_fte = (
            current_hours / standard_hours_this_month if standard_hours_this_month else 0.0
        )
        summary_data = {
            "user_id": employee.id,
            "full_name": employee.full_name,
            "total_hours": int(current_hours),
            "fte_percentage": round(current_fte * 100, 2),
            "role": primary_role_lookup.get(employee.id),
            "projects": current_project_breakdown.get(employee.id, []),
        }

        if current_fte > 1.0:
            over_allocated.append(EmployeeCapacitySummary(**summary_data))
        elif current_fte <= 0.25:
            summary_data["available_hours"] = max(standard_hours_this_month - current_hours, 0)
            bench.append(EmployeeCapacitySummary(**summary_data))

    over_allocated.sort(key=lambda item: item.fte_percentage, reverse=True)
    bench.sort(key=lambda item: item.available_hours or 0, reverse=True)

    return PortfolioDashboardResponse(
        total_projects=total_projects,
        total_employees=total_employees,
        overall_utilization_pct=round(overall_utilization_pct, 2),
        fte_by_role={role: round(value, 2) for role, value in fte_by_role.items()},
        over_allocated_employees=over_allocated,
        bench_employees=bench,
    )


# ======================================================================================
# Manager Allocations Rollup - Dashboard Grid
# ======================================================================================

class EmployeeMonthlyTotal(BaseModel):
    """Monthly allocation total for an employee."""
    year: int
    month: int
    total_hours: int
    fte_percentage: float

class EmployeeAllocationRollup(BaseModel):
    """Rollup of all allocations for a single employee."""
    employee_id: int
    employee_name: str
    total_funded_hours: int
    monthly_totals: List[EmployeeMonthlyTotal] = Field(default_factory=list)

class ManagerAllocationsResponse(BaseModel):
    """Response for manager allocations rollup grid."""
    employees: List[EmployeeAllocationRollup] = Field(default_factory=list)
    date_range: Dict[str, int] = Field(default_factory=dict)

@router.get(
    "/manager-allocations",
    response_model=ManagerAllocationsResponse,
    summary="Get manager allocation rollup for dashboard grid",
)
def get_manager_allocations(
    manager_id: Optional[int] = Query(None, description="Manager ID for data isolation (optional)"),
    start_year: int = Query(..., ge=2020, le=2050, description="Start year for date range"),
    start_month: int = Query(..., ge=1, le=12, description="Start month for date range"),
    end_year: int = Query(..., ge=2020, le=2050, description="End year for date range"),
    end_month: int = Query(..., ge=1, le=12, description="End month for date range"),
    db: Session = Depends(get_db)
):
    """
    Retrieve allocation rollup for all employees managed by a specific manager.
    
    Returns:
    - List of employees with their total funded hours
    - Monthly allocation totals for each employee across all projects
    - Date range info
    
    This endpoint powers the dashboard allocation rollup grid.
    """
    logger.info(f"Generating manager allocations rollup for manager {manager_id}")
    
    # Get all employees for this manager
    employees = crud.get_users(
        db,
        skip=0,
        limit=2000,
        manager_id=manager_id,
        system_role=models.SystemRole.EMPLOYEE,
    )
    
    # Get monthly totals for this manager's projects
    monthly_totals = crud.get_monthly_user_allocation_totals(db, manager_id=manager_id)
    
    # Get funded hours per employee across all projects
    funded_hours_query = (
        db.query(
            models.ProjectAssignment.user_id.label("user_id"),
            func.sum(models.ProjectAssignment.funded_hours).label("total_funded"),
        )
        .join(models.Project, models.Project.id == models.ProjectAssignment.project_id)
        .filter(models.Project.manager_id == manager_id)
        .group_by(models.ProjectAssignment.user_id)
        .all()
    )
    
    funded_lookup = {row.user_id: int(row.total_funded or 0) for row in funded_hours_query}
    
    # Build response
    employee_rollups = []
    for employee in employees:
        # Get monthly totals for this employee within date range
        employee_monthlies = []
        for month_data in monthly_totals:
            if month_data["user_id"] != employee.id:
                continue
            year = month_data["year"]
            month = month_data["month"]
            
            # Check if within date range
            if (year < start_year or (year == start_year and month < start_month)):
                continue
            if (year > end_year or (year == end_year and month > end_month)):
                continue
            
            total_hours = int(month_data.get("total_hours") or 0)
            standard_hours = max(standard_month_hours(year, month), 1)
            fte_pct = (total_hours / standard_hours) * 100
            
            employee_monthlies.append(EmployeeMonthlyTotal(
                year=year,
                month=month,
                total_hours=total_hours,
                fte_percentage=round(fte_pct, 2)
            ))
        
        # Sort by year/month
        employee_monthlies.sort(key=lambda x: (x.year, x.month))
        
        employee_rollups.append(EmployeeAllocationRollup(
            employee_id=employee.id,
            employee_name=employee.full_name,
            total_funded_hours=funded_lookup.get(employee.id, 0),
            monthly_totals=employee_monthlies
        ))
    
    # Sort by employee name
    employee_rollups.sort(key=lambda x: x.employee_name)
    
    return ManagerAllocationsResponse(
        employees=employee_rollups,
        date_range={
            "start_year": start_year,
            "start_month": start_month,
            "end_year": end_year,
            "end_month": end_month
        }
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
    
    totals = crud.get_project_funded_and_allocated_totals(db, project_id=project_id)
    total_funded = int(totals.get("funded_hours", 0))
    total_allocated = int(totals.get("allocated_hours", 0))
    utilization = (total_allocated / total_funded * 100) if total_funded else 0.0

    logger.info("Generating project dashboard", project_id=project_id)

    monthly_allocations = crud.get_project_monthly_allocations(db, project_id=project_id)
    allocation_map = {
        (row["year"], row["month"]): float(row.get("allocated_hours") or 0.0)
        for row in monthly_allocations
    }

    if allocation_map:
        min_year, min_month = min(allocation_map.keys())
        max_year, max_month = max(allocation_map.keys())
        start_month = date(min_year, min_month, 1)
        end_month = date(max_year, max_month, 1)
    else:
        start_month = date(db_project.start_date.year, db_project.start_date.month, 1)
        estimated_end = default_project_end(db_project.start_date, db_project.sprints)
        end_month = date(estimated_end.year, estimated_end.month, 1)

    month_windows = iter_months(start_month, end_month)
    if not month_windows:
        month_windows = [(start_month.year, start_month.month)]

    overrides = crud.get_overrides_for_project(db, project_id=project_id)
    override_map = {
        (override.year, override.month): override.overridden_hours
        for override in overrides
    }

    burn_down_data = build_burn_down_series(
        float(total_funded), month_windows, allocation_map, override_map
    )

    return ProjectDashboardResponse(
        project_id=project_id,
        project_name=db_project.name,
        total_funded_hours=total_funded,
        total_allocated_hours=total_allocated,
        utilization_pct=round(utilization, 2),
        burn_down_data=burn_down_data,
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
    project_breakdown_rows = crud.get_monthly_user_project_allocations(
        db, user_id=employee_id
    )

    breakdown_map: Dict[Tuple[int, int], List[ProjectAllocationBreakdown]] = defaultdict(list)
    for row in project_breakdown_rows:
        key = (row["year"], row["month"])
        breakdown_map[key].append(
            ProjectAllocationBreakdown(
                project_id=row["project_id"],
                project_name=row["project_name"],
                allocated_hours=int(row.get("allocated_hours") or 0),
            )
        )

    for allocations in breakdown_map.values():
        allocations.sort(key=lambda item: item.allocated_hours, reverse=True)

    # Filter by date range if provided
    if start_year and start_month:
        summary = [
            s
            for s in summary
            if (s['year'] > start_year) or (s['year'] == start_year and s['month'] >= start_month)
        ]

    if end_year and end_month:
        summary = [
            s
            for s in summary
            if (s['year'] < end_year) or (s['year'] == end_year and s['month'] <= end_month)
        ]

    logger.info("Generating employee timeline", user_id=employee_id)

    summary.sort(key=lambda item: (item["year"], item["month"]))

    timeline: List[EmployeeTimelineMonth] = []
    for item in summary:
        year = item["year"]
        month = item["month"]
        total_hours = int(item.get("total_hours") or 0)
        standard_hours = standard_month_hours(year, month)
        fte_percentage = (
            round((total_hours / standard_hours) * 100, 2) if standard_hours else 0.0
        )
        available_hours = max(standard_hours - total_hours, 0)

        timeline.append(
            EmployeeTimelineMonth(
                year=year,
                month=month,
                total_hours=total_hours,
                standard_hours=standard_hours,
                fte_percentage=fte_percentage,
                available_hours=available_hours,
                allocations=breakdown_map.get((year, month), []),
            )
        )

    return EmployeeTimelineResponse(
        employee_id=employee_id,
        employee_name=db_user.full_name,
        timeline=timeline,
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
    """
    logger.info("Exporting portfolio data to Excel")

    from sqlalchemy.orm import joinedload

    projects = (
        db.query(models.Project)
        .options(
            joinedload(models.Project.assignments).joinedload(models.ProjectAssignment.allocations),
            joinedload(models.Project.manager),
        )
        .all()
    )

    metrics = get_portfolio_dashboard(db)

    response = portfolio_workbook(
        projects=projects,
        over_allocated=metrics.over_allocated_employees,
        bench=metrics.bench_employees,
    )
    filename = f"staffalloc-portfolio-{date.today().isoformat()}.xlsx"

    return StreamingResponse(
        response,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
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
    logger.info("Exporting project data", project_id=project_id)

    project = crud.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    buffer = project_workbook(project)
    filename = f"staffalloc-project-{project.code}-{date.today().isoformat()}.xlsx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
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
    
    snapshot = crud.get_role_utilization_snapshot(db, year=year, month=month)
    standard_hours = max(standard_month_hours(year, month), 1)

    items: List[Dict[str, object]] = []
    for row in snapshot:
        allocated_hours = float(row.get("allocated_hours") or 0.0)
        funded_hours = float(row.get("funded_hours") or 0.0)
        fte_percentage = round((allocated_hours / standard_hours) * 100, 2)

        items.append(
            {
                "role_id": row.get("role_id"),
                "role_name": row.get("role_name"),
                "total_hours": int(allocated_hours),
                "fte_percentage": fte_percentage,
                "funded_hours": int(funded_hours),
                "assignment_count": int(row.get("assignment_count") or 0),
            }
        )

    items.sort(key=lambda item: item["fte_percentage"], reverse=True)

    return {
        "year": year,
        "month": month,
        "utilization_by_role": items,
    }

