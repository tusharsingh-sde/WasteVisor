"""Bedrock vision validation tests using a mocked Converse client."""

import os
from pathlib import Path

import pytest
from app.data.loader import load_knowledge_base
from app.schemas.knowledge import Condition
from app.services.vision import identify_image

KNOWLEDGE = load_knowledge_base()
VALID_RESULT = (
    '{"item":"old_smartphone","material":["glass","metal"],'
    '"category":"e_waste","condition":"working","hazard_flags":[], '
    '"confidence":0.91,"needs_confirmation":false}'
)


class FakeConverseClient:
    """Return configured Bedrock-style responses or raise queued exceptions."""

    def __init__(self, outcomes: list[object]) -> None:
        self.outcomes = outcomes
        self.calls: list[dict[str, object]] = []

    def converse(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return {"output": {"message": {"content": [{"text": outcome}]}}}


def identify_with(client: FakeConverseClient):
    return identify_image(
        b"image-bytes",
        "image/jpeg",
        KNOWLEDGE,
        model_id="test-model",
        aws_region="us-east-1",
        model_client=client,
    )


def test_valid_converse_json_is_schema_validated() -> None:
    client = FakeConverseClient([VALID_RESULT])

    result = identify_with(client)

    assert result.item == "old_smartphone"
    assert result.condition == Condition.WORKING
    assert result.needs_confirmation is False
    assert len(client.calls) == 1


def test_malformed_output_retries_once_then_returns_safe_fallback() -> None:
    client = FakeConverseClient(["not json", "still not json"])

    result = identify_with(client)

    assert len(client.calls) == 2
    assert result.item == "unknown"
    assert result.condition == Condition.UNKNOWN
    assert result.confidence == 0
    assert result.needs_confirmation is True


def test_model_exception_retries_and_does_not_escape() -> None:
    client = FakeConverseClient([RuntimeError("secret provider detail"), RuntimeError("failed")])

    result = identify_with(client)

    assert len(client.calls) == 2
    assert result.needs_confirmation is True
    assert "secret provider detail" not in str(result.model_dump())


def test_low_confidence_or_unsupported_item_requires_confirmation() -> None:
    low_confidence = VALID_RESULT.replace('"confidence":0.91', '"confidence":0.2')
    client = FakeConverseClient([low_confidence])

    result = identify_with(client)

    assert result.needs_confirmation is True
    assert result.condition == Condition.UNKNOWN


def test_model_unavailable_uses_fallback_without_calling_provider() -> None:
    result = identify_image(
        b"image-bytes",
        "image/png",
        KNOWLEDGE,
        model_id="",
        aws_region="us-east-1",
    )

    assert result.item == "unknown"
    assert result.needs_confirmation is True


@pytest.mark.live
@pytest.mark.skipif(
    os.getenv("RUN_LIVE_TESTS") != "1" or not os.getenv("BEDROCK_MODEL_ID"),
    reason="Set RUN_LIVE_TESTS=1 and BEDROCK_MODEL_ID to enable Bedrock integration test.",
)
def test_live_bedrock_identification() -> None:
    """Optional connectivity check; relies on AWS credentials from the normal SDK chain."""
    from app.core.config import get_settings

    settings = get_settings()
    result = identify_image(
        (Path(__file__).parents[2] / "src" / "dummy.jpg").read_bytes(),
        "image/jpeg",
        KNOWLEDGE,
        model_id=settings.bedrock_model_id,
        aws_region=settings.aws_region,
    )
    assert 0 <= result.confidence <= 1
