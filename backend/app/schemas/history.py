"""Typed request and response schemas for action completion and history."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.knowledge import ActionType, Condition


class RecommendRequest(BaseModel):
    """Confirmed item details used for deterministic action ranking."""

    model_config = ConfigDict(extra="forbid")

    item: str = Field(min_length=1)
    condition: Condition
    city: str | None = None
    context: dict[str, str | bool | int | float] | None = None


class CompleteActionRequest(BaseModel):
    """User confirmation that a selected next action was completed."""

    model_config = ConfigDict(extra="forbid")

    item: str = Field(min_length=1)
    condition: Condition
    action_type: ActionType
    completed_at: datetime | None = None
    recovered_value_inr: float | None = Field(default=None, ge=0)


class EstimateMetric(BaseModel):
    """A number explicitly labeled as an estimate."""

    value: float = Field(ge=0)
    is_estimate: bool = True


class StoredImpact(BaseModel):
    """Impact estimates persisted for one completed action."""

    kg_diverted: float = Field(ge=0)
    co2e_saved_kg: float = Field(ge=0)
    is_estimate: bool = True


class HistoryEntry(BaseModel):
    """One completed action stored by WasteVisor."""

    id: str
    item: str
    condition: Condition
    action_type: ActionType
    completed_at: datetime
    impact: StoredImpact
    recovered_value_inr: EstimateMetric


class ImpactTotals(BaseModel):
    """Aggregated estimates from completed actions."""

    kg_diverted: EstimateMetric
    co2e_saved_kg: EstimateMetric
    recovered_value_inr: EstimateMetric


class CompleteActionResponse(BaseModel):
    """Completion receipt and updated estimated totals."""

    history_entry: HistoryEntry
    totals: ImpactTotals


class HistoryResponse(BaseModel):
    """Paginated action history."""

    items: list[HistoryEntry]
    total: int
    limit: int
    offset: int


class ImpactResponse(ImpactTotals):
    """Running totals derived from completed records."""

    basis: str


class CatalogItem(BaseModel):
    """One supported item and its selectable conditions."""

    id: str
    display_name: str
    category: str
    conditions: list[Condition]
    hazard_flags: list[str]


class ItemsResponse(BaseModel):
    """Supported catalog response."""

    items: list[CatalogItem]
