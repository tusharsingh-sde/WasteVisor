"""Load and validate WasteVisor YAML knowledge and estimate factors."""

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

from app.schemas.knowledge import ImpactFactorTable, KnowledgeBase

DATA_DIRECTORY = Path(__file__).resolve().parent
ModelType = TypeVar("ModelType", bound=BaseModel)


def _load_yaml(path: Path, model: type[ModelType]) -> ModelType:
    """Parse one YAML file and validate it against its Pydantic model."""
    with path.open(encoding="utf-8") as data_file:
        raw_data = yaml.safe_load(data_file)
    return model.model_validate(raw_data)


def load_knowledge_base(path: Path | None = None) -> KnowledgeBase:
    """Load the configured item catalog and condition-specific action rules."""
    return _load_yaml(path or DATA_DIRECTORY / "knowledge_base.yaml", KnowledgeBase)


def load_impact_factors(path: Path | None = None) -> ImpactFactorTable:
    """Load documented, estimated impact and value factors."""
    return _load_yaml(path or DATA_DIRECTORY / "impact_factors.yaml", ImpactFactorTable)


def validate_data_pair(knowledge: KnowledgeBase, factors: ImpactFactorTable) -> None:
    """Ensure every catalog item has exactly one factor row and vice versa."""
    item_ids = set(knowledge.items)
    factor_ids = set(factors.factors)
    if item_ids != factor_ids:
        missing_factors = sorted(item_ids - factor_ids)
        unknown_factors = sorted(factor_ids - item_ids)
        raise ValueError(
            f"Knowledge/factor item IDs differ; missing factors={missing_factors}, "
            f"unknown factors={unknown_factors}"
        )


def load_startup_data() -> tuple[KnowledgeBase, ImpactFactorTable]:
    """Load both data files and validate their cross-file item identifiers."""
    knowledge = load_knowledge_base()
    factors = load_impact_factors()
    validate_data_pair(knowledge, factors)
    return knowledge, factors

