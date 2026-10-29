"""Knowledge-base and documented factor validation tests."""

from app.data.loader import load_impact_factors, load_knowledge_base, validate_data_pair
from app.schemas.knowledge import Condition


def test_catalog_covers_supported_conditions_and_prioritized_rules() -> None:
    knowledge = load_knowledge_base()

    assert 12 <= len(knowledge.items) <= 15
    for item in knowledge.items.values():
        assert set(item.condition_rules) == set(Condition)
        for rule_set_name in item.condition_rules.values():
            rules = knowledge.rule_sets[rule_set_name]
            assert rules
            assert all(rule.reason_code for rule in rules)
            assert [rule.priority for rule in rules] == sorted(rule.priority for rule in rules)


def test_every_catalog_item_has_documented_estimate_factors() -> None:
    knowledge = load_knowledge_base()
    factors = load_impact_factors()

    validate_data_pair(knowledge, factors)
    assert set(knowledge.items) == set(factors.factors)
    assert all(factor.source_note for factor in factors.factors.values())
