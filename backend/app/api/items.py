"""Supported WasteVisor item catalog endpoint."""

from fastapi import APIRouter, Request

from app.schemas.history import CatalogItem, ItemsResponse
from app.schemas.knowledge import Condition

router = APIRouter(tags=["items"])


@router.get("/items", response_model=ItemsResponse, summary="List supported waste items")
def list_items(request: Request) -> ItemsResponse:
    """List catalog items and the conditions accepted for frontend confirmation."""
    knowledge = request.app.state.knowledge_base
    return ItemsResponse(
        items=[
            CatalogItem(
                id=item_id,
                display_name=item.display_name,
                category=item.category,
                conditions=list(Condition),
                hazard_flags=item.hazard_flags,
            )
            for item_id, item in knowledge.items.items()
        ]
    )
