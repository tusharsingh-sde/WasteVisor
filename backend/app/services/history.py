"""SQLite persistence for completed WasteVisor actions and derived totals."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import Float, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from app.schemas.history import (
    CompleteActionResponse,
    EstimateMetric,
    HistoryEntry,
    HistoryResponse,
    ImpactTotals,
    StoredImpact,
)
from app.schemas.knowledge import ActionType, Condition, ImpactFactorTable, KnowledgeBase


class Base(DeclarativeBase):
    """Base metadata for the WasteVisor local SQLite store."""


class CompletedActionRecord(Base):
    """Persisted user-completed action with server-derived impact estimates."""

    __tablename__ = "completed_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    item: Mapped[str] = mapped_column(String(100), index=True)
    condition: Mapped[str] = mapped_column(String(20))
    action_type: Mapped[str] = mapped_column(String(50))
    completed_at: Mapped[datetime] = mapped_column(index=True)
    kg_diverted: Mapped[float] = mapped_column(Float)
    co2e_saved_kg: Mapped[float] = mapped_column(Float)
    recovered_value_inr: Mapped[float] = mapped_column(Float)


class HistoryStore:
    """Small synchronous SQLite repository used by the prototype API."""

    def __init__(self, database_url: str) -> None:
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        if database_url.startswith("sqlite:///") and ":memory:" not in database_url:
            database_path = Path(database_url.removeprefix("sqlite:///"))
            if not database_path.is_absolute():
                database_path = Path.cwd() / database_path
            database_path.parent.mkdir(parents=True, exist_ok=True)
        pool = StaticPool if ":memory:" in database_url else None
        self.engine = create_engine(
            database_url,
            connect_args=connect_args,
            poolclass=pool,
        )
        self.session_factory = sessionmaker(self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

    def complete(
        self,
        item: str,
        condition: Condition,
        action_type: ActionType,
        completed_at: datetime | None,
        recovered_value_inr: float | None,
        knowledge: KnowledgeBase,
        factors: ImpactFactorTable,
    ) -> CompleteActionResponse:
        """Persist an eligible action and return its receipt and updated totals."""
        item_definition = knowledge.items[item]
        rule_set = knowledge.rule_sets[item_definition.condition_rules[condition]]
        if action_type not in {rule.action for rule in rule_set}:
            raise ValueError("The selected action is not eligible for this item and condition.")

        factor = factors.factors[item]
        timestamp = completed_at or datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        record = CompletedActionRecord(
            id=str(uuid4()),
            item=item,
            condition=condition.value,
            action_type=action_type.value,
            completed_at=timestamp,
            kg_diverted=factor.kg_diverted,
            co2e_saved_kg=factor.co2e_saved_kg,
            recovered_value_inr=recovered_value_inr or 0.0,
        )
        with self.session_factory() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            history_entry = self._to_history_entry(record)
        return CompleteActionResponse(history_entry=history_entry, totals=self.get_totals())

    def list_history(self, limit: int, offset: int) -> HistoryResponse:
        """Return latest completed actions in bounded pages."""
        with self.session_factory() as session:
            total = session.scalar(select(func.count()).select_from(CompletedActionRecord)) or 0
            records = session.scalars(
                select(CompletedActionRecord)
                .order_by(CompletedActionRecord.completed_at.desc())
                .limit(limit)
                .offset(offset)
            ).all()
        return HistoryResponse(
            items=[self._to_history_entry(record) for record in records],
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_totals(self) -> ImpactTotals:
        """Aggregate estimates exclusively from stored completed action records."""
        with self.session_factory() as session:
            row = session.execute(
                select(
                    func.coalesce(func.sum(CompletedActionRecord.kg_diverted), 0.0),
                    func.coalesce(func.sum(CompletedActionRecord.co2e_saved_kg), 0.0),
                    func.coalesce(func.sum(CompletedActionRecord.recovered_value_inr), 0.0),
                )
            ).one()
        return ImpactTotals(
            kg_diverted=EstimateMetric(value=round(float(row[0]), 3)),
            co2e_saved_kg=EstimateMetric(value=round(float(row[1]), 3)),
            recovered_value_inr=EstimateMetric(value=round(float(row[2]), 2)),
        )

    @staticmethod
    def _to_history_entry(record: CompletedActionRecord) -> HistoryEntry:
        """Convert a database row into the public typed response."""
        return HistoryEntry(
            id=record.id,
            item=record.item,
            condition=Condition(record.condition),
            action_type=ActionType(record.action_type),
            completed_at=record.completed_at,
            impact=StoredImpact(
                kg_diverted=record.kg_diverted,
                co2e_saved_kg=record.co2e_saved_kg,
                is_estimate=True,
            ),
            recovered_value_inr=EstimateMetric(value=record.recovered_value_inr),
        )
