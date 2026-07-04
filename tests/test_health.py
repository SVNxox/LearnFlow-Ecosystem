"""
tests/test_health.py

Tests for liveness and readiness probes.
"""
import pytest

pytestmark = pytest.mark.django_db


class TestHealthEndpoints:
    def test_health_live_returns_200(self, api_client):
        resp = api_client.get("/health/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_health_live_contains_timestamp(self, api_client):
        resp = api_client.get("/health/")
        assert "timestamp" in resp.json()

    def test_health_ready_returns_200(self, api_client):
        resp = api_client.get("/health/ready/")
        assert resp.status_code == 200

    def test_health_ready_checks_db(self, api_client):
        resp = api_client.get("/health/ready/")
        data = resp.json()
        assert "db" in data["checks"]
        assert data["checks"]["db"] == "ok"

    def test_health_ready_checks_cache(self, api_client):
        resp = api_client.get("/health/ready/")
        data = resp.json()
        assert "cache" in data["checks"]
