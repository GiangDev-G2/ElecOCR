"""Typed runtime configuration for the API process."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded once at the application boundary."""

    model_config = SettingsConfigDict(env_prefix="ELECOCR_", env_file=".env", extra="ignore")

    app_version: str = "0.1.0"
    model_version: str = "unavailable"
    frontend_origin: str = "http://127.0.0.1:5173"
    max_image_bytes: int = Field(default=12 * 1024 * 1024, ge=1)
    max_image_side_px: int = Field(default=8192, ge=1)
