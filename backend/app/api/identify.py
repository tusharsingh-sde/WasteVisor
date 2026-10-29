"""Image identification endpoint."""

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from app.schemas.errors import ErrorEnvelope
from app.schemas.identification import DemoMetadata, IdentifyResponse
from app.services.vision import SUPPORTED_MEDIA_TYPES, identify_image

router = APIRouter(tags=["identify"])


@router.post(
    "/identify",
    response_model=IdentifyResponse,
    summary="Identify a waste item from a photo",
    responses={
        400: {"model": ErrorEnvelope},
        413: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
async def identify(
    request: Request,
    image: UploadFile = File(...),  # noqa: B008
    sample_id: str | None = Form(default=None),
) -> IdentifyResponse:
    """Identify a supported uploaded image, safely falling back if Bedrock is unavailable."""
    content_type = image.content_type or ""
    if content_type not in SUPPORTED_MEDIA_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Upload a JPEG, PNG, or WebP image.",
        )
    settings = request.app.state.settings
    image_bytes = await image.read(settings.max_upload_size_bytes + 1)
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(image_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(status_code=413, detail="The image exceeds the 5 MB upload limit.")

    identification = identify_image(
        image_bytes,
        content_type,
        request.app.state.knowledge_base,
        model_id=settings.bedrock_model_id,
        aws_region=settings.aws_region,
    )
    return IdentifyResponse(
        identification=identification,
        demo=DemoMetadata(is_demo=False, sample_id=sample_id),
    )
