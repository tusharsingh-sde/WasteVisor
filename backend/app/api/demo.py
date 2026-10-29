"""Offline demo sample listing endpoint."""

from fastapi import APIRouter, Request

from app.schemas.demo import DemoSample, DemoSamplesResponse

router = APIRouter(tags=["demo"])


@router.get("/demo/samples", response_model=DemoSamplesResponse, summary="List demo samples")
def list_demo_samples(request: Request) -> DemoSamplesResponse:
    """List cached item scenarios and local image URLs."""
    fixtures = request.app.state.demo_fixtures
    return DemoSamplesResponse(
        samples=[
            DemoSample(
                id=fixture.id,
                item=fixture.identification.item,
                label=fixture.label,
                image_url=f"/samples/{fixture.image_filename}",
            )
            for fixture in fixtures.values()
        ]
    )
