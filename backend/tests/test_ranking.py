"""Expected top recommendation for every supported item and condition."""

import pytest
from app.data.loader import load_impact_factors, load_knowledge_base
from app.schemas.knowledge import ActionType, Condition
from app.services.ranking import rank_actions

KNOWLEDGE = load_knowledge_base()
FACTORS = load_impact_factors()

EXPECTED_TOP_ACTIONS = {
    "old_smartphone": {
        "working": "resale",
        "damaged": "repair",
        "dead": "authorized_disposal",
        "unknown": "authorized_disposal",
    },
    "computer_accessories": {
        "working": "reuse",
        "damaged": "repair",
        "dead": "authorized_disposal",
        "unknown": "authorized_disposal",
    },
    "household_battery": {condition: "hazardous_collection" for condition in Condition},
    "household_bulb": {
        "working": "reuse",
        "damaged": "hazardous_collection",
        "dead": "hazardous_collection",
        "unknown": "hazardous_collection",
    },
    "pet_bottle": {condition: "recycling" for condition in Condition},
    "glass_bottle": {
        "working": "reuse",
        "damaged": "recycling",
        "dead": "recycling",
        "unknown": "recycling",
    },
    "cardboard_box": {
        "working": "reuse",
        "damaged": "recycling",
        "dead": "recycling",
        "unknown": "recycling",
    },
    "paper": {
        "working": "reuse",
        "damaged": "compost",
        "dead": "compost",
        "unknown": "recycling",
    },
    "clothing": {
        "working": "reuse",
        "damaged": "repair",
        "dead": "recycling",
        "unknown": "recycling",
    },
    "food_scraps": {condition: "compost" for condition in Condition},
    "cooking_oil": {condition: "used_cooking_oil_collection" for condition in Condition},
    "medicine_strips": {condition: "medicine_takeback" for condition in Condition},
    "small_appliance": {
        "working": "reuse",
        "damaged": "repair",
        "dead": "authorized_disposal",
        "unknown": "authorized_disposal",
    },
    "furniture": {
        "working": "reuse",
        "damaged": "repair",
        "dead": "donate_refurbish",
        "unknown": "donate_refurbish",
    },
}


@pytest.mark.parametrize(
    ("item_id", "condition", "expected_action"),
    [
        (item_id, condition, expected)
        for item_id, conditions in EXPECTED_TOP_ACTIONS.items()
        for condition, expected in conditions.items()
    ],
)
def test_top_action_for_every_item_condition(
    item_id: str, condition: str, expected_action: str
) -> None:
    result = rank_actions(
        item_id,
        Condition(condition),
        KNOWLEDGE,
        FACTORS,
    )

    assert result.recommended_actions[0].action_type == ActionType(expected_action)
    assert result.recommended_actions[0].rank == 1


def test_active_battery_hazard_overrides_normal_phone_resale() -> None:
    result = rank_actions(
        "old_smartphone",
        Condition.WORKING,
        KNOWLEDGE,
        FACTORS,
        hazard_flags=["swollen_battery"],
    )

    assert result.recommended_actions[0].action_type == ActionType.AUTHORIZED_DISPOSAL
    assert result.recommended_actions[0].safety_warning is not None


def test_unknown_item_requests_confirmation_without_fabricated_estimates() -> None:
    result = rank_actions("unknown_item", Condition.UNKNOWN, KNOWLEDGE, FACTORS)

    assert result.needs_confirmation is True
    assert result.safe_guidance
    assert result.recommended_actions == []


def test_estimates_include_source_note_and_estimate_labels() -> None:
    result = rank_actions("old_smartphone", Condition.WORKING, KNOWLEDGE, FACTORS)
    primary_action = result.recommended_actions[0]

    assert primary_action.impact is not None
    assert primary_action.impact.is_estimate is True
    assert "Prototype assumption" in primary_action.impact.basis
    assert primary_action.estimated_value_inr is not None
    assert primary_action.estimated_value_inr.is_estimate is True
