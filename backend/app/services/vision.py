"""Amazon Bedrock image identification with strict validation and safe fallback."""

import json
import logging
from typing import Any

import boto3
from pydantic import ValidationError

from app.schemas.identification import Identification
from app.schemas.knowledge import Condition, KnowledgeBase

logger = logging.getLogger("wastevisor.vision")

PROMPT = """Identify the household waste item in this image. Return exactly one JSON object with
these keys: item, material (array of strings), category, condition (working, damaged, dead, or
unknown), hazard_flags (array of strings), confidence (number from 0 to 1), and
needs_confirmation (boolean). Use a supported catalog item ID when recognizable; otherwise use
item='unknown', condition='unknown', confidence below 0.5, and needs_confirmation=true. Do not
include markdown, commentary, recommendations, or JSON fields not listed."""

SUPPORTED_MEDIA_TYPES = {
    "image/jpeg": "jpeg",
    "image/png": "png",
    "image/webp": "webp",
}


def safe_fallback() -> Identification:
    """Return conservative confirmation-required output if the model is unavailable."""
    return Identification(
        item="unknown",
        material=[],
        category="unknown",
        condition=Condition.UNKNOWN,
        hazard_flags=[],
        confidence=0.0,
        needs_confirmation=True,
        safe_guidance=(
            "WasteVisor could not identify this item with confidence. Keep it separate until "
            "its material and any hazards are confirmed."
        ),
    )


def _parse_model_text(text: str, knowledge: KnowledgeBase) -> Identification:
    """Parse strict JSON and normalize unknown/unsupported catalog items safely."""
    result = Identification.model_validate(json.loads(text))
    if result.item not in knowledge.items:
        result.item = "unknown"
        result.category = "unknown"
        result.condition = Condition.UNKNOWN
        result.needs_confirmation = True
    if result.confidence < 0.5:
        result.needs_confirmation = True
        result.condition = Condition.UNKNOWN
    return result


def identify_image(
    image_bytes: bytes,
    content_type: str,
    knowledge: KnowledgeBase,
    *,
    model_id: str,
    aws_region: str,
    model_client: Any | None = None,
) -> Identification:
    """Identify image content with one retry; never surface provider/model exceptions."""
    media_format = SUPPORTED_MEDIA_TYPES.get(content_type)
    if media_format is None:
        raise ValueError("Unsupported image type")
    if not model_id:
        logger.info("WasteVisor vision model is not configured; returning safe fallback")
        return safe_fallback()

    client = model_client or boto3.client("bedrock-runtime", region_name=aws_region)
    prompt = f"{PROMPT}\nSupported item IDs: {', '.join(knowledge.items)}."
    for attempt in range(2):
        try:
            response = client.converse(
                modelId=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"text": prompt},
                            {"image": {"format": media_format, "source": {"bytes": image_bytes}}},
                        ],
                    }
                ],
                inferenceConfig={"maxTokens": 500, "temperature": 0},
            )
            content: list[dict[str, Any]] = response["output"]["message"]["content"]
            model_text = next(part["text"] for part in content if "text" in part)
            return _parse_model_text(model_text, knowledge)
        except (ValidationError, json.JSONDecodeError, KeyError, StopIteration, TypeError) as exc:
            logger.warning(
                "WasteVisor received invalid model output (attempt %s/2): %s",
                attempt + 1,
                type(exc).__name__,
            )
        except Exception as exc:
            logger.warning(
                "WasteVisor vision provider failed (attempt %s/2): %s",
                attempt + 1,
                type(exc).__name__,
            )
    return safe_fallback()
