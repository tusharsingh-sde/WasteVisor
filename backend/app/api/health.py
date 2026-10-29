"""Health endpoint."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Check WasteVisor backend status")
def health_check() -> HealthResponse:
    """Report app status and configured capabilities without exposing credentials."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        demo_mode=settings.demo_mode,
        model_available=bool(settings.bedrock_model_id),
        storage="sqlite",
    )
