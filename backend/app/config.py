"""
Configuration management for the Time Tracker application.
Loads environment variables and provides app settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str

    @property
    def async_database_url(self) -> str:
        """Convert database URL to async format (postgresql+asyncpg)."""
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str

    # FastAPI
    environment: str = "development"
    debug: bool = True

    # CORS
    cors_origins: str = "http://localhost:8080"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()
