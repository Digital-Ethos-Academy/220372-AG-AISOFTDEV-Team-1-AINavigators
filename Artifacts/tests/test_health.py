"""Health and root endpoint tests for the StaffAlloc backend."""

from __future__ import annotations


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["message"].startswith("Welcome to the")
    assert "version" in body


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["dependencies"]["database"] == "ok"
    assert body["dependencies"]["llm_service"] in {"ok", "unavailable"}


