"""Typed recommendation and explicitly estimated impact result models."""

from pydantic import BaseModel, Field

from app.schemas.knowledge import ActionType


class EstimatedValue(BaseModel):
    """Indicative INR range, never a guaranteed resale quote."""

    min: float = Field(ge=0)
    max: float = Field(ge=0)
    is_estimate: bool = True
    basis: str


class ImpactEstimate(BaseModel):
    """Indicative diversion and emissions figures with their assumptions."""

    kg_diverted: float = Field(ge=0)
    co2e_saved_kg: float = Field(ge=0)
    is_estimate: bool = True
    basis: str


class RecommendedAction(BaseModel):
    """One rules-ranked action and concrete household next steps."""

    action_type: ActionType
    rank: int = Field(ge=1)
    why_best: str
    reason_codes: list[str]
    effort_minutes: int = Field(ge=0)
    estimated_value_inr: EstimatedValue | None
    impact: ImpactEstimate | None
    next_steps: list[str]
    preparation_checklist: list[str]
    safety_warning: str | None


class RecommendationResult(BaseModel):
    """Recommendation outcome for a known or unsupported item."""

    item: str
    condition: str
    needs_confirmation: bool
    safe_guidance: str | None = None
    recommended_actions: list[RecommendedAction]
