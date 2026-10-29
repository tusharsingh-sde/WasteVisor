"""Validated demo fixture and sample catalog schemas."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.identification import Identification


class DemoFixture(BaseModel):
    """One image, label, and cached identification for an offline scenario."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    image_filename: str = Field(min_length=1)
    identification: Identification


class DemoSample(BaseModel):
    """Sample option exposed to the future frontend."""

    id: str
    item: str
    label: str
    image_url: str


class DemoSamplesResponse(BaseModel):
    """Available one-tap demo item choices."""

    samples: list[DemoSample]
