"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional, Dict, List, Any

from pydantic import BaseModel, Field, ConfigDict, EmailStr


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
    uptime_seconds: float = 0.0
    memory_mb: float = 0.0
    cpu_percent: float = 0.0


# Telemetry schemas
class TelemetryEvent(BaseModel):
    """Frontend telemetry event."""
    event_name: str
    timestamp: str
    page: str
    user_agent: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class TelemetryResponse(BaseModel):
    """Telemetry submission response."""
    status: str = "ok"
    message: str = "Event received"


# User schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    notification_preferences: Optional[Dict[str, Any]] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: Optional[str] = None
    phone: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# User Subscription schemas
class SubscriptionBase(BaseModel):
    """Base subscription schema."""
    station_id: int
    min_alert_level: str = Field(default="warning", pattern="^(info|warning|severe|extreme)$")


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a subscription."""
    user_id: int


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription."""
    min_alert_level: Optional[str] = Field(None, pattern="^(info|warning|severe|extreme)$")
    is_active: Optional[bool] = None


class SubscriptionResponse(SubscriptionBase):
    """Schema for subscription response."""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Alert Rule schemas
class AlertRuleBase(BaseModel):
    """Base alert rule schema."""
    station_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    rule_type: str = Field(..., pattern="^(threshold|rate_of_rise|time_window|multi_station)$")
    config: Dict[str, Any]
    priority: int = Field(default=100, ge=1, le=1000)


class AlertRuleCreate(AlertRuleBase):
    """Schema for creating an alert rule."""
    pass


class AlertRuleUpdate(BaseModel):
    """Schema for updating an alert rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=1000)


class AlertRuleResponse(AlertRuleBase):
    """Schema for alert rule response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Webhook schemas
class WebhookBase(BaseModel):
    """Base webhook schema."""
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=500)
    webhook_type: str = Field(default="generic", pattern="^(generic|slack|discord|telegram|teams)$")
    min_alert_level: str = Field(default="warning", pattern="^(info|warning|severe|extreme)$")
    station_filter: Optional[List[int]] = None
    headers: Optional[Dict[str, str]] = None
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=60, ge=10, le=3600)


class WebhookCreate(WebhookBase):
    """Schema for creating a webhook."""
    pass


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    webhook_type: Optional[str] = Field(None, pattern="^(generic|slack|discord|telegram|teams)$")
    min_alert_level: Optional[str] = Field(None, pattern="^(info|warning|severe|extreme)$")
    station_filter: Optional[List[int]] = None
    headers: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    retry_delay_seconds: Optional[int] = Field(None, ge=10, le=3600)


class WebhookResponse(WebhookBase):
    """Schema for webhook response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookDeliveryResponse(BaseModel):
    """Schema for webhook delivery response."""
    id: int
    webhook_id: int
    alert_id: int
    status: str
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    attempt_number: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Alert Acknowledgment schemas
class AlertAcknowledgmentCreate(BaseModel):
    """Schema for creating an alert acknowledgment."""
    alert_id: int
    user_id: Optional[int] = None
    notes: Optional[str] = None
    action: str = Field(default="acknowledged", pattern="^(acknowledged|dismissed|resolved|escalated)$")


class AlertAcknowledgmentResponse(BaseModel):
    """Schema for alert acknowledgment response."""
    id: int
    alert_id: int
    user_id: Optional[int] = None
    acknowledged_at: datetime
    notes: Optional[str] = None
    action: str

    model_config = ConfigDict(from_attributes=True)


# Notification Log schemas
class NotificationLogResponse(BaseModel):
    """Schema for notification log response."""
    id: int
    alert_id: int
    user_id: Optional[int] = None
    notification_type: str
    recipient: str
    status: str
    error_message: Optional[str] = None
    provider: Optional[str] = None
    provider_message_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Analytics schemas
class AlertAnalytics(BaseModel):
    """Schema for alert analytics."""
    total_alerts: int
    active_alerts: int
    by_level: Dict[str, int]
    by_station: List[Dict[str, Any]]
    acknowledgment_rate: float
    avg_response_time_minutes: Optional[float] = None


class NotificationAnalytics(BaseModel):
    """Schema for notification analytics."""
    total_sent: int
    by_type: Dict[str, int]
    success_rate: float
    failed_count: int
    by_provider: Dict[str, Dict[str, int]]


# Vessel Detection schemas (Maritime Extension)
class VesselDetectionBase(BaseModel):
    """Base vessel detection schema."""
    scene_id: str = Field(..., min_length=1, max_length=255)
    detection_time: datetime
    intensity_db: float
    confidence: float = Field(..., ge=0, le=1)
    vessel_length_m: Optional[float] = Field(None, ge=0)
    vessel_heading_deg: Optional[float] = Field(None, ge=0, le=360)
    in_river_mouth: bool = False
    in_port_zone: bool = False
    near_flood_plume: bool = False
    detector_type: str = Field(default="cfar", max_length=50)


class VesselDetectionCreate(VesselDetectionBase):
    """Schema for creating a vessel detection (requires lon/lat)."""
    lon: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)


class VesselDetectionResponse(VesselDetectionBase):
    """Schema for vessel detection response."""
    id: int
    lon: float
    lat: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VesselDetectionGeoJSON(BaseModel):
    """GeoJSON Feature response for vessel detection."""
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


# Port Fairway schemas
class PortFairwayBase(BaseModel):
    """Base port fairway schema."""
    name: str = Field(..., min_length=1, max_length=255)
    port_code: str = Field(..., min_length=1, max_length=50)
    reference_draught_m: float = Field(..., gt=0)
    baseline_discharge_m3s: float = Field(..., gt=0)
    country: Optional[str] = Field(None, max_length=2)
    river_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class PortFairwayResponse(PortFairwayBase):
    """Schema for port fairway response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Port Safe Draught schemas
class PortSafeDraughtResponse(BaseModel):
    """Schema for port safe draught calculation response."""
    port_name: str
    port_code: str
    calculation_time: datetime
    reference_draught_m: float
    current_discharge_m3s: float
    baseline_discharge_m3s: float
    siltation_depth_m: float
    safe_draught_m: float
    draught_change_24h_m: Optional[float] = None
    risk_level: str  # "normal", "reduced", "critical"
    
    model_config = ConfigDict(from_attributes=True)


class PortRiskSummary(BaseModel):
    """Schema for port risk summary (for dashboard widget)."""
    port_name: str
    port_code: str
    safe_draught_m: float
    risk_level: str
    draught_change_24h_m: Optional[float] = None
    status_message: str  # Human-readable status
    color: str  # Color code for UI: "green", "yellow", "red"
    
    model_config = ConfigDict(from_attributes=True)


# Flood Plume schemas
class FloodPlumeBase(BaseModel):
    """Base flood plume schema."""
    river_name: str = Field(..., min_length=1, max_length=255)
    river_basin: Optional[str] = Field(None, max_length=255)
    peak_discharge_m3s: float = Field(..., gt=0)
    current_discharge_m3s: Optional[float] = Field(None, gt=0)
    detection_time: datetime
    turbidity_index: Optional[float] = None
    area_km2: Optional[float] = Field(None, gt=0)
    buffer_radius_km: float = Field(..., gt=0)
    detection_method: str = Field(default="turbidity", max_length=50)
    is_active: bool = True
    has_vessel_activity: bool = False
    vessel_count: int = Field(default=0, ge=0)


class FloodPlumeResponse(FloodPlumeBase):
    """Schema for flood plume response."""
    id: int
    source_scene_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FloodPlumeGeoJSON(BaseModel):
    """GeoJSON Feature response for flood plume."""
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)


class PlumeSummary(BaseModel):
    """Schema for plume summary (for dashboard widget)."""
    river_name: str
    peak_discharge_m3s: float
    area_km2: Optional[float]
    vessel_count: int
    detection_time: datetime
    is_active: bool
    alert_level: str  # "none", "warning", "critical"
    color: str  # Color code for UI: "blue", "orange", "red"
    
    model_config = ConfigDict(from_attributes=True)
