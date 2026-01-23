from functools import lru_cache
from typing import Any
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "TechHouse API"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "postgresql://techhouse:techhouse_password@db:5432/techhouse"
    database_echo: bool = False

    secret_key: str = "techhouse-development-secret-key-pdp-assignment-v1"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    api_prefix: str = "/api/v1"
    cors_origins: str = (
        "http://localhost:3000,http://localhost:8080"  # Store as string, parse in getter
    )

    default_skip: int = 0
    default_limit: int = 100

    model_config = ConfigDict(
        env_file=".env", case_sensitive=False, str_strip_whitespace=True, extra="ignore"
    )

    def get_cors_origins(self) -> list[str]:
        """Parse CORS_ORIGINS from comma-separated string."""
        if isinstance(self.cors_origins, str):
            if not self.cors_origins:
                return []
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins if self.cors_origins else []


@lru_cache
def get_settings() -> Settings:
    return Settings()
