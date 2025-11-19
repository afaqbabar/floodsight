"""Database models."""
from datetime import datetime, timezone
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
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
    acknowledgments: Mapped[list["AlertAcknowledgment"]] = relationship(
        "AlertAcknowledgment", back_populates="alert", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Alert(station_id={self.station_id}, level={self.level}, issued={self.issued_at})>"


class User(Base):
    """User account for subscriptions and notifications."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Notification preferences (JSON)
    # Example: {"email": true, "sms": false, "push": true, "min_level": "warning"}
    notification_preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Push notification tokens
    push_tokens: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
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
    subscriptions: Mapped[list["UserSubscription"]] = relationship(
        "UserSubscription", back_populates="user", cascade="all, delete-orphan"
    )
    acknowledgments: Mapped[list["AlertAcknowledgment"]] = relationship(
        "AlertAcknowledgment", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(email={self.email}, name={self.name})>"


class UserSubscription(Base):
    """User subscription to specific stations."""

    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Minimum alert level to notify (info, warning, severe, extreme)
    min_alert_level: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    station: Mapped["Station"] = relationship("Station")

    def __repr__(self) -> str:
        return f"<UserSubscription(user_id={self.user_id}, station_id={self.station_id})>"


class AlertRule(Base):
    """Custom alert rules for stations."""

    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Rule type: "threshold", "rate_of_rise", "time_window", "multi_station"
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Rule configuration (JSON)
    # Examples:
    # - threshold: {"info": 500, "warning": 800, "severe": 1200, "extreme": 1500}
    # - rate_of_rise: {"threshold_m3s_per_hour": 50, "level": "warning"}
    # - time_window: {"start_hour": 22, "end_hour": 6, "level_boost": 1}
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # Higher = applied first
    
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
    station: Mapped["Station"] = relationship("Station")

    def __repr__(self) -> str:
        return f"<AlertRule(station_id={self.station_id}, type={self.rule_type}, name={self.name})>"


class Webhook(Base):
    """Webhook configuration for alert notifications."""

    __tablename__ = "webhooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Webhook type: "generic", "slack", "discord", "telegram", "teams"
    webhook_type: Mapped[str] = mapped_column(String(50), default="generic", nullable=False)
    
    # Minimum alert level to trigger (info, warning, severe, extreme)
    min_alert_level: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)
    
    # Optional: filter by station IDs (JSON array)
    station_filter: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Headers (JSON)
    headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Retry configuration
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    retry_delay_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
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
    delivery_logs: Mapped[list["WebhookDelivery"]] = relationship(
        "WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Webhook(name={self.name}, type={self.webhook_type})>"


class WebhookDelivery(Base):
    """Webhook delivery log."""

    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    webhook_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Delivery status: "pending", "success", "failed", "retrying"
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Response info
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Retry tracking
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    webhook: Mapped["Webhook"] = relationship("Webhook", back_populates="delivery_logs")
    alert: Mapped["Alert"] = relationship("Alert")

    def __repr__(self) -> str:
        return f"<WebhookDelivery(webhook_id={self.webhook_id}, alert_id={self.alert_id}, status={self.status})>"


class AlertAcknowledgment(Base):
    """Alert acknowledgment tracking."""

    __tablename__ = "alert_acknowledgments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    acknowledged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Optional: notes from user
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Action taken: "acknowledged", "dismissed", "resolved", "escalated"
    action: Mapped[str] = mapped_column(String(50), default="acknowledged", nullable=False)

    # Relationships
    alert: Mapped["Alert"] = relationship("Alert", back_populates="acknowledgments")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="acknowledgments")

    def __repr__(self) -> str:
        return f"<AlertAcknowledgment(alert_id={self.alert_id}, user_id={self.user_id}, action={self.action})>"


class NotificationLog(Base):
    """Notification delivery log for tracking all notification attempts."""

    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Notification type: "email", "sms", "push", "webhook"
    notification_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Recipient (email/phone/device_token)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Delivery status: "sent", "failed", "pending"
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Error details if failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Provider info (e.g., "sendgrid", "twilio", "firebase")
    provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    alert: Mapped["Alert"] = relationship("Alert")
    user: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return f"<NotificationLog(alert_id={self.alert_id}, type={self.notification_type}, status={self.status})>"


class VesselDetection(Base):
    """SAR vessel detection from Sentinel-1 for maritime/dark-vessel monitoring."""

    __tablename__ = "vessel_detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Geospatial point (lon, lat)
    geom = mapped_column(Geometry('POINT', srid=4326), nullable=False, index=True)
    
    # Sentinel-1 scene metadata
    scene_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    detection_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    
    # Detection metrics
    intensity_db: Mapped[float] = mapped_column(Float, nullable=False)  # Sigma0 VV in dB
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # CFAR ratio or ML confidence
    
    # Optional: vessel characteristics (if using advanced detectors)
    vessel_length_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vessel_heading_deg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Maritime context flags
    in_river_mouth: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    in_port_zone: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    near_flood_plume: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Detection source: "cfar", "sarfish", "sumo", "custom_cnn"
    detector_type: Mapped[str] = mapped_column(String(50), default="cfar", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<VesselDetection(scene_id={self.scene_id}, time={self.detection_time}, confidence={self.confidence})>"

