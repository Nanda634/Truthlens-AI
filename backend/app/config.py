"""
Central application configuration.

TruthLens AI uses Neon PostgreSQL as its database.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "TruthLens AI"

    # Neon PostgreSQL
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # Storage
    UPLOAD_DIR: str = "./storage/uploads"
    TEMP_DIR: str = "./storage/tmp"
    REPORT_DIR: str = "./storage/reports"

    MAX_FILE_SIZE: int = 200 * 1024 * 1024

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI model paths
    MODEL_IMAGE_PATH: str = ""
    MODEL_VIDEO_PATH: str = ""
    MODEL_AUDIO_PATH: str = ""

    RETENTION_DAYS: int = 30

    CORS_ORIGINS: str = "http://localhost:5173"

    # Confidence model weights
    WEIGHT_METADATA: float = 0.10
    WEIGHT_FORENSIC: float = 0.25
    WEIGHT_ML: float = 0.40
    WEIGHT_STRUCTURAL: float = 0.15
    WEIGHT_CONSISTENCY: float = 0.10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Create required storage directories
for directory in (
    settings.UPLOAD_DIR,
    settings.TEMP_DIR,
    settings.REPORT_DIR,
):
    os.makedirs(directory, exist_ok=True)