"""Tests for AI-related endpoints."""

from __future__ import annotations

import pytest


@pytest.fixture
def ai_setup(client, api_prefix):
    role_id = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "AI Specialist", "description": "Supports AI workflows"},
    ).json()["id"]

    project_id = client.post(
        f"{api_prefix}/projects/",
        json={
            "name": "AI Project",
            "code": "PRJ-AI",
            "client": "Cyberdyne",
            "start_date": "2025-03-01",
            "sprints": 3,
            "status": "Active",
        },
    ).json()["id"]

    return {"role_id": role_id, "project_id": project_id}


def test_chat_endpoint_placeholder(client, api_prefix):
    response = client.post(
        f"{api_prefix}/ai/chat",
        json={"query": "What is the status of Project X?", "context_limit": 3},
    )
    # AI chat now returns real responses or configuration errors
    assert response.status_code in [200, 503]  # 503 if GOOGLE_API_KEY not configured
    if response.status_code == 200:
        data = response.json()
        assert "answer" in data
        assert "sources" in data


def test_recommend_staff_placeholder(client, api_prefix, ai_setup):
    payload = {
        "project_id": ai_setup["project_id"],
        "role_id": ai_setup["role_id"],
        "year": 2025,
        "month": 5,
        "required_hours": 120,
    }
    response = client.post(f"{api_prefix}/ai/recommend-staff", json=payload)
    assert response.status_code == 200
    assert response.json()["candidates"] == []


def test_recommend_staff_missing_entities(client, api_prefix):
    payload = {
        "project_id": 1234,
        "role_id": 5678,
        "year": 2025,
        "month": 6,
        "required_hours": 80,
    }
    project_missing = client.post(f"{api_prefix}/ai/recommend-staff", json=payload)
    assert project_missing.status_code == 404

    role_payload = payload.copy()
    role_payload["project_id"] = client.post(
        f"{api_prefix}/projects/",
        json={
            "name": "AI Missing Role",
            "code": "PRJ-AI-NO-ROLE",
            "client": "Skynet",
            "start_date": "2025-01-01",
            "sprints": 2,
            "status": "Active",
        },
    ).json()["id"]

    role_missing = client.post(
        f"{api_prefix}/ai/recommend-staff", json=role_payload
    )
    assert role_missing.status_code == 404


def test_conflict_forecast_balance_and_reindex(client, api_prefix, ai_setup):
    # AI features now return real responses or configuration errors
    conflicts = client.get(f"{api_prefix}/ai/conflicts")
    assert conflicts.status_code in [200, 503]
    if conflicts.status_code == 200:
        data = conflicts.json()
        assert "message" in data
        assert "conflicts" in data

    forecast = client.get(
        f"{api_prefix}/ai/forecast", params={"months_ahead": 6}
    )
    assert forecast.status_code in [200, 503]
    if forecast.status_code == 200:
        data = forecast.json()
        assert data["forecast_period_months"] == 6
        assert "predictions" in data

    balance = client.get(
        f"{api_prefix}/ai/balance-suggestions",
        params={"project_id": ai_setup["project_id"]},
    )
    assert balance.status_code in [200, 503]
    if balance.status_code == 200:
        data = balance.json()
        assert "suggestions" in data
        assert "message" in data

    reindex = client.post(f"{api_prefix}/ai/reindex")
    assert reindex.status_code == 202
    data = reindex.json()
    assert data["status"] == "accepted"
    assert "message" in data


