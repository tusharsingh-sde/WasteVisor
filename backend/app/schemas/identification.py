"""Strict vision identification request and response schemas."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.knowledge import Condition


class Identification(BaseModel):
    """Structured image understanding result returned by WasteVisor."""

    model_config = ConfigDict(extra="forbid")

    item: str = Field(min_length=1)
    material: list[str]
    category: str = Field(min_length=1)
    condition: Condition
    hazard_flags: list[str]
    confidence: float = Field(ge=0, le=1)
    needs_confirmation: bool
    safe_guidance: str | None = None

    @model_validator(mode="after")
    def unknown_items_require_confirmation(self) -> "Identification":
        if self.confidence < 0.5 or self.item == "unknown":
            self.needs_confirmation = True
        return self


class DemoMetadata(BaseModel):
    """Indicates whether the identification came from a cached demo result."""

    is_demo: bool
    sample_id: str | None = None


class IdentifyResponse(BaseModel):
    """Response shape for POST /api/identify."""

    identification: Identification
    demo: DemoMetadata
