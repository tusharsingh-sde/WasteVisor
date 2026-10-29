"""Rules-based WasteVisor next-action ranking and template explanations."""

from app.schemas.knowledge import (
    ActionRule,
    ActionType,
    Condition,
    ImpactFactorTable,
    KnowledgeBase,
)
from app.schemas.recommendation import RecommendationResult, RecommendedAction
from app.services.impact import estimate_item_impact, estimate_item_value

ACTION_COPY: dict[ActionType, tuple[list[str], list[str]]] = {
    ActionType.REUSE: (
        ["Keep the item for another use or pass it to someone who can use it."],
        ["Check that it is clean and safe to use."],
    ),
    ActionType.RESALE: (
        [
            "Check the item's condition and remove personal data where relevant.",
            "Compare offers on a resale platform you already trust.",
        ],
        ["Photograph the item honestly.", "Disclose defects and included accessories."],
    ),
    ActionType.REPAIR: (
        [
            "Check whether repair is safe and practical.",
            "Compare repair cost with the item's remaining usefulness.",
        ],
        [
            "Unplug or power down the item.",
            "Do not open a battery or mains-powered device unless qualified.",
        ],
    ),
    ActionType.DONATE_REFURBISH: (
        ["Offer the clean, usable item to a person or organization that accepts it."],
        ["Clean the item.", "Confirm acceptance and condition requirements before travelling."],
    ),
    ActionType.COMPOST: (
        ["Add suitable organic material to a managed home or community compost system."],
        [
            "Separate non-compostable packaging.",
            "Follow the compost system's accepted-material guidance.",
        ],
    ),
    ActionType.RECYCLING: (
        [
            "Keep the material clean and dry where appropriate.",
            "Check that the local collection accepts this material.",
        ],
        [
            "Separate components when safe.",
            "Verify local acceptance before placing it for collection.",
        ],
    ),
    ActionType.AUTHORIZED_DISPOSAL: (
        [
            "Keep the item out of mixed household waste.",
            "Use an authorized e-waste or bulky-waste collection route.",
        ],
        ["Store safely until handoff.", "Do not dismantle hazardous components."],
    ),
    ActionType.HAZARDOUS_COLLECTION: (
        [
            "Keep the item separate from household waste.",
            "Use an appropriate authorized special-waste collection point.",
        ],
        [
            "Avoid opening, crushing, or mixing it with other waste.",
            "Check local collection instructions.",
        ],
    ),
    ActionType.USED_COOKING_OIL_COLLECTION: (
        [
            "Let the oil cool and place it in a sealed container.",
            "Ask the municipality or a verified collector about accepted drop-off.",
        ],
        [
            "Do not pour oil into a sink, drain, or soil.",
            "Do not store hot oil in a sealed container.",
        ],
    ),
    ActionType.MEDICINE_TAKEBACK: (
        [
            "Keep medicine separate from household recycling.",
            "Ask a pharmacy or local authority about authorized take-back.",
        ],
        [
            "Keep it in its packaging where safe.",
            "Do not flush medicine unless official instructions specifically say so.",
        ],
    ),
}

REASON_COPY = {
    "WORKING_DEVICE_VALUE_RECOVERY": "A working device may remain useful and recover value.",
    "EXTEND_USEFUL_LIFE": "Keeping a usable item in use avoids replacing it prematurely.",
    "MATERIAL_RECOVERY": "Material recovery is the next option when direct reuse is not suitable.",
    "COMPOST_ORGANIC_MATERIAL": "Suitable food scraps can become a useful compost input.",
    "SPECIAL_HANDLING_REQUIRED": (
        "This item needs separate handling to reduce safety and pollution risks."
    ),
    "AUTHORIZED_E_WASTE_REQUIRED": (
        "A dead electronic item should go through an authorized e-waste route."
    ),
    "NEVER_POUR_OIL_IN_DRAIN": (
        "Keeping used oil out of drains prevents avoidable blockages and pollution."
    ),
    "AUTHORIZED_MEDICINE_HANDLING": (
        "Medicine needs a take-back route rather than ordinary recycling."
    ),
}

ACTIVE_HAZARD_ACTIONS: dict[str, ActionType] = {
    "swollen_battery": ActionType.AUTHORIZED_DISPOSAL,
    "damaged_battery": ActionType.AUTHORIZED_DISPOSAL,
    "leaking": ActionType.HAZARDOUS_COLLECTION,
    "exposed_wires": ActionType.AUTHORIZED_DISPOSAL,
    "mercury": ActionType.HAZARDOUS_COLLECTION,
    "broken_glass": ActionType.HAZARDOUS_COLLECTION,
    "pharmaceutical": ActionType.MEDICINE_TAKEBACK,
    "hot_liquid": ActionType.USED_COOKING_OIL_COLLECTION,
}

HAZARD_WARNINGS: dict[str, str] = {
    "swollen_battery": "Do not charge, puncture, compress, or place the device in household waste.",
    "damaged_battery": "Do not charge or dismantle the damaged battery; keep it away from heat.",
    "leaking": (
        "Avoid direct contact; keep the leaking item separate and seek "
        "local hazardous-waste guidance."
    ),
    "exposed_wires": (
        "Do not plug in or handle exposed wiring; keep the item away from children and moisture."
    ),
    "mercury": (
        "Do not break the bulb. If broken, avoid contact and follow local hazardous-waste guidance."
    ),
    "broken_glass": (
        "Do not handle shards with bare hands; package safely before an accepted collection route."
    ),
    "pharmaceutical": (
        "Keep medicines away from children; do not flush unless official guidance instructs it."
    ),
    "hot_liquid": "Allow the oil to cool fully before handling or storing it.",
}


def _safe_override_action(item_id: str, action: ActionType, knowledge: KnowledgeBase) -> ActionType:
    """Choose a documented safe action when a detected hazard overrides normal ranking."""
    item = knowledge.items[item_id]
    allowed_actions = set(ActionType)
    if action == ActionType.AUTHORIZED_DISPOSAL and item.category == "hazardous":
        return ActionType.HAZARDOUS_COLLECTION
    if action not in allowed_actions:
        return ActionType.AUTHORIZED_DISPOSAL
    return action


def rank_actions(
    item_id: str,
    condition: Condition,
    knowledge: KnowledgeBase,
    factors: ImpactFactorTable,
    hazard_flags: list[str] | None = None,
) -> RecommendationResult:
    """Rank eligible actions from the local rules; never ask an LLM to choose them."""
    hazards = set(hazard_flags or [])
    if item_id not in knowledge.items:
        return RecommendationResult(
            item=item_id,
            condition=condition.value,
            needs_confirmation=True,
            safe_guidance=(
                "Keep the item separate until its materials and hazards are confirmed. "
                "Do not place batteries, chemicals, medicines, or electronics in mixed waste."
            ),
            recommended_actions=[],
        )

    item = knowledge.items[item_id]
    rule_set_name = item.condition_rules[condition]
    rules = list(knowledge.rule_sets[rule_set_name])
    active_hazards = sorted(hazards.intersection(ACTIVE_HAZARD_ACTIONS))

    if active_hazards:
        override = _safe_override_action(
            item_id,
            ACTIVE_HAZARD_ACTIONS[active_hazards[0]],
            knowledge,
        )
        rules = [
            ActionRule(
                action=override,
                priority=1,
                reason_code="ACTIVE_HAZARD_SAFE_HANDLING",
            )
        ]

    factor = factors.factors[item_id]
    recommended = [
        RecommendedAction(
            action_type=rule.action,
            rank=rank,
            why_best=REASON_COPY.get(
                rule.reason_code,
                (
                    "This is the recommended next step for this item's condition "
                    f"({rule.reason_code.lower().replace('_', ' ')})."
                ),
            ),
            reason_codes=[rule.reason_code],
            effort_minutes=factor.effort_minutes,
            estimated_value_inr=estimate_item_value(factor),
            impact=estimate_item_impact(factor),
            next_steps=ACTION_COPY[rule.action][0],
            preparation_checklist=ACTION_COPY[rule.action][1],
            safety_warning=next(
                (HAZARD_WARNINGS[flag] for flag in active_hazards if flag in HAZARD_WARNINGS),
                None,
            ),
        )
        for rank, rule in enumerate(sorted(rules, key=lambda entry: entry.priority), start=1)
    ]
    return RecommendationResult(
        item=item_id,
        condition=condition.value,
        needs_confirmation=condition == Condition.UNKNOWN,
        recommended_actions=recommended,
    )
