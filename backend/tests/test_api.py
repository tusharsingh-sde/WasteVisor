"""Slice 5 API behavior tests with isolated SQLite storage."""

from collections.abc import Iterator

import pytest
from app.core.config import Settings
from app.main import create_app
from app.schemas.identification import Identification
from app.schemas.knowledge import Condition
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path) -> Iterator[TestClient]:
    """Build an API instance with an isolated in-memory database."""
    settings = Settings(
        _env_file=None,
        demo_mode=False,
        database_url="sqlite:///:memory:",
        db_path=str(tmp_path / "unused.db"),
        max_upload_size_bytes=5 * 1024 * 1024,
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def test_identify_returns_structured_confirmation_fallback(client, monkeypatch) -> None:
    def fallback(*_args, **_kwargs):
        return Identification(
            item="unknown",
            material=[],
            category="unknown",
            condition=Condition.UNKNOWN,
            hazard_flags=[],
            confidence=0,
            needs_confirmation=True,
            safe_guidance="Keep separate until confirmed.",
        )

    monkeypatch.setattr("app.api.identify.identify_image", fallback)

    response = client.post(
        "/api/identify",
        files={"image": ("sample.png", b"sample-image", "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["identification"]["needs_confirmation"] is True
    assert response.json()["demo"]["is_demo"] is False


def test_identify_rejects_unsupported_mime_type(client) -> None:
    response = client.post(
        "/api/identify",
        files={"image": ("sample.gif", b"GIF89a", "image/gif")},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"


def test_identify_rejects_upload_over_five_megabytes(client) -> None:
    response = client.post(
        "/api/identify",
        files={"image": ("large.jpg", b"x" * (5 * 1024 * 1024 + 1), "image/jpeg")},
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "payload_too_large"


def test_recommend_returns_ranked_action_and_unknown_fallback(client) -> None:
    known = client.post(
        "/api/recommend",
        json={"item": "old_smartphone", "condition": "working"},
    )
    unknown = client.post(
        "/api/recommend",
        json={"item": "unlisted_item", "condition": "unknown"},
    )

    assert known.status_code == 200
    assert known.json()["recommended_actions"][0]["action_type"] == "resale"
    assert known.json()["recommended_actions"][0]["impact"]["is_estimate"] is True
    assert unknown.json()["needs_confirmation"] is True
    assert unknown.json()["safe_guidance"]


def test_completed_actions_persist_and_update_impact_totals(client) -> None:
    completion = client.post(
        "/api/actions/complete",
        json={
            "item": "old_smartphone",
            "condition": "working",
            "action_type": "resale",
            "recovered_value_inr": 3500,
        },
    )
    history = client.get("/api/history")
    impact = client.get("/api/impact")

    assert completion.status_code == 201
    assert completion.json()["totals"]["kg_diverted"]["is_estimate"] is True
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["action_type"] == "resale"
    assert impact.json()["kg_diverted"]["value"] == 0.18
    assert impact.json()["co2e_saved_kg"]["is_estimate"] is True
    assert impact.json()["recovered_value_inr"]["value"] == 3500


def test_rejects_action_not_eligible_for_item_and_condition(client) -> None:
    response = client.post(
        "/api/actions/complete",
        json={
            "item": "household_battery",
            "condition": "dead",
            "action_type": "recycling",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_items_endpoint_lists_supported_conditions(client) -> None:
    response = client.get("/api/items")
    items = {item["id"]: item for item in response.json()["items"]}

    assert len(items) == 14
    assert items["old_smartphone"]["conditions"] == ["working", "damaged", "dead", "unknown"]


def test_demo_sample_list_and_cached_identification(client) -> None:
    client.app.state.settings.demo_mode = True
    sample_list = client.get("/api/demo/samples")
    sample_ids = {sample["id"] for sample in sample_list.json()["samples"]}

    assert sample_ids == {"smartphone_working", "food_scraps", "used_battery"}
    image_response = client.get("/samples/smartphone_working.jpg")
    assert image_response.status_code == 200
    identification = client.post(
        "/api/identify",
        data={"sample_id": "smartphone_working"},
        files={"image": ("smartphone.jpg", b"sample image bytes", "image/jpeg")},
    )

    assert identification.status_code == 200
    assert identification.json()["identification"]["item"] == "old_smartphone"
    assert identification.json()["demo"] == {
        "is_demo": True,
        "sample_id": "smartphone_working",
    }
