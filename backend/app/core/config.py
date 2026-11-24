"""Environment-backed application settings."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Settings shared by the API, database, and authentication layer."""

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./c9_draft_scout.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "local-development-secret-change-me")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    )
    jwt_algorithm: str = "HS256"


settings = Settings()