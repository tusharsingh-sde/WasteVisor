"""Completed-action, history, and impact endpoints."""

from typing import cast

from fastapi import APIRouter, HTTPException, Query, Request

from app.schemas.errors import ErrorEnvelope
from app.schemas.history import (
    CompleteActionRequest,
    CompleteActionResponse,
    HistoryResponse,
    ImpactResponse,
)
from app.services.history import HistoryStore

router = APIRouter(tags=["tracking"])


@router.post(
    "/actions/complete",
    response_model=CompleteActionResponse,
    status_code=201,
    summary="Record a completed action",
    responses={404: {"model": ErrorEnvelope}, 422: {"model": ErrorEnvelope}},
)
def complete_action(
    body: CompleteActionRequest,
    request: Request,
) -> CompleteActionResponse:
    """Persist an eligible action and return updated estimate totals."""
    knowledge = request.app.state.knowledge_base
    if body.item not in knowledge.items:
        raise HTTPException(status_code=404, detail="The requested item is not supported.")
    try:
        store = cast(HistoryStore, request.app.state.history_store)
        return store.complete(
            item=body.item,
            condition=body.condition,
            action_type=body.action_type,
            completed_at=body.completed_at,
            recovered_value_inr=body.recovered_value_inr,
            knowledge=knowledge,
            factors=request.app.state.impact_factors,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="List completed actions",
    responses={422: {"model": ErrorEnvelope}},
)
def list_history(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> HistoryResponse:
    """Return completed actions ordered from newest to oldest."""
    store = cast(HistoryStore, request.app.state.history_store)
    return store.list_history(limit=limit, offset=offset)


@router.get("/impact", response_model=ImpactResponse, summary="Get estimated impact totals")
def get_impact(request: Request) -> ImpactResponse:
    """Aggregate all estimated metrics from persisted completed actions."""
    store = cast(HistoryStore, request.app.state.history_store)
    totals = store.get_totals()
    return ImpactResponse(
        **totals.model_dump(),
        basis=(
            "Totals are estimates calculated from documented WasteVisor factors "
            "and completed actions."
        ),
    )
