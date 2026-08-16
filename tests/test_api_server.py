"""
Tests for FastAPI REST and WebSocket API Server.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.api_server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "capabilities" in data


def test_auth_login_success(client):
    with patch("app.auth.SecurityManager.authenticate") as mock_auth:
        mock_auth.return_value = ({"username": "admin", "role": "admin", "tenant_id": "default"}, "Login successful")

        response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "correct_password"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["username"] == "admin"


def test_auth_login_failure(client):
    with patch("app.auth.SecurityManager.authenticate") as mock_auth:
        mock_auth.return_value = (None, "Invalid credentials")
        response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong_password"})
        assert response.status_code == 401


def test_telemetry_predict(client):
    telemetry_payload = {
        "cpu_percent": 95.0,
        "memory_percent": 90.0,
        "disk_percent": 50.0,
        "db_connections": 98.0,
        "db_pool_usage": 99.0,
        "api_latency_ms": 1500.0,
        "error_rate": 12.0,
        "request_rate": 2000.0,
        "queue_depth": 180.0,
        "network_latency_ms": 100.0,
        "traffic_growth_percent": 30.0,
    }
    response = client.post("/api/v1/telemetry/predict", json=telemetry_payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_failure_type" in data
    assert "failure_risk" in data


def test_copilot_chat(client):
    with patch("app.sre_chat.SRECopilot.ask") as mock_ask:
        mock_ask.return_value = "Simulated SRE diagnostic answer"
        response = client.post("/api/v1/copilot/chat", json={"message": "What is wrong with Redis?"})
        assert response.status_code == 200
        assert response.json()["reply"] == "Simulated SRE diagnostic answer"


def test_audit_logs(client):
    with patch("app.auth.SecurityManager.get_audit_logs") as mock_logs:
        mock_logs.return_value = [{"event_type": "AUTH_LOGIN", "actor": "admin"}]
        response = client.get("/api/v1/audit/logs")
        assert response.status_code == 200
        assert "audit_logs" in response.json()
