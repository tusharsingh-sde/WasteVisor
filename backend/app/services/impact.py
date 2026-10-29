"""Deterministic estimate calculation from documented WasteVisor factors."""

from app.schemas.knowledge import ImpactFactor
from app.schemas.recommendation import EstimatedValue, ImpactEstimate


def estimate_item_impact(factor: ImpactFactor) -> ImpactEstimate:
    """Return the documented item's diversion and CO2e estimates."""
    return ImpactEstimate(
        kg_diverted=factor.kg_diverted,
        co2e_saved_kg=factor.co2e_saved_kg,
        is_estimate=True,
        basis=factor.source_note,
    )


def estimate_item_value(factor: ImpactFactor) -> EstimatedValue:
    """Return the documented indicative INR range."""
    return EstimatedValue(
        min=factor.estimated_value_inr.min,
        max=factor.estimated_value_inr.max,
        is_estimate=True,
        basis=factor.source_note,
    )
