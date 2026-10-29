"""Slice 1 API contract smoke tests."""

from app.main import create_app
from fastapi.testclient import TestClient


def test_health_returns_non_sensitive_readiness() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "demo_mode": True,
        "model_available": False,
        "storage": "sqlite",
    }


def test_openapi_metadata_uses_wastevisor_brand() -> None:
    client = TestClient(create_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "WasteVisor API"
    assert "/api/health" in response.json()["paths"]


def test_errors_use_shared_error_envelope() -> None:
    client = TestClient(create_app())

    response = client.get("/api/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "Not Found",
        }
    }


def test_startup_loads_validated_catalog_and_estimate_factors() -> None:
    client = TestClient(create_app())

    with client:
        assert len(client.app.state.knowledge_base.items) == 14
        assert set(client.app.state.knowledge_base.items) == set(
            client.app.state.impact_factors.factors
        )
