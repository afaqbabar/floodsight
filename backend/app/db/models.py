"""Database models."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Station(Base):
    """Hydrological monitoring station."""

    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    river_basin: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Geographic coordinates
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    forecasts: Mapped[list["Forecast"]] = relationship(
        "Forecast", back_populates="station", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(
        "Alert", back_populates="station", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Station(code={self.code}, name={self.name})>"


class Forecast(Base):
    """Flood discharge forecast."""

    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Forecast metadata
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )  # Forecast timestamp
    lead_hours: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # Lead time in hours (e.g., 6, 12, 24, 48, 72)
    
    # Forecast data
    discharge_m3s: Mapped[float] = mapped_column(Float, nullable=False)  # m³/s
    
    # Optional: additional forecast parameters
    water_level_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    return_period_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Metadata
    source: Mapped[str] = mapped_column(
        String(50), default="GloFAS", nullable=False
    )  # e.g., "GloFAS", "EFAS"
    model_run: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # When the model was run
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    station: Mapped["Station"] = relationship("Station", back_populates="forecasts")

    def __repr__(self) -> str:
        return f"<Forecast(station_id={self.station_id}, ts={self.ts}, lead={self.lead_hours}h, discharge={self.discharge_m3s})>"


class Alert(Base):
    """Flood alert/warning."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Alert metadata
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    
    # Alert level: "info", "warning", "severe", "extreme"
    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Probability (0.0 - 1.0)
    probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Alert message
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Optional: valid time range
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Whether the alert is still active
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    station: Mapped["Station"] = relationship("Station", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert(station_id={self.station_id}, level={self.level}, issued={self.issued_at})>"

