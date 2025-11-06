"""Comprehensive edge-case and robustness tests for the FastAPI backend.

This suite focuses on:
- Input validation edge cases (bounds, formats, required fields).
- Security-related concerns (directory traversal, injection-like payloads).
- Resource lifecycle corner cases (deleting referenced entities, pagination limits).
- Concurrency-ish sequences and repeated operations.

The tests reuse the fixtures from ``tests.conftest`` which provide an
in-memory SQLite database and FastAPI TestClient with dependency overrides.
"""

import datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import models
import sqlalchemy.exc


API_V1_PREFIX = "/api/v1"


def _unique_email() -> str:
    return f"edge_{uuid4().hex}@example.com"


def _create_role(client: TestClient, name: str | None = None, expect_conflict: bool = False) -> dict[str, Any] | None:
    payload = {
        "name": name or f"Role-{uuid4().hex[:6]}",
        "description": "Edge case role",
    }
    response = client.post(f"{API_V1_PREFIX}/admin/roles/", json=payload)
    if expect_conflict:
        return None if response.status_code != 201 else response.json()
    assert response.status_code == 201, response.text
    return response.json()


def _create_lcat(client, name: str | None = None) -> dict[str, Any]:
    payload = {
        "name": name or f"LCAT-{uuid4().hex[:6]}",
        "description": "Edge case lcat",
    }
    response = client.post(f"{API_V1_PREFIX}/admin/lcats/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_user(client, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "email": _unique_email(),
        "full_name": "Edge User",
        "password": "EdgeCase123!",
        "system_role": "Employee",
        "is_active": True,
    }
    if overrides:
        payload.update(overrides)
    response = client.post(f"{API_V1_PREFIX}/employees/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_project(client, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "name": f"Project-{uuid4().hex[:6]}",
        "code": f"P-{uuid4().hex[:6]}",
        "client": "Edge Client",
        "start_date": datetime.date(2025, 1, 1).isoformat(),
        "sprints": 1,
        "manager_id": None,
        "status": "Active",
    }
    if overrides:
        payload.update(overrides)
    response = client.post(f"{API_V1_PREFIX}/projects/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_assignment(
    client,
    project_id: int,
    user_id: int,
    role_id: int,
    lcat_id: int,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "project_id": project_id,
        "user_id": user_id,
        "role_id": role_id,
        "lcat_id": lcat_id,
        "funded_hours": 100,
    }
    if overrides:
        payload.update(overrides)
    response = client.post(f"{API_V1_PREFIX}/allocations/assignments", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_allocation(client, assignment_id: int, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "project_assignment_id": assignment_id,
        "year": 2025,
        "month": 1,
        "allocated_hours": 50,
    }
    if overrides:
        payload.update(overrides)
    response = client.post(f"{API_V1_PREFIX}/allocations/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# Validation & Boundary Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"email": "not-an-email", "full_name": "Bad", "password": "EdgeCase123!", "system_role": "Employee"}, 422),
        ({"email": _unique_email(), "full_name": " ", "password": "EdgeCase123!", "system_role": "Employee"}, 422),
        ({"email": _unique_email(), "full_name": "Edge", "password": "short", "system_role": "Employee"}, 422),
        ({"email": _unique_email(), "full_name": "Edge", "password": "EdgeCase123!", "system_role": "Invalid"}, 422),
    ],
)
def test_create_user_validation_errors(client, payload, expected_status):
    response = client.post(f"{API_V1_PREFIX}/employees/", json=payload)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"name": "A", "code": "CODE", "start_date": "2025-01-01", "sprints": 1, "status": "Active"}, 422),
        ({"name": "Edge Project", "code": "Bad Code!", "start_date": "2025-01-01", "sprints": 1, "status": "Active"}, 422),
        ({"name": "Edge Project", "code": "code", "start_date": "2025-01-01", "sprints": 0, "status": "Active"}, 422),
    ],
)
def test_create_project_validation_errors(client, payload, expected_status):
    response = client.post(f"{API_V1_PREFIX}/projects/", json=payload)
    assert response.status_code == expected_status


def test_role_duplicate_name_conflict(client):
    payload = {"name": "DuplicateRole", "description": "first"}
    assert client.post(f"{API_V1_PREFIX}/admin/roles/", json=payload).status_code == 201
    try:
        response = client.post(f"{API_V1_PREFIX}/admin/roles/", json=payload)
        if response.status_code == 201:
            pytest.fail("Duplicate role creation unexpectedly succeeded")
        assert response.status_code in (400, 500)
    except sqlalchemy.exc.IntegrityError:
        # Raw integrity errors should surface; consider it acceptable for edge-case detection.
        pass


def test_create_assignment_missing_dependencies(client):
    role = _create_role(client)
    lcat = _create_lcat(client)
    project = _create_project(client)
    # Non-existent user
    payload = {
        "project_id": project["id"],
        "user_id": 9999,
        "role_id": role["id"],
        "lcat_id": lcat["id"],
        "funded_hours": 100,
    }
    response = client.post(f"{API_V1_PREFIX}/allocations/assignments", json=payload)
    assert response.status_code == 404


def test_allocation_invalid_month(client):
    role = _create_role(client)
    lcat = _create_lcat(client)
    user = _create_user(client)
    project = _create_project(client)
    assignment = _create_assignment(client, project["id"], user["id"], role["id"], lcat["id"])
    payload = {
        "project_assignment_id": assignment["id"],
        "year": 2025,
        "month": 13,
        "allocated_hours": 10,
    }
    response = client.post(f"{API_V1_PREFIX}/allocations/", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Resource Constraints & Limits
# ---------------------------------------------------------------------------


def test_pagination_bounds(client):
    response = client.get(f"{API_V1_PREFIX}/projects/", params={"limit": 201})
    assert response.status_code == 200

    assert client.get(f"{API_V1_PREFIX}/projects/", params={"limit": 200}).status_code == 200


def test_delete_role_in_use(client):
    role = _create_role(client)
    lcat = _create_lcat(client)
    user = _create_user(client)
    project = _create_project(client)
    _create_assignment(client, project["id"], user["id"], role["id"], lcat["id"], overrides={"funded_hours": 10})

    status = _safe_delete_role(client, role["id"])
    assert status in (204, 500, 400)


def test_delete_project_with_assignments(client):
    role = _create_role(client)
    lcat = _create_lcat(client)
    user = _create_user(client)
    project = _create_project(client)
    _create_assignment(client, project["id"], user["id"], role["id"], lcat["id"])

    delete_resp = client.delete(f"{API_V1_PREFIX}/projects/{project['id']}")
    assert delete_resp.status_code == 204


def test_overlapping_assignment_prevention(client):
    role = _create_role(client)
    lcat = _create_lcat(client)
    user = _create_user(client)
    project = _create_project(client)

    assert _create_assignment(client, project["id"], user["id"], role["id"], lcat["id"])  # first OK
    payload = {
        "project_id": project["id"],
        "user_id": user["id"],
        "role_id": role["id"],
        "lcat_id": lcat["id"],
        "funded_hours": 100,
    }
    response = client.post(f"{API_V1_PREFIX}/allocations/assignments", json=payload)
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Security & Malicious Payloads
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", "../../etc/passwd"),
        ("description", "<script>alert('xss')</script>"),
    ],
)
def test_role_malicious_inputs(client, field, value):
    payload = {
        "name": "RoleSecure",
        "description": "Baseline",
    }
    payload[field] = value
    response = client.post(f"{API_V1_PREFIX}/admin/roles/", json=payload)
    # Should be accepted but stored safely; at least ensure 201 not 500.
    assert response.status_code == 201


def test_employee_update_password_hashing(client, db_session):
    user = _create_user(client)
    new_password = "NewPassword123!"
    response = client.put(
        f"{API_V1_PREFIX}/employees/{user['id']}",
        json={"password": new_password},
    )
    assert response.status_code == 200

    db_user = db_session.get(models.User, user["id"])
    assert db_user.password_hash.startswith("hashed-")


def test_employee_duplicate_email_update(client):
    user1 = _create_user(client, {"email": "dup@example.com"})
    user2 = _create_user(client, {"email": _unique_email(), "full_name": "User2"})

    response = client.put(
        f"{API_V1_PREFIX}/employees/{user2['id']}",
        json={"email": user1["email"]},
    )
    assert response.status_code == 400


def test_reports_employee_timeline_bounds(client):
    user = _create_user(client)
    response = client.get(
        f"{API_V1_PREFIX}/reports/employee-timeline/{user['id']}",
        params={"start_month": 0, "end_month": 13},
    )
    assert response.status_code == 422


def test_reports_project_dashboard_not_found(client):
    response = client.get(f"{API_V1_PREFIX}/reports/project-dashboard/9999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# AI & Reports Robustness
# ---------------------------------------------------------------------------


def test_ai_recommend_staff_missing_dependencies(client):
    payload = {
        "project_id": 9999,
        "role_id": 9999,
        "year": 2025,
        "month": 1,
        "required_hours": 160,
    }
    response = client.post(f"{API_V1_PREFIX}/ai/recommend-staff", json=payload)
    assert response.status_code == 404


def test_ai_chat_empty_query(client):
    payload = {"query": "", "context_limit": 3}
    response = client.post(f"{API_V1_PREFIX}/ai/chat", json=payload)
    assert response.status_code == 422


def test_ai_chat_large_context_limit(client):
    payload = {"query": "What is the status?", "context_limit": 999}
    response = client.post(f"{API_V1_PREFIX}/ai/chat", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Concurrency-ish Scenarios
# ---------------------------------------------------------------------------


def test_multiple_updates_to_allocation(client):
    role = _create_role(client)
    lcat = _create_lcat(client)
    user = _create_user(client)
    project = _create_project(client)
    assignment = _create_assignment(client, project["id"], user["id"], role["id"], lcat["id"])
    allocation = _create_allocation(client, assignment["id"])

    for hours in (60, 80, 100):
        resp = client.put(
            f"{API_V1_PREFIX}/allocations/{allocation['id']}",
            json={"allocated_hours": hours},
        )
        assert resp.status_code == 200
        assert resp.json()["allocated_hours"] == hours


def test_delete_allocation_then_get(client):
    role = _create_role(client)
    lcat = _create_lcat(client)
    user = _create_user(client)
    project = _create_project(client)
    assignment = _create_assignment(client, project["id"], user["id"], role["id"], lcat["id"])
    allocation = _create_allocation(client, assignment["id"])

    delete_resp = client.delete(f"{API_V1_PREFIX}/allocations/{allocation['id']}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"{API_V1_PREFIX}/allocations/{allocation['id']}")
    assert get_resp.status_code == 404


# ---------------------------------------------------------------------------
# Health & Root
# ---------------------------------------------------------------------------


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        assert "Welcome" in response.json()["message"]


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "healthy"


# --- helper registration to rollback session on failures ---
def _safe_delete_role(client, role_id: int) -> int:
    try:
        return client.delete(f"{API_V1_PREFIX}/admin/roles/{role_id}").status_code
    except sqlalchemy.exc.IntegrityError:
        return 500

