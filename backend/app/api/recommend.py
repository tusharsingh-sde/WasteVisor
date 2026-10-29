"""Ranked action recommendation endpoint."""

from fastapi import APIRouter, Request

from app.schemas.errors import ErrorEnvelope
from app.schemas.history import RecommendRequest
from app.schemas.recommendation import RecommendationResult
from app.services.ranking import rank_actions

router = APIRouter(tags=["recommend"])


@router.post(
    "/recommend",
    response_model=RecommendationResult,
    summary="Recommend the best next action",
    responses={422: {"model": ErrorEnvelope}},
)
def recommend(body: RecommendRequest, request: Request) -> RecommendationResult:
    """Rank actions using local rules for the confirmed item and condition."""
    return rank_actions(
        body.item,
        body.condition,
        request.app.state.knowledge_base,
        request.app.state.impact_factors,
    )
