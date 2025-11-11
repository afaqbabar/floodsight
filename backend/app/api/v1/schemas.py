"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Station schemas
class StationBase(BaseModel):
    """Base station schema."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    river_basin: Optional[str] = Field(None, max_length=100)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class StationCreate(StationBase):
    """Schema for creating a station."""
    pass


class StationResponse(StationBase):
    """Schema for station response."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Forecast schemas
class ForecastBase(BaseModel):
    """Base forecast schema."""
    station_id: int
    ts: datetime
    lead_hours: int = Field(..., ge=0)
    discharge_m3s: float = Field(..., ge=0)
    water_level_m: Optional[float] = Field(None, ge=0)
    return_period_years: Optional[int] = Field(None, ge=1)
    source: str = Field(default="GloFAS", max_length=50)
    model_run: Optional[datetime] = None


class ForecastCreate(ForecastBase):
    """Schema for creating a forecast."""
    pass


class ForecastResponse(ForecastBase):
    """Schema for forecast response."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Alert schemas
class AlertBase(BaseModel):
    """Base alert schema."""
    station_id: int
    level: str = Field(..., pattern="^(info|warning|severe|extreme)$")
    probability: Optional[float] = Field(None, ge=0, le=1)
    message: str = Field(..., min_length=1)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class AlertCreate(AlertBase):
    """Schema for creating an alert."""
    pass


class AlertResponse(AlertBase):
    """Schema for alert response."""
    id: int
    issued_at: datetime
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Health schema
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    app: str
    version: str
    environment: str
    database: str = "connected"

