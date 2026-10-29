"""Validated models for WasteVisor catalog, ranking rules, and estimate factors."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Condition(StrEnum):
    """Supported item condition values."""

    WORKING = "working"
    DAMAGED = "damaged"
    DEAD = "dead"
    UNKNOWN = "unknown"


class ActionType(StrEnum):
    """Actions WasteVisor can recommend."""

    REUSE = "reuse"
    RESALE = "resale"
    REPAIR = "repair"
    DONATE_REFURBISH = "donate_refurbish"
    COMPOST = "compost"
    RECYCLING = "recycling"
    AUTHORIZED_DISPOSAL = "authorized_disposal"
    HAZARDOUS_COLLECTION = "hazardous_collection"
    USED_COOKING_OIL_COLLECTION = "used_cooking_oil_collection"
    MEDICINE_TAKEBACK = "medicine_takeback"


class ActionDefinition(BaseModel):
    """User-facing label for an action type."""

    label: str = Field(min_length=1)


class ActionRule(BaseModel):
    """One eligible action with explicit rank and a stable explanation reason code."""

    action: ActionType
    priority: int = Field(ge=1)
    reason_code: str = Field(min_length=1)


class ItemDefinition(BaseModel):
    """Supported item metadata and condition-specific action eligibility."""

    display_name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    variants: list[str] = Field(min_length=1)
    hazard_flags: list[str]
    condition_rules: dict[Condition, str]

    @model_validator(mode="after")
    def all_conditions_have_rules(self) -> "ItemDefinition":
        missing = set(Condition) - set(self.condition_rules)
        if missing:
            raise ValueError(
                f"Condition rules missing for: {sorted(item.value for item in missing)}"
            )
        return self


class KnowledgeBase(BaseModel):
    """Whole validated WasteVisor decision knowledge base."""

    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    actions: dict[ActionType, ActionDefinition]
    rule_sets: dict[str, list[ActionRule]]
    items: dict[str, ItemDefinition] = Field(min_length=12, max_length=15)

    @model_validator(mode="after")
    def rules_only_reference_defined_actions(self) -> "KnowledgeBase":
        missing = {
            action
            for item in self.items.values()
            for rule_set_name in item.condition_rules.values()
            for rule in self.rule_sets.get(rule_set_name, [])
            for action in [rule.action]
            if action not in self.actions
        }
        if missing:
            raise ValueError(
                f"Action definitions missing: {sorted(action.value for action in missing)}"
            )
        unknown_rule_sets = {
            rule_set
            for item in self.items.values()
            for rule_set in item.condition_rules.values()
            if rule_set not in self.rule_sets
        }
        if unknown_rule_sets:
            raise ValueError(f"Unknown rule sets: {sorted(unknown_rule_sets)}")
        for name, rules in self.rule_sets.items():
            priorities = [rule.priority for rule in rules]
            if not rules or len(priorities) != len(set(priorities)):
                raise ValueError(f"Rule set {name} must have rules with unique priorities")
        return self


class ValueRange(BaseModel):
    """Estimated value interval in INR."""

    min: float = Field(ge=0)
    max: float = Field(ge=0)

    @model_validator(mode="after")
    def maximum_not_below_minimum(self) -> "ValueRange":
        if self.max < self.min:
            raise ValueError("estimated value max must be greater than or equal to min")
        return self


class ImpactFactor(BaseModel):
    """Documented, explicitly estimated impact/value factors for one item."""

    model_config = ConfigDict(extra="forbid")

    kg_diverted: float = Field(ge=0)
    co2e_saved_kg: float = Field(ge=0)
    estimated_value_inr: ValueRange
    effort_minutes: int = Field(ge=0)
    source_note: str = Field(min_length=20)


class ImpactFactorTable(BaseModel):
    """Whole validated estimate factor table."""

    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    currency: str = Field(pattern="^INR$")
    method_note: str = Field(min_length=20)
    factors: dict[str, ImpactFactor] = Field(min_length=12, max_length=15)
