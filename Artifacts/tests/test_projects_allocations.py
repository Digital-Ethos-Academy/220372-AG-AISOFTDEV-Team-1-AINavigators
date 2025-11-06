"""Integration tests for project and allocation workflows."""

from __future__ import annotations

from datetime import date


def _create_employee(client, api_prefix, email="john.doe@example.com"):
    payload = {
        "email": email,
        "full_name": "John Doe",
        "password": "Password1!",
        "system_role": "Employee",
        "is_active": True,
    }
    return client.post(f"{api_prefix}/employees/", json=payload)


def _create_project(client, api_prefix, code="PRJ-001"):
    payload = {
        "name": "Project Alpha",
        "code": code,
        "client": "Acme Corp",
        "start_date": date.today().isoformat(),
        "sprints": 6,
        "status": "Active",
    }
    return client.post(f"{api_prefix}/projects/", json=payload)


def test_project_crud_and_overrides(client, api_prefix):
    create_response = _create_project(client, api_prefix)
    assert create_response.status_code == 201
    project = create_response.json()
    project_id = project["id"]

    list_response = client.get(f"{api_prefix}/projects/")
    assert list_response.status_code == 200
    assert any(p["id"] == project_id for p in list_response.json())

    detail_response = client.get(f"{api_prefix}/projects/{project_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["assignments"] == []
    assert detail["monthly_hour_overrides"] == []

    update_response = client.put(
        f"{api_prefix}/projects/{project_id}",
        json={"status": "Closed", "client": "Globex"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Closed"

    override_payload = {
        "project_id": project_id,
        "year": 2025,
        "month": 1,
        "overridden_hours": 120,
    }
    override_response = client.post(
        f"{api_prefix}/projects/overrides", json=override_payload
    )
    assert override_response.status_code == 201
    override_id = override_response.json()["id"]

    override_update = client.put(
        f"{api_prefix}/projects/overrides/{override_id}",
        json={"overridden_hours": 150},
    )
    assert override_update.status_code == 200
    assert override_update.json()["overridden_hours"] == 150

    delete_override = client.delete(
        f"{api_prefix}/projects/overrides/{override_id}"
    )
    assert delete_override.status_code == 204

    delete_project = client.delete(f"{api_prefix}/projects/{project_id}")
    assert delete_project.status_code == 204

    missing_response = client.get(f"{api_prefix}/projects/{project_id}")
    assert missing_response.status_code == 404


def test_project_duplicate_code_rejected(client, api_prefix):
    first = _create_project(client, api_prefix, code="PRJ-DUP")
    assert first.status_code == 201

    duplicate = _create_project(client, api_prefix, code="PRJ-DUP")
    assert duplicate.status_code == 400
    assert "already exists" in duplicate.json()["detail"]


def test_allocation_workflow(client, api_prefix):
    role_resp = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "Data Analyst", "description": "Analyzes data"},
    )
    assert role_resp.status_code == 201
    role_id = role_resp.json()["id"]

    lcat_resp = client.post(
        f"{api_prefix}/admin/lcats/",
        json={"name": "Level 2", "description": "Mid level"},
    )
    assert lcat_resp.status_code == 201
    lcat_id = lcat_resp.json()["id"]

    user_resp = _create_employee(client, api_prefix)
    assert user_resp.status_code == 201
    user_id = user_resp.json()["id"]

    project_resp = _create_project(client, api_prefix, code="PRJ-ALLOC")
    assert project_resp.status_code == 201
    project_id = project_resp.json()["id"]

    assignment_payload = {
        "project_id": project_id,
        "user_id": user_id,
        "role_id": role_id,
        "lcat_id": lcat_id,
        "funded_hours": 400,
    }
    assignment_resp = client.post(
        f"{api_prefix}/allocations/assignments", json=assignment_payload
    )
    assert assignment_resp.status_code == 201
    assignment = assignment_resp.json()
    assignment_id = assignment["id"]

    assignment_detail = client.get(
        f"{api_prefix}/allocations/assignments/{assignment_id}"
    )
    assert assignment_detail.status_code == 200
    assert assignment_detail.json()["allocations"] == []

    assignment_update = client.put(
        f"{api_prefix}/allocations/assignments/{assignment_id}",
        json={"funded_hours": 420},
    )
    assert assignment_update.status_code == 200
    assert assignment_update.json()["funded_hours"] == 420

    allocation_payload = {
        "project_assignment_id": assignment_id,
        "year": 2025,
        "month": 2,
        "allocated_hours": 160,
    }
    allocation_resp = client.post(
        f"{api_prefix}/allocations/", json=allocation_payload
    )
    assert allocation_resp.status_code == 201
    allocation_id = allocation_resp.json()["id"]

    allocation_detail = client.get(
        f"{api_prefix}/allocations/{allocation_id}"
    )
    assert allocation_detail.status_code == 200
    assert allocation_detail.json()["allocated_hours"] == 160

    allocation_update = client.put(
        f"{api_prefix}/allocations/{allocation_id}",
        json={"allocated_hours": 170},
    )
    assert allocation_update.status_code == 200
    assert allocation_update.json()["allocated_hours"] == 170

    summary_resp = client.get(
        f"{api_prefix}/allocations/users/{user_id}/summary"
    )
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary == [{"year": 2025, "month": 2, "total_hours": 170}]

    delete_allocation = client.delete(
        f"{api_prefix}/allocations/{allocation_id}"
    )
    assert delete_allocation.status_code == 204

    delete_assignment = client.delete(
        f"{api_prefix}/allocations/assignments/{assignment_id}"
    )
    assert delete_assignment.status_code == 204


def test_assignment_duplicate_user_project_disallowed(client, api_prefix):
    role_resp = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "Tester", "description": "Tests software"},
    )
    lcat_resp = client.post(
        f"{api_prefix}/admin/lcats/",
        json={"name": "QA", "description": "Quality"},
    )
    user_resp = _create_employee(client, api_prefix, email="qa@example.com")
    project_resp = _create_project(client, api_prefix, code="PRJ-DUPE-ASSIGN")

    assignment_payload = {
        "project_id": project_resp.json()["id"],
        "user_id": user_resp.json()["id"],
        "role_id": role_resp.json()["id"],
        "lcat_id": lcat_resp.json()["id"],
        "funded_hours": 200,
    }

    create_resp = client.post(
        f"{api_prefix}/allocations/assignments", json=assignment_payload
    )
    assert create_resp.status_code == 201

    duplicate_resp = client.post(
        f"{api_prefix}/allocations/assignments", json=assignment_payload
    )
    assert duplicate_resp.status_code == 400
    assert "already assigned" in duplicate_resp.json()["detail"].lower()


def test_allocation_requires_existing_assignment(client, api_prefix):
    response = client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": 9999,
            "year": 2025,
            "month": 3,
            "allocated_hours": 40,
        },
    )
    assert response.status_code == 404


def test_allocation_validation_rules(client, api_prefix):
    role_id = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "Validation Engineer", "description": "Ensures integrity"},
    ).json()["id"]
    lcat_id = client.post(
        f"{api_prefix}/admin/lcats/",
        json={"name": "Level V", "description": "Expert"},
    ).json()["id"]
    user_id = _create_employee(client, api_prefix, email="validator@example.com").json()[
        "id"
    ]
    project_id = _create_project(client, api_prefix, code="PRJ-VALID").json()["id"]

    assignment_id = client.post(
        f"{api_prefix}/allocations/assignments",
        json={
            "project_id": project_id,
            "user_id": user_id,
            "role_id": role_id,
            "lcat_id": lcat_id,
            "funded_hours": 150,
        },
    ).json()["id"]

    negative_hours = client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": assignment_id,
            "year": 2025,
            "month": 5,
            "allocated_hours": -10,
        },
    )
    assert negative_hours.status_code == 422

    invalid_month = client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": assignment_id,
            "year": 2025,
            "month": 13,
            "allocated_hours": 40,
        },
    )
    assert invalid_month.status_code == 422


def test_user_allocation_summary_detects_over_allocation(client, api_prefix):
    role_id = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "Architect", "description": "Designs systems"},
    ).json()["id"]

    lcat_id = client.post(
        f"{api_prefix}/admin/lcats/",
        json={"name": "Principal QA", "description": "Principal"},
    ).json()["id"]

    user_id = _create_employee(client, api_prefix, email="overload@example.com").json()[
        "id"
    ]

    project_a = _create_project(client, api_prefix, code="PRJ-OVER-A").json()["id"]
    project_b = _create_project(client, api_prefix, code="PRJ-OVER-B").json()["id"]

    assignment_a = client.post(
        f"{api_prefix}/allocations/assignments",
        json={
            "project_id": project_a,
            "user_id": user_id,
            "role_id": role_id,
            "lcat_id": lcat_id,
            "funded_hours": 300,
        },
    ).json()["id"]

    assignment_b = client.post(
        f"{api_prefix}/allocations/assignments",
        json={
            "project_id": project_b,
            "user_id": user_id,
            "role_id": role_id,
            "lcat_id": lcat_id,
            "funded_hours": 300,
        },
    ).json()["id"]

    client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": assignment_a,
            "year": 2025,
            "month": 4,
            "allocated_hours": 120,
        },
    )

    client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": assignment_b,
            "year": 2025,
            "month": 4,
            "allocated_hours": 100,
        },
    )

    summary = client.get(
        f"{api_prefix}/allocations/users/{user_id}/summary"
    ).json()

    assert summary == [
        {"year": 2025, "month": 4, "total_hours": 220},
    ]
    # Validate that business logic consumers can detect over-allocation (>160 hours typical FTE month).
    assert summary[0]["total_hours"] > 160


