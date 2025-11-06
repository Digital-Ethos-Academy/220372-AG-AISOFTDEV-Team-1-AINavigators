"""Tests for the administrative API endpoints."""

from __future__ import annotations

from datetime import datetime

from app import crud, schemas


def test_role_crud_flow(client, api_prefix):
    create_payload = {"name": "Software Engineer", "description": "Builds software"}
    response = client.post(f"{api_prefix}/admin/roles/", json=create_payload)
    assert response.status_code == 201
    role = response.json()
    role_id = role["id"]
    assert role["name"] == create_payload["name"]

    list_response = client.get(f"{api_prefix}/admin/roles/")
    assert list_response.status_code == 200
    roles = list_response.json()
    assert any(r["id"] == role_id for r in roles)

    detail_response = client.get(f"{api_prefix}/admin/roles/{role_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["description"] == create_payload["description"]

    update_payload = {"description": "Builds and maintains software systems"}
    update_response = client.put(
        f"{api_prefix}/admin/roles/{role_id}", json=update_payload
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == update_payload["description"]

    delete_response = client.delete(f"{api_prefix}/admin/roles/{role_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"{api_prefix}/admin/roles/{role_id}")
    assert missing_response.status_code == 404


def test_lcat_crud_flow(client, api_prefix):
    create_payload = {"name": "Level 1", "description": "Entry level"}
    response = client.post(f"{api_prefix}/admin/lcats/", json=create_payload)
    assert response.status_code == 201
    lcat_id = response.json()["id"]

    list_response = client.get(f"{api_prefix}/admin/lcats/")
    assert list_response.status_code == 200
    assert any(l["id"] == lcat_id for l in list_response.json())

    detail_response = client.get(f"{api_prefix}/admin/lcats/{lcat_id}")
    assert detail_response.status_code == 200

    update_response = client.put(
        f"{api_prefix}/admin/lcats/{lcat_id}",
        json={"description": "Junior labor category"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Junior labor category"

    delete_response = client.delete(f"{api_prefix}/admin/lcats/{lcat_id}")
    assert delete_response.status_code == 204


def test_audit_logs_listing(client, db_session, api_prefix):
    log_entry = schemas.AuditLogCreate(
        action="PROJECT_CREATE",
        entity_type="project",
        entity_id=1,
        user_id=None,
        details={"code": "PRJ-001"},
    )
    crud.create_audit_log(db_session, log_entry)
    db_session.commit()

    response = client.get(f"{api_prefix}/admin/audit-logs/")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["action"] == "PROJECT_CREATE"

    filtered = client.get(f"{api_prefix}/admin/audit-logs/project/1")
    assert filtered.status_code == 200
    filtered_logs = filtered.json()
    assert len(filtered_logs) == 1


def test_rag_cache_management(client, db_session, api_prefix):
    cache_item = schemas.AIRagCacheCreate(
        source_entity="project",
        source_id=99,
        document_text="Project summary text",
    )
    created = crud.create_or_update_rag_cache(db_session, cache_item)
    db_session.commit()

    list_response = client.get(f"{api_prefix}/admin/rag-cache/")
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 1
    assert items[0]["source_entity"] == "project"

    delete_response = client.delete(f"{api_prefix}/admin/rag-cache/{created.id}")
    assert delete_response.status_code == 204

    confirm_response = client.get(f"{api_prefix}/admin/rag-cache/")
    assert confirm_response.status_code == 200
    assert confirm_response.json() == []


def test_admin_ai_recommendation_endpoints(client, db_session, api_prefix):
    recommendation = schemas.AIRecommendationCreate(
        recommendation_type=schemas.RecommendationType.STAFFING,
        context_json={"project_id": 1},
        recommendation_text="Assign Alice to Project X",
    )
    record = crud.create_ai_recommendation(db_session, recommendation)
    db_session.commit()

    list_response = client.get(f"{api_prefix}/admin/recommendations/")
    assert list_response.status_code == 200
    records = list_response.json()
    assert len(records) == 1
    assert records[0]["id"] == record.id

    detail_response = client.get(
        f"{api_prefix}/admin/recommendations/{record.id}"
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["recommendation_text"] == "Assign Alice to Project X"

    update_payload = {"status": "Accepted"}
    update_response = client.put(
        f"{api_prefix}/admin/recommendations/{record.id}",
        json=update_payload,
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Accepted"

    filtered_response = client.get(
        f"{api_prefix}/admin/recommendations/",
        params={"status": "Accepted"},
    )
    assert filtered_response.status_code == 200
    filtered_records = filtered_response.json()
    assert len(filtered_records) == 1
    assert filtered_records[0]["status"] == "Accepted"


def test_admin_role_and_lcat_not_found_handling(client, api_prefix):
    missing_role = client.get(f"{api_prefix}/admin/roles/999")
    assert missing_role.status_code == 404

    missing_lcat = client.get(f"{api_prefix}/admin/lcats/999")
    assert missing_lcat.status_code == 404

    update_missing_role = client.put(
        f"{api_prefix}/admin/roles/999", json={"description": "N/A"}
    )
    assert update_missing_role.status_code == 404

    delete_missing_lcat = client.delete(f"{api_prefix}/admin/lcats/999")
    assert delete_missing_lcat.status_code == 404


