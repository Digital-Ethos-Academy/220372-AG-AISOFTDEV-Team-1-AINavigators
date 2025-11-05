import datetime
from uuid import uuid4

import pytest

from app import models


API_V1_PREFIX = "/api/v1"


def _create_role(client, name: str | None = None):
    role_name = name or f"Role-{uuid4().hex[:6]}"
    payload = {"name": role_name, "description": f"{role_name} description"}
    response = client.post(f"{API_V1_PREFIX}/admin/roles/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_lcat(client, name: str | None = None):
    lcat_name = name or f"LCAT-{uuid4().hex[:6]}"
    payload = {"name": lcat_name, "description": f"{lcat_name} description"}
    response = client.post(f"{API_V1_PREFIX}/admin/lcats/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_user(client, email: str | None = None, full_name: str | None = None):
    user_email = email or f"user{uuid4().hex[:6]}@example.com"
    user_name = full_name or "Test User"
    payload = {
        "email": user_email,
        "full_name": user_name,
        "password": "Password123!",
        "system_role": "Employee",
        "is_active": True,
    }
    response = client.post(f"{API_V1_PREFIX}/employees/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_project(client, code: str | None = None, manager_id: int | None = None):
    project_code = code or f"PRJ{uuid4().hex[:6].upper()}"
    payload = {
        "name": f"Project {project_code}",
        "code": project_code,
        "client": "Test Client",
        "start_date": datetime.date(2025, 1, 1).isoformat(),
        "sprints": 6,
        "manager_id": manager_id,
        "status": "Active",
    }
    response = client.post(f"{API_V1_PREFIX}/projects/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_assignment(client, project_id: int, user_id: int, role_id: int, lcat_id: int, funded_hours: int = 200):
    payload = {
        "project_id": project_id,
        "user_id": user_id,
        "role_id": role_id,
        "lcat_id": lcat_id,
        "funded_hours": funded_hours,
    }
    response = client.post(f"{API_V1_PREFIX}/allocations/assignments", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_allocation(client, assignment_id: int, year: int = 2025, month: int = 1, hours: int = 100):
    payload = {
        "project_assignment_id": assignment_id,
        "year": year,
        "month": month,
        "allocated_hours": hours,
    }
    response = client.post(f"{API_V1_PREFIX}/allocations/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _setup_base_entities(client):
    role = _create_role(client)
    lcat = _create_lcat(client)
    user = _create_user(client)
    project = _create_project(client)
    return role, lcat, user, project


def test_admin_role_lifecycle(client):
    role = _create_role(client, name="Software Engineer")
    role_id = role["id"]

    list_resp = client.get(f"{API_V1_PREFIX}/admin/roles/")
    assert list_resp.status_code == 200
    assert any(r["id"] == role_id for r in list_resp.json())

    get_resp = client.get(f"{API_V1_PREFIX}/admin/roles/{role_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Software Engineer"

    update_resp = client.put(
        f"{API_V1_PREFIX}/admin/roles/{role_id}",
        json={"description": "Updated role description"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["description"] == "Updated role description"

    delete_resp = client.delete(f"{API_V1_PREFIX}/admin/roles/{role_id}")
    assert delete_resp.status_code == 204

    not_found_resp = client.get(f"{API_V1_PREFIX}/admin/roles/{role_id}")
    assert not_found_resp.status_code == 404


def test_admin_lcat_lifecycle(client):
    lcat = _create_lcat(client, name="Level 1")
    lcat_id = lcat["id"]

    list_resp = client.get(f"{API_V1_PREFIX}/admin/lcats/")
    assert list_resp.status_code == 200
    assert any(item["id"] == lcat_id for item in list_resp.json())

    get_resp = client.get(f"{API_V1_PREFIX}/admin/lcats/{lcat_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Level 1"

    update_resp = client.put(
        f"{API_V1_PREFIX}/admin/lcats/{lcat_id}",
        json={"description": "Updated LCAT description"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["description"] == "Updated LCAT description"

    delete_resp = client.delete(f"{API_V1_PREFIX}/admin/lcats/{lcat_id}")
    assert delete_resp.status_code == 204

    not_found_resp = client.get(f"{API_V1_PREFIX}/admin/lcats/{lcat_id}")
    assert not_found_resp.status_code == 404


def test_employee_crud_flow(client):
    user = _create_user(client, email="alice@example.com", full_name="Alice Example")
    user_id = user["id"]

    list_resp = client.get(f"{API_V1_PREFIX}/employees/")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    get_resp = client.get(f"{API_V1_PREFIX}/employees/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["assignments"] == []

    update_resp = client.put(
        f"{API_V1_PREFIX}/employees/{user_id}",
        json={"full_name": "Alice Updated"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["full_name"] == "Alice Updated"

    delete_resp = client.delete(f"{API_V1_PREFIX}/employees/{user_id}")
    assert delete_resp.status_code == 204

    not_found_resp = client.get(f"{API_V1_PREFIX}/employees/{user_id}")
    assert not_found_resp.status_code == 404


def test_project_crud_flow(client):
    project = _create_project(client, code="PRJ001")
    project_id = project["id"]

    list_resp = client.get(f"{API_V1_PREFIX}/projects/")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    get_resp = client.get(f"{API_V1_PREFIX}/projects/{project_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["assignments"] == []

    update_resp = client.put(
        f"{API_V1_PREFIX}/projects/{project_id}",
        json={"status": "Closed"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "Closed"

    delete_resp = client.delete(f"{API_V1_PREFIX}/projects/{project_id}")
    assert delete_resp.status_code == 204

    not_found_resp = client.get(f"{API_V1_PREFIX}/projects/{project_id}")
    assert not_found_resp.status_code == 404


def test_project_overrides_flow(client):
    project = _create_project(client, code="PRJ002")
    override_payload = {
        "project_id": project["id"],
        "year": 2025,
        "month": 1,
        "overridden_hours": 160,
    }
    create_resp = client.post(f"{API_V1_PREFIX}/projects/overrides", json=override_payload)
    assert create_resp.status_code == 201
    override_id = create_resp.json()["id"]

    update_resp = client.put(
        f"{API_V1_PREFIX}/projects/overrides/{override_id}",
        json={"overridden_hours": 170},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["overridden_hours"] == 170

    delete_resp = client.delete(f"{API_V1_PREFIX}/projects/overrides/{override_id}")
    assert delete_resp.status_code == 204

    project_details = client.get(f"{API_V1_PREFIX}/projects/{project['id']}")
    assert project_details.status_code == 200
    assert project_details.json()["monthly_hour_overrides"] == []


def test_allocations_assignment_flow(client):
    role, lcat, user, project = _setup_base_entities(client)
    assignment = _create_assignment(
        client,
        project_id=project["id"],
        user_id=user["id"],
        role_id=role["id"],
        lcat_id=lcat["id"],
    )
    assignment_id = assignment["id"]

    assert assignment["project"]["id"] == project["id"]
    assert assignment["user"]["id"] == user["id"]

    get_resp = client.get(f"{API_V1_PREFIX}/allocations/assignments/{assignment_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["allocations"] == []

    update_resp = client.put(
        f"{API_V1_PREFIX}/allocations/assignments/{assignment_id}",
        json={"funded_hours": 220},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["funded_hours"] == 220

    delete_resp = client.delete(f"{API_V1_PREFIX}/allocations/assignments/{assignment_id}")
    assert delete_resp.status_code == 204

    not_found_resp = client.get(f"{API_V1_PREFIX}/allocations/assignments/{assignment_id}")
    assert not_found_resp.status_code == 404


def test_allocations_allocation_flow(client):
    role, lcat, user, project = _setup_base_entities(client)
    assignment = _create_assignment(
        client,
        project_id=project["id"],
        user_id=user["id"],
        role_id=role["id"],
        lcat_id=lcat["id"],
    )

    allocation = _create_allocation(client, assignment_id=assignment["id"], month=2, hours=120)
    allocation_id = allocation["id"]

    get_resp = client.get(f"{API_V1_PREFIX}/allocations/{allocation_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["allocated_hours"] == 120

    update_resp = client.put(
        f"{API_V1_PREFIX}/allocations/{allocation_id}",
        json={"allocated_hours": 140},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["allocated_hours"] == 140

    delete_resp = client.delete(f"{API_V1_PREFIX}/allocations/{allocation_id}")
    assert delete_resp.status_code == 204

    not_found_resp = client.get(f"{API_V1_PREFIX}/allocations/{allocation_id}")
    assert not_found_resp.status_code == 404


def test_user_allocation_summary(client):
    role, lcat, user, project = _setup_base_entities(client)
    assignment = _create_assignment(
        client,
        project_id=project["id"],
        user_id=user["id"],
        role_id=role["id"],
        lcat_id=lcat["id"],
        funded_hours=400,
    )
    _create_allocation(client, assignment_id=assignment["id"], year=2025, month=1, hours=100)
    _create_allocation(client, assignment_id=assignment["id"], year=2025, month=2, hours=80)

    summary_resp = client.get(f"{API_V1_PREFIX}/allocations/users/{user['id']}/summary")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert {item["month"]: item["total_hours"] for item in summary} == {1: 100, 2: 80}


def test_reports_endpoints(client):
    role, lcat, user, project = _setup_base_entities(client)
    assignment = _create_assignment(
        client,
        project_id=project["id"],
        user_id=user["id"],
        role_id=role["id"],
        lcat_id=lcat["id"],
        funded_hours=200,
    )
    _create_allocation(client, assignment_id=assignment["id"], year=2025, month=1, hours=120)

    portfolio_resp = client.get(f"{API_V1_PREFIX}/reports/portfolio-dashboard")
    assert portfolio_resp.status_code == 200
    portfolio = portfolio_resp.json()
    assert portfolio["total_projects"] == 1
    assert portfolio["total_employees"] == 1

    project_resp = client.get(f"{API_V1_PREFIX}/reports/project-dashboard/{project['id']}")
    assert project_resp.status_code == 200
    project_summary = project_resp.json()
    assert project_summary["total_funded_hours"] == 200
    assert project_summary["total_allocated_hours"] == 120

    timeline_resp = client.get(f"{API_V1_PREFIX}/reports/employee-timeline/{user['id']}")
    assert timeline_resp.status_code == 200
    assert len(timeline_resp.json()["timeline"]) == 1

    utilization_resp = client.get(f"{API_V1_PREFIX}/reports/utilization-by-role", params={"year": 2025, "month": 1})
    assert utilization_resp.status_code == 200

    export_portfolio_resp = client.get(f"{API_V1_PREFIX}/reports/export/portfolio")
    assert export_portfolio_resp.status_code == 501

    export_project_resp = client.get(f"{API_V1_PREFIX}/reports/export/project/{project['id']}")
    assert export_project_resp.status_code == 501


def test_admin_audit_and_rag_endpoints(client, db_session):
    user = _create_user(client)
    project = _create_project(client)

    audit_log = models.AuditLog(
        user_id=user["id"],
        action="PROJECT_CREATE",
        entity_type="project",
        entity_id=project["id"],
        details={"code": project["code"]},
    )
    db_session.add(audit_log)

    rag_item = models.AIRagCache(
        source_entity="project",
        source_id=project["id"],
        document_text="Sample document",
    )
    db_session.add(rag_item)

    recommendation = models.AIRecommendation(
        recommendation_type=models.RecommendationType.STAFFING,
        context_json={"project_id": project["id"]},
        recommendation_text="Add another engineer",
    )
    db_session.add(recommendation)
    db_session.commit()
    db_session.refresh(audit_log)
    db_session.refresh(rag_item)
    db_session.refresh(recommendation)

    audit_list_resp = client.get(f"{API_V1_PREFIX}/admin/audit-logs/")
    assert audit_list_resp.status_code == 200
    assert len(audit_list_resp.json()) == 1

    audit_entity_resp = client.get(
        f"{API_V1_PREFIX}/admin/audit-logs/project/{project['id']}"
    )
    assert audit_entity_resp.status_code == 200
    assert len(audit_entity_resp.json()) == 1

    recommendation_list_resp = client.get(f"{API_V1_PREFIX}/admin/recommendations/")
    assert recommendation_list_resp.status_code == 200
    assert len(recommendation_list_resp.json()) == 1

    recommendation_get_resp = client.get(
        f"{API_V1_PREFIX}/admin/recommendations/{recommendation.id}"
    )
    assert recommendation_get_resp.status_code == 200

    update_rec_resp = client.put(
        f"{API_V1_PREFIX}/admin/recommendations/{recommendation.id}",
        json={"status": "Accepted"},
    )
    assert update_rec_resp.status_code == 200
    assert update_rec_resp.json()["status"] == "Accepted"

    rag_list_resp = client.get(f"{API_V1_PREFIX}/admin/rag-cache/")
    assert rag_list_resp.status_code == 200
    assert len(rag_list_resp.json()) == 1

    rag_delete_resp = client.delete(f"{API_V1_PREFIX}/admin/rag-cache/{rag_item.id}")
    assert rag_delete_resp.status_code == 204

    rag_empty_resp = client.get(f"{API_V1_PREFIX}/admin/rag-cache/")
    assert rag_empty_resp.status_code == 200
    assert rag_empty_resp.json() == []


def test_ai_endpoints(client):
    project = _create_project(client)
    role = _create_role(client)

    chat_resp = client.post(
        f"{API_V1_PREFIX}/ai/chat",
        json={"query": "How many allocations exist?", "context_limit": 3},
    )
    assert chat_resp.status_code == 200
    assert "answer" in chat_resp.json()

    recommend_resp = client.post(
        f"{API_V1_PREFIX}/ai/recommend-staff",
        json={
            "project_id": project["id"],
            "role_id": role["id"],
            "year": 2025,
            "month": 1,
            "required_hours": 160,
        },
    )
    assert recommend_resp.status_code == 200
    assert "candidates" in recommend_resp.json()

    conflicts_resp = client.get(f"{API_V1_PREFIX}/ai/conflicts")
    assert conflicts_resp.status_code == 200

    forecast_resp = client.get(f"{API_V1_PREFIX}/ai/forecast", params={"months_ahead": 4})
    assert forecast_resp.status_code == 200

    balance_resp = client.get(
        f"{API_V1_PREFIX}/ai/balance-suggestions",
        params={"project_id": project["id"]},
    )
    assert balance_resp.status_code == 200

    reindex_resp = client.post(f"{API_V1_PREFIX}/ai/reindex")
    assert reindex_resp.status_code == 202

