"""WasteVisor FastAPI application factory."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.health import router as health_router
from app.core.config import get_settings
from app.schemas.errors import ErrorDetail, ErrorEnvelope

logger = logging.getLogger("wastevisor")


def create_app() -> FastAPI:
    """Build the API with WasteVisor metadata, CORS, and consistent error handlers."""
    settings = get_settings()
    application = FastAPI(
        title="WasteVisor API",
        summary="WasteVisor household waste-management advisor API",
        description=(
            "Know Before You Throw. Identify household waste and recommend its best next action."
        ),
        version="0.1.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @application.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code = {
            400: "bad_request",
            404: "not_found",
            413: "payload_too_large",
            422: "validation_error",
            503: "service_unavailable",
        }.get(exc.status_code, "request_error")
        message = (
            exc.detail
            if isinstance(exc.detail, str)
            else "The request could not be completed."
        )
        payload = ErrorEnvelope(error=ErrorDetail(code=code, message=message))
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, _exc: RequestValidationError
    ) -> JSONResponse:
        payload = ErrorEnvelope(
            error=ErrorDetail(
                code="validation_error",
                message="The request did not match the API schema.",
            )
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @application.exception_handler(Exception)
    async def unexpected_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled WasteVisor API error", exc_info=exc)
        payload = ErrorEnvelope(
            error=ErrorDetail(
                code="internal_error",
                message="WasteVisor could not complete the request.",
            )
        )
        return JSONResponse(status_code=500, content=payload.model_dump())

    application.include_router(health_router, prefix="/api")
    return application


app = create_app()

