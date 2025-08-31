"""Core configuration module for Aetheria API."""

import os
from functools import lru_cache
from typing import Literal

import pytz
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database
    database_url: str = "postgresql://user:pass@localhost/aetheria"
    
    # Application
    app_env: Literal["dev", "prod"] = "dev"
    log_level: str = "INFO"
    api_key: str = "dev-api-key"
    
    # Timezone
    timezone: str = "Asia/Kolkata"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """Validate APP_ENV values."""
        if v not in ("dev", "prod"):
            raise ValueError("APP_ENV must be either 'dev' or 'prod'")
        return v
    
    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate timezone string."""
        try:
            pytz.timezone(v)
        except pytz.UnknownTimeZoneError:
            raise ValueError(f"Invalid timezone: {v}")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "prod"
    
    @property
    def tz(self) -> pytz.BaseTzInfo:
        """Get timezone object."""
        return pytz.timezone(self.timezone)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
