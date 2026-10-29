"""Environment-backed WasteVisor backend settings."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from the environment and optional backend/.env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "WasteVisor"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = ""
    demo_mode: bool = True
    database_url: str = "sqlite:///./wastevisor.db"
    db_path: str = "./wastevisor.db"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    vision_max_retries: int = Field(default=1, ge=0, le=1)
    max_upload_size_bytes: int = Field(default=10 * 1024 * 1024, gt=0)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached process settings."""
    return Settings()
