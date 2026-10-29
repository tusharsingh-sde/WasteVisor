"""Health response schema."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Non-sensitive backend readiness information."""

    status: str
    demo_mode: bool
    model_available: bool
    storage: str

