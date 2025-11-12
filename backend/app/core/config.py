"""Application configuration."""
import json
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "FloodSight API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API
    API_V1_PREFIX: str = "/v1"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://192.168.178.50:5173",  # Local network access
        "https://floodsight.vercel.app",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return json.loads(v)
        return v

    @field_validator("GLOFAS_LEADTIMES", mode="before")
    @classmethod
    def parse_glofas_leadtimes(cls, v: str | List[int]) -> List[int]:
        """Parse lead times from JSON string or comma separated values."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
            except json.JSONDecodeError:
                parsed = [int(item.strip()) for item in v.split(",") if item.strip()]
            return parsed
        return v

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/floodsight"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_JWKS_URL: str = ""

    # Prefect
    PREFECT_API_URL: str = "http://localhost:4200"

    # Metrics
    METRICS_ENABLED: bool = True

    # GloFAS / ECMWF Copernicus Data Store
    GLOFAS_INGEST_MODE: str = "auto"  # Options: auto, real, fake
    CDS_API_URL: str = "https://cds.climate.copernicus.eu/api/v2"
    CDS_API_KEY: str = ""
    CDS_API_EMAIL: str = ""
    CDS_API_VERIFY: bool = True
    CDS_API_TIMEOUT: int = 900  # seconds
    GLOFAS_SYSTEM_VERSION: str = "version_4_0"
    GLOFAS_PRODUCT_TYPE: str = "control_forecast"
    GLOFAS_VARIABLE: str = "river_discharge_in_the_last_6_hours"
    GLOFAS_LEADTIMES: List[int] = [
        6,
        12,
        18,
        24,
        30,
        36,
        42,
        48,
        54,
        60,
        66,
        72,
        78,
        84,
        90,
        96,
        102,
        108,
        114,
        120,
    ]
    GLOFAS_BUFFER_DEGREES: float = 1.5
    GLOFAS_MAX_RECORDS_PER_STATION: int = 120
    GLOFAS_RUN_LAG_HOURS: int = 6

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

