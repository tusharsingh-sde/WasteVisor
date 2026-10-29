"""Consistent API error models."""

from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    """Machine-readable error code and safe user-facing message."""

    code: str
    message: str


class ErrorEnvelope(BaseModel):
    """Shared WasteVisor API error response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "not_found",
                    "message": "The requested resource was not found.",
                }
            }
        }
    )

    error: ErrorDetail
