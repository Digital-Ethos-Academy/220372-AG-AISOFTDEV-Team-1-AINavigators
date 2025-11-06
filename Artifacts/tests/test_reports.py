"""Tests for reporting endpoints."""

from __future__ import annotations

import pytest


@pytest.fixture
def reports_seed(client, api_prefix):
    role_id = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "Consultant", "description": "Advises clients"},
    ).json()["id"]

    lcat_id = client.post(
        f"{api_prefix}/admin/lcats/",
        json={"name": "Senior", "description": "Experienced"},
    ).json()["id"]

    user = client.post(
        f"{api_prefix}/employees/",
        json={
            "email": "consultant@example.com",
            "full_name": "Casey Consultant",
            "password": "SecurePass9!",
            "system_role": "Employee",
            "is_active": True,
        },
    ).json()
    user_id = user["id"]

    project = client.post(
        f"{api_prefix}/projects/",
        json={
            "name": "Project Reports",
            "code": "PRJ-RPT",
            "client": "Initech",
            "start_date": "2025-01-01",
            "sprints": 4,
            "status": "Active",
        },
    ).json()
    project_id = project["id"]

    assignment = client.post(
        f"{api_prefix}/allocations/assignments",
        json={
            "project_id": project_id,
            "user_id": user_id,
            "role_id": role_id,
            "lcat_id": lcat_id,
            "funded_hours": 320,
        },
    ).json()
    assignment_id = assignment["id"]

    client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": assignment_id,
            "year": 2025,
            "month": 1,
            "allocated_hours": 160,
        },
    )

    client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": assignment_id,
            "year": 2025,
            "month": 2,
            "allocated_hours": 120,
        },
    )

    return {
        "role_id": role_id,
        "lcat_id": lcat_id,
        "user_id": user_id,
        "project_id": project_id,
        "assignment_id": assignment_id,
    }


def test_portfolio_dashboard(client, api_prefix, reports_seed):
    response = client.get(f"{api_prefix}/reports/portfolio-dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_projects"] == 1
    assert data["total_employees"] == 1
    assert isinstance(data["fte_by_role"], dict)


def test_project_dashboard(client, api_prefix, reports_seed):
    project_id = reports_seed["project_id"]
    response = client.get(f"{api_prefix}/reports/project-dashboard/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project_id
    assert data["total_funded_hours"] == 320
    assert data["total_allocated_hours"] == 280
    assert data["utilization_pct"] == round((280 / 320) * 100, 2)


def test_employee_timeline(client, api_prefix, reports_seed):
    user_id = reports_seed["user_id"]
    response = client.get(
        f"{api_prefix}/reports/employee-timeline/{user_id}",
        params={"start_year": 2025, "start_month": 1, "end_year": 2025, "end_month": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == user_id
    assert len(data["timeline"]) == 2


def test_utilization_by_role_placeholder(client, api_prefix, reports_seed):
    response = client.get(
        f"{api_prefix}/reports/utilization-by-role",
        params={"year": 2025, "month": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2025
    assert data["month"] == 1
    assert "message" in data


def test_export_endpoints(client, api_prefix, reports_seed):
    project_id = reports_seed["project_id"]

    portfolio_export = client.get(f"{api_prefix}/reports/export/portfolio")
    assert portfolio_export.status_code == 501

    project_export = client.get(
        f"{api_prefix}/reports/export/project/{project_id}"
    )
    assert project_export.status_code == 501


def test_reports_handles_missing_entities(client, api_prefix):
    missing_project = client.get(f"{api_prefix}/reports/project-dashboard/999")
    assert missing_project.status_code == 404

    missing_employee = client.get(
        f"{api_prefix}/reports/employee-timeline/999"
    )
    assert missing_employee.status_code == 404


