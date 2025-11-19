"""API v1 endpoints."""
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.schemas import (
    AlertCreate,
    AlertResponse,
    ForecastCreate,
    ForecastResponse,
    HealthResponse,
    StationCreate,
    StationResponse,
    TelemetryEvent,
    TelemetryResponse,
    VesselDetectionResponse,
    VesselDetectionGeoJSON,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import Alert, Forecast, Station, VesselDetection
from app.db.session import get_db
from app.services.glefas import (
    GlofasCredentialsError,
    GlofasIngestionError,
    ingest_fake_forecast,
    ingest_forecasts,
)
from app.services.alerts import compute_alerts_from_forecasts, create_alerts_from_forecasts
from app.services.sentinel1 import ingest_sentinel1_with_vessels

logger = get_logger(__name__)

router = APIRouter()


# Health endpoint
@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Health check endpoint.
    
    Returns application status, database connectivity, and process metrics.
    """
    import time
    import psutil
    import os
    from app.main import APP_START_TIME
    
    try:
        # Test database connection
        await db.execute(select(1))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    # Get process metrics
    try:
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent(interval=0.1)
        uptime_seconds = time.time() - APP_START_TIME
    except Exception as e:
        logger.warning(f"Failed to get process metrics: {e}")
        memory_mb = 0.0
        cpu_percent = 0.0
        uptime_seconds = 0.0
    
    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        uptime_seconds=uptime_seconds,
        memory_mb=memory_mb,
        cpu_percent=cpu_percent,
    )


# Telemetry endpoint
@router.post("/telemetry", response_model=TelemetryResponse, tags=["Telemetry"])
async def log_telemetry(event: TelemetryEvent) -> TelemetryResponse:
    """
    Log frontend telemetry events.
    
    Receives client-side events like errors, page views, or user actions.
    Logs them for analysis and optionally forwards to monitoring systems.
    """
    logger.info(
        f"Telemetry event: {event.event_name}",
        extra={
            "event_name": event.event_name,
            "timestamp": event.timestamp,
            "page": event.page,
            "user_agent": event.user_agent,
            "context": event.context,
        },
    )
    
    return TelemetryResponse(
        status="ok",
        message="Event received",
    )


# Station endpoints
@router.get("/stations", response_model=List[StationResponse], tags=["Stations"])
async def list_stations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[Station]:
    """
    List all hydrological stations.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    result = await db.execute(
        select(Station).offset(skip).limit(limit).order_by(Station.name)
    )
    stations = result.scalars().all()
    return list(stations)


@router.get("/stations/{station_id}", response_model=StationResponse, tags=["Stations"])
async def get_station(
    station_id: int,
    db: AsyncSession = Depends(get_db),
) -> Station:
    """Get a specific station by ID."""
    result = await db.execute(select(Station).where(Station.id == station_id))
    station = result.scalar_one_or_none()
    
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with id {station_id} not found",
        )
    
    return station


@router.post(
    "/stations",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Stations"],
)
async def create_station(
    station: StationCreate,
    db: AsyncSession = Depends(get_db),
) -> Station:
    """
    Create a new station.
    
    Note: In production, this should require authentication.
    """
    # Check if station code already exists
    result = await db.execute(select(Station).where(Station.code == station.code))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Station with code {station.code} already exists",
        )
    
    db_station = Station(**station.model_dump())
    db.add(db_station)
    await db.commit()
    await db.refresh(db_station)
    
    logger.info(f"Created station: {db_station.code} - {db_station.name}")
    return db_station


# Forecast endpoints
@router.get("/forecasts", response_model=List[ForecastResponse], tags=["Forecasts"])
async def list_forecasts(
    station_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[Forecast]:
    """
    List forecasts.
    
    - **station_id**: Filter by station ID (optional)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    query = select(Forecast).order_by(Forecast.ts.desc())
    
    if station_id:
        query = query.where(Forecast.station_id == station_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    forecasts = result.scalars().all()
    return list(forecasts)


@router.post(
    "/forecasts",
    response_model=ForecastResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Forecasts"],
)
async def create_forecast(
    forecast: ForecastCreate,
    db: AsyncSession = Depends(get_db),
) -> Forecast:
    """
    Create a new forecast.
    
    Note: In production, this should require authentication.
    """
    # Verify station exists
    result = await db.execute(select(Station).where(Station.id == forecast.station_id))
    station = result.scalar_one_or_none()
    
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with id {forecast.station_id} not found",
        )
    
    db_forecast = Forecast(**forecast.model_dump())
    db.add(db_forecast)
    await db.commit()
    await db.refresh(db_forecast)
    
    logger.info(f"Created forecast for station {forecast.station_id}: {forecast.discharge_m3s} m³/s")
    return db_forecast


@router.post(
    "/forecasts/ingest",
    status_code=status.HTTP_201_CREATED,
    tags=["Forecasts"],
)
async def ingest_forecasts_api(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Trigger forecast ingestion (real GloFAS or fallback to fake).
    
    Behaviour depends on ``GLOFAS_INGEST_MODE``:
    - ``auto`` (default): try real ingestion, fallback to fake.
    - ``real``: require real ingestion (errors if unavailable).
    - ``fake``: generate synthetic data.
    """
    logger.info("Manual forecast ingestion (auto/real) triggered")
    try:
        forecast_count, mode = await ingest_forecasts(db)
        return {
            "status": "success",
            "message": f"Ingested {forecast_count} forecasts ({mode})",
            "forecasts_created": forecast_count,
            "mode": mode,
        }
    except GlofasCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except GlofasIngestionError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.post(
    "/forecasts/ingest-dev",
    status_code=status.HTTP_201_CREATED,
    tags=["Forecasts"],
)
async def ingest_dev_forecasts(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Manually trigger fake forecast ingestion for development/testing.
    
    This endpoint:
    - Generates fake GloFAS forecast data for all stations
    - Creates forecasts for 72-hour lead time (6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72 hours)
    - Useful for testing alert computation and data flow
    
    In production, this will be replaced by scheduled Prefect flows
    that download real ECMWF GloFAS data.
    """
    logger.info("Manual forecast ingestion triggered")
    
    try:
        forecast_count = await ingest_fake_forecast(db)
        
        return {
            "status": "success",
            "message": f"Ingested {forecast_count} forecasts",
            "forecasts_created": forecast_count,
        }
    except Exception as e:
        logger.error(f"Forecast ingestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecast ingestion failed: {str(e)}",
        )


# Alert endpoints
@router.get("/alerts", response_model=List[AlertResponse], tags=["Alerts"])
async def list_alerts(
    station_id: int | None = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[Alert]:
    """
    List alerts.
    
    - **station_id**: Filter by station ID (optional)
    - **active_only**: Show only active alerts (default: true)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    query = select(Alert).order_by(Alert.issued_at.desc())
    
    if station_id:
        query = query.where(Alert.station_id == station_id)
    
    if active_only:
        query = query.where(Alert.is_active == True)  # noqa: E712
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    alerts = result.scalars().all()
    return list(alerts)


@router.post(
    "/alerts",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Alerts"],
)
async def create_alert(
    alert: AlertCreate,
    db: AsyncSession = Depends(get_db),
) -> Alert:
    """
    Create a new alert.
    
    Note: In production, this should require authentication.
    """
    # Verify station exists
    result = await db.execute(select(Station).where(Station.id == alert.station_id))
    station = result.scalar_one_or_none()
    
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with id {alert.station_id} not found",
        )
    
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    
    logger.info(f"Created alert for station {alert.station_id}: {alert.level}")
    return db_alert


@router.patch("/alerts/{alert_id}/deactivate", response_model=AlertResponse, tags=["Alerts"])
async def deactivate_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
) -> Alert:
    """Deactivate an alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found",
        )
    
    alert.is_active = False
    await db.commit()
    await db.refresh(alert)
    
    logger.info(f"Deactivated alert {alert_id}")
    return alert


@router.post(
    "/alerts/compute",
    status_code=status.HTTP_201_CREATED,
    tags=["Alerts"],
)
async def compute_alerts(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Compute alerts from recent forecast data.
    
    This endpoint:
    - Analyzes recent forecasts (last 6 hours)
    - Determines alert levels based on discharge thresholds:
      - info: 800+ m³/s
      - warning: 1200+ m³/s  
      - severe: 1600+ m³/s
      - extreme: 2000+ m³/s
    - Calculates probability based on forecast lead time
    - Creates/updates alert records in database
    
    Returns computed alerts with station information.
    """
    logger.info("Alert computation triggered")
    
    try:
        # Compute alerts from forecasts
        computed_alerts = await compute_alerts_from_forecasts(db)
        
        # Create alerts in database
        alerts_created = await create_alerts_from_forecasts(db)
        
        return {
            "status": "success",
            "message": f"Computed {len(computed_alerts)} alerts, created {alerts_created} in database",
            "alerts_computed": len(computed_alerts),
            "alerts_created": alerts_created,
            "alerts": computed_alerts,
        }
    except Exception as e:
        logger.error(f"Alert computation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert computation failed: {str(e)}",
        )


# Vessel Detection endpoints (Maritime Extension)
@router.get("/vessels", response_model=List[VesselDetectionResponse], tags=["Vessels"])
async def list_vessel_detections(
    scene_id: str | None = None,
    min_confidence: float = 0.0,
    in_river_mouth: bool | None = None,
    in_port_zone: bool | None = None,
    near_flood_plume: bool | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    List vessel detections from Sentinel-1 SAR processing.
    
    - **scene_id**: Filter by Sentinel-1 scene ID (optional)
    - **min_confidence**: Minimum detection confidence (0-1, default: 0.0)
    - **in_river_mouth**: Filter vessels in river mouths (optional)
    - **in_port_zone**: Filter vessels in port zones (optional)
    - **near_flood_plume**: Filter vessels near flood plumes (optional)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    
    Returns vessel detections with lon/lat extracted from PostGIS geometry.
    """
    from sqlalchemy import func, cast, String
    
    query = select(
        VesselDetection,
        func.ST_X(VesselDetection.geom).label('lon'),
        func.ST_Y(VesselDetection.geom).label('lat')
    ).order_by(VesselDetection.detection_time.desc())
    
    if scene_id:
        query = query.where(VesselDetection.scene_id == scene_id)
    
    if min_confidence > 0:
        query = query.where(VesselDetection.confidence >= min_confidence)
    
    if in_river_mouth is not None:
        query = query.where(VesselDetection.in_river_mouth == in_river_mouth)
    
    if in_port_zone is not None:
        query = query.where(VesselDetection.in_port_zone == in_port_zone)
    
    if near_flood_plume is not None:
        query = query.where(VesselDetection.near_flood_plume == near_flood_plume)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    rows = result.all()
    
    # Convert to response format
    detections = []
    for vessel, lon, lat in rows:
        detection_dict = {
            "id": vessel.id,
            "scene_id": vessel.scene_id,
            "detection_time": vessel.detection_time,
            "intensity_db": vessel.intensity_db,
            "confidence": vessel.confidence,
            "vessel_length_m": vessel.vessel_length_m,
            "vessel_heading_deg": vessel.vessel_heading_deg,
            "in_river_mouth": vessel.in_river_mouth,
            "in_port_zone": vessel.in_port_zone,
            "near_flood_plume": vessel.near_flood_plume,
            "detector_type": vessel.detector_type,
            "lon": lon,
            "lat": lat,
            "created_at": vessel.created_at,
        }
        detections.append(detection_dict)
    
    return detections


@router.get("/vessels/geojson", response_model=dict, tags=["Vessels"])
async def list_vessel_detections_geojson(
    scene_id: str | None = None,
    min_confidence: float = 0.0,
    limit: int = 1000,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    List vessel detections as GeoJSON FeatureCollection.
    
    Optimized for map rendering in frontend dashboards.
    
    - **scene_id**: Filter by Sentinel-1 scene ID (optional)
    - **min_confidence**: Minimum detection confidence (0-1, default: 0.0)
    - **limit**: Maximum number of features to return (default: 1000)
    
    Returns GeoJSON FeatureCollection compatible with Mapbox/Leaflet.
    """
    from sqlalchemy import func
    
    query = select(
        VesselDetection,
        func.ST_X(VesselDetection.geom).label('lon'),
        func.ST_Y(VesselDetection.geom).label('lat')
    ).order_by(VesselDetection.detection_time.desc())
    
    if scene_id:
        query = query.where(VesselDetection.scene_id == scene_id)
    
    if min_confidence > 0:
        query = query.where(VesselDetection.confidence >= min_confidence)
    
    query = query.limit(limit)
    result = await db.execute(query)
    rows = result.all()
    
    # Build GeoJSON FeatureCollection
    features = []
    for vessel, lon, lat in rows:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "id": vessel.id,
                "scene_id": vessel.scene_id,
                "detection_time": vessel.detection_time.isoformat(),
                "intensity_db": vessel.intensity_db,
                "confidence": vessel.confidence,
                "vessel_length_m": vessel.vessel_length_m,
                "vessel_heading_deg": vessel.vessel_heading_deg,
                "in_river_mouth": vessel.in_river_mouth,
                "in_port_zone": vessel.in_port_zone,
                "near_flood_plume": vessel.near_flood_plume,
                "detector_type": vessel.detector_type,
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "count": len(features),
            "scene_id": scene_id,
            "min_confidence": min_confidence,
        }
    }


@router.post(
    "/vessels/ingest",
    status_code=status.HTTP_201_CREATED,
    tags=["Vessels"],
)
async def ingest_vessels_api(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Trigger Sentinel-1 vessel detection ingestion.
    
    This endpoint:
    - Processes latest Sentinel-1 scene(s)
    - Runs CFAR vessel detection on speckle-filtered SAR data
    - Stores vessel detections as PostGIS points
    - Returns count of vessels detected
    
    In production, this runs automatically via scheduled Prefect flows.
    Use this endpoint for manual testing or on-demand processing.
    """
    logger.info("Manual Sentinel-1 vessel detection triggered")
    
    try:
        vessel_count = await ingest_sentinel1_with_vessels(db)
        
        return {
            "status": "success",
            "message": f"Detected {vessel_count} vessels",
            "vessels_detected": vessel_count,
        }
    except Exception as e:
        logger.error(f"Sentinel-1 vessel detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentinel-1 vessel detection failed: {str(e)}",
        )



# ==================== Maritime: Port Siltation & Safe Draught ====================

from app.services.port_siltation import calculate_port_safe_draught, calculate_all_ports
from app.api.v1.schemas import PortSafeDraughtResponse, PortRiskSummary, PortFairwayResponse
from app.db.models import PortFairway, PortSafeDraughtLog


@router.get("/maritime/port-risk", response_model=PortSafeDraughtResponse, tags=["Maritime"])
async def get_port_risk(
    port: str = "Port of Duisburg",
    db: AsyncSession = Depends(get_db),
) -> PortSafeDraughtResponse:
    """
    Get current safe draught and risk assessment for a port.
    
    **Example:** `/v1/maritime/port-risk?port=Port of Duisburg`
    
    Returns:
        Current safe draught, siltation depth, and risk level
    """
    logger.info(f"Port risk request: {port}")
    
    calculation = await calculate_port_safe_draught(db, port)
    
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Port not found or no discharge data available: {port}"
        )
    
    return PortSafeDraughtResponse(**calculation)


@router.get("/maritime/port-risk/summary", response_model=List[PortRiskSummary], tags=["Maritime"])
async def get_all_ports_risk_summary(
    db: AsyncSession = Depends(get_db),
) -> List[PortRiskSummary]:
    """
    Get risk summary for all active ports (for dashboard widget).
    
    Returns:
        List of port risk summaries with color-coded status
    """
    logger.info("Fetching risk summary for all ports")
    
    calculations = await calculate_all_ports(db)
    
    summaries = []
    for calc in calculations:
        # Determine color based on risk level
        color_map = {
            "normal": "green",
            "reduced": "yellow",
            "critical": "red"
        }
        
        # Generate status message
        status_messages = {
            "normal": f"Safe draught: {calc['safe_draught_m']:.1f}m (Normal)",
            "reduced": f"⚠️ Reduced draught: {calc['safe_draught_m']:.1f}m",
            "critical": f"🚨 Critical: {calc['safe_draught_m']:.1f}m - Navigation restricted"
        }
        
        summary = PortRiskSummary(
            port_name=calc["port_name"],
            port_code=calc["port_code"],
            safe_draught_m=calc["safe_draught_m"],
            risk_level=calc["risk_level"],
            draught_change_24h_m=calc.get("draught_change_24h_m"),
            status_message=status_messages.get(calc["risk_level"], "Unknown status"),
            color=color_map.get(calc["risk_level"], "gray")
        )
        
        summaries.append(summary)
    
    logger.info(f"Returning risk summary for {len(summaries)} ports")
    
    return summaries


@router.get("/maritime/ports", response_model=List[PortFairwayResponse], tags=["Maritime"])
async def list_ports(
    db: AsyncSession = Depends(get_db),
    active_only: bool = True,
) -> List[PortFairwayResponse]:
    """
    List all port fairways.
    
    Args:
        active_only: Only return active ports (default: True)
    
    Returns:
        List of port fairways
    """
    query = select(PortFairway)
    
    if active_only:
        query = query.where(PortFairway.is_active == True)
    
    result = await db.execute(query)
    ports = result.scalars().all()
    
    logger.info(f"Returning {len(ports)} ports")
    
    return [PortFairwayResponse.model_validate(port) for port in ports]


@router.post("/maritime/calculate-all-ports", status_code=status.HTTP_200_OK, tags=["Maritime"])
async def trigger_port_calculations(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Manually trigger safe draught calculations for all ports.
    
    Returns:
        Summary of calculations performed
    """
    logger.info("Manual trigger: calculating safe draught for all ports")
    
    try:
        calculations = await calculate_all_ports(db)
        
        return {
            "status": "success",
            "message": f"Calculated safe draught for {len(calculations)} ports",
            "ports_calculated": len(calculations),
            "calculations": calculations
        }
    except Exception as e:
        logger.error(f"Failed to calculate port safe draughts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate port safe draughts: {str(e)}"
        )


# ==================== Maritime: Flood Plumes & Nutrient Monitoring ====================

from app.services.plume_detection import detect_all_river_plumes, get_recent_plumes
from app.api.v1.schemas import FloodPlumeResponse, FloodPlumeGeoJSON, PlumeSummary
from app.db.models import FloodPlume
from geoalchemy2.shape import to_shape


@router.get("/maritime/plumes", response_model=List[FloodPlumeResponse], tags=["Maritime"])
async def list_flood_plumes(
    river: Optional[str] = None,
    days: int = 7,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
) -> List[FloodPlumeResponse]:
    """
    List flood plumes for nutrient/sediment monitoring.
    
    **Example:** `/v1/maritime/plumes?river=elbe&days=7`
    
    Args:
        river: Filter by river name (e.g., "elbe", "rhine", "danube")
        days: Number of days to look back (default: 7)
        active_only: Only return currently active plumes (default: true)
    
    Returns:
        List of flood plumes with vessel activity
    """
    logger.info(f"Plume list request: river={river}, days={days}, active_only={active_only}")
    
    plumes = await get_recent_plumes(db, river, days, active_only)
    
    return [FloodPlumeResponse.model_validate(plume) for plume in plumes]


@router.get("/maritime/plumes/geojson", response_model=dict, tags=["Maritime"])
async def list_flood_plumes_geojson(
    river: Optional[str] = None,
    days: int = 7,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get flood plumes as GeoJSON FeatureCollection for map visualization.
    
    Args:
        river: Filter by river name
        days: Number of days to look back
        active_only: Only return active plumes
    
    Returns:
        GeoJSON FeatureCollection with plume polygons
    """
    logger.info(f"Plume GeoJSON request: river={river}, days={days}")
    
    plumes = await get_recent_plumes(db, river, days, active_only)
    
    features = []
    for plume in plumes:
        geom = to_shape(plume.geom)
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [list(geom.exterior.coords)]
            },
            "properties": {
                "id": plume.id,
                "river_name": plume.river_name,
                "peak_discharge_m3s": plume.peak_discharge_m3s,
                "area_km2": plume.area_km2,
                "vessel_count": plume.vessel_count,
                "has_vessel_activity": plume.has_vessel_activity,
                "detection_time": plume.detection_time.isoformat(),
                "is_active": plume.is_active,
                "detection_method": plume.detection_method,
            }
        }
        
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    logger.info(f"Returning {len(features)} plume features as GeoJSON")
    
    return geojson


@router.get("/maritime/plumes/summary", response_model=List[PlumeSummary], tags=["Maritime"])
async def get_plumes_summary(
    db: AsyncSession = Depends(get_db),
    days: int = 7,
) -> List[PlumeSummary]:
    """
    Get plume summary for dashboard widget (color-coded alerts).
    
    Args:
        days: Number of days to look back
    
    Returns:
        List of plume summaries with alert levels
    """
    logger.info(f"Plume summary request: days={days}")
    
    plumes = await get_recent_plumes(db, river_name=None, days=days, active_only=True)
    
    summaries = []
    for plume in plumes:
        # Determine alert level based on vessel count
        if plume.vessel_count >= 10:
            alert_level = "critical"
            color = "red"
        elif plume.vessel_count >= 5:
            alert_level = "warning"
            color = "orange"
        else:
            alert_level = "none"
            color = "blue"
        
        summary = PlumeSummary(
            river_name=plume.river_name,
            peak_discharge_m3s=plume.peak_discharge_m3s,
            area_km2=plume.area_km2,
            vessel_count=plume.vessel_count,
            detection_time=plume.detection_time,
            is_active=plume.is_active,
            alert_level=alert_level,
            color=color
        )
        
        summaries.append(summary)
    
    logger.info(f"Returning summary for {len(summaries)} plumes")
    
    return summaries


@router.post("/maritime/detect-plumes", status_code=status.HTTP_200_OK, tags=["Maritime"])
async def trigger_plume_detection(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Manually trigger plume detection for all rivers.
    
    Returns:
        Summary of plumes detected
    """
    logger.info("Manual trigger: detecting flood plumes for all rivers")
    
    try:
        plumes = await detect_all_river_plumes(db)
        
        return {
            "status": "success",
            "message": f"Detected {len(plumes)} flood plumes",
            "plumes_detected": len(plumes),
            "plumes": [
                {
                    "river": p.river_name,
                    "discharge": p.peak_discharge_m3s,
                    "area_km2": p.area_km2,
                    "vessels": p.vessel_count
                }
                for p in plumes
            ]
        }
    except Exception as e:
        logger.error(f"Failed to detect plumes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect plumes: {str(e)}"
        )


# ==================== Grounding Risk Tiles ====================

from fastapi.responses import Response
from app.services.grounding_risk_tiles import generate_mvt_tile, VESSEL_DRAUGHTS


@router.get("/maritime/grounding-risk/tiles/{z}/{x}/{y}.pbf", tags=["Maritime"])
async def get_grounding_risk_tile(
    z: int,
    x: int,
    y: int,
    vessel_draught: Optional[float] = None,
    vessel_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Get grounding risk vector tile for map visualization.
    
    Returns Mapbox Vector Tile (MVT) with color-coded grounding risk:
    - **Green**: Safe (clearance > 2m)
    - **Yellow**: Caution (0.5m < clearance <= 2m)
    - **Red**: Danger (clearance <= 0.5m)
    
    **Risk calculation:** `clearance = safe_draught - vessel_draught`
    
    **Args:**
    - `z`: Tile zoom level (0-22)
    - `x`: Tile X coordinate
    - `y`: Tile Y coordinate
    - `vessel_draught`: Vessel draught in metres (optional)
    - `vessel_type`: Vessel type: 'small', 'medium', 'large', 'vlcc' (optional)
    
    **Example:** `/v1/maritime/grounding-risk/tiles/8/132/84.pbf?vessel_type=large`
    """
    # Determine vessel draught
    if vessel_draught is None:
        if vessel_type and vessel_type in VESSEL_DRAUGHTS:
            vessel_draught = VESSEL_DRAUGHTS[vessel_type]
        else:
            vessel_draught = VESSEL_DRAUGHTS["medium"]  # Default to medium vessel
    
    logger.info(
        f"Grounding risk tile request: z={z}, x={x}, y={y}, "
        f"vessel_draught={vessel_draught:.2f}m"
    )
    
    try:
        tile_data = await generate_mvt_tile(db, z, x, y, vessel_draught)
        
        if tile_data is None:
            # Empty tile (HTTP 204 No Content)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        
        # Return tile with appropriate content type
        # For now, returning GeoJSON; in production, use actual MVT/PBF
        return Response(
            content=tile_data,
            media_type="application/json",  # Change to "application/vnd.mapbox-vector-tile" for real MVT
            headers={
                "Cache-Control": "public, max-age=300",  # Cache for 5 minutes
                "Access-Control-Allow-Origin": "*",
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate tile {z}/{x}/{y}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate grounding risk tile: {str(e)}"
        )


@router.get("/maritime/grounding-risk/heatmap", response_model=dict, tags=["Maritime"])
async def get_grounding_risk_heatmap(
    vessel_draught: Optional[float] = None,
    vessel_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get grounding risk heatmap data for dashboard widget.
    
    Returns all active ports with their current grounding risk levels.
    
    **Args:**
    - `vessel_draught`: Vessel draught in metres (optional)
    - `vessel_type`: Vessel type: 'small', 'medium', 'large', 'vlcc' (optional)
    
    **Response:** GeoJSON FeatureCollection with risk-colored port polygons
    """
    from app.services.grounding_risk_tiles import get_grounding_risk_features
    
    # Determine vessel draught
    if vessel_draught is None:
        if vessel_type and vessel_type in VESSEL_DRAUGHTS:
            vessel_draught = VESSEL_DRAUGHTS[vessel_type]
        else:
            vessel_draught = VESSEL_DRAUGHTS["medium"]
    
    logger.info(f"Heatmap request: vessel_draught={vessel_draught:.2f}m")
    
    try:
        # Get all ports (use a large tile that covers typical European waters)
        # z=5 covers a large area
        features = await get_grounding_risk_features(db, 5, 16, 10, vessel_draught)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "vessel_draught_m": vessel_draught,
                "vessel_type": vessel_type or "medium",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }
        
        return geojson
    except Exception as e:
        logger.error(f"Failed to generate heatmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate grounding risk heatmap: {str(e)}"
        )


@router.get("/maritime/demo-data", response_model=dict, tags=["Maritime"])
async def get_maritime_demo_data(
    vessel_type: str = Query("medium", description="Vessel type for grounding risk"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Fast single-response endpoint for the Maritime Demo page.
    
    Combines all maritime data sources into one JSON response:
    - Vessel detections (dark vessels)
    - Flood plumes
    - Port risk summary
    - Grounding risk heatmap
    - Recent maritime alerts
    
    **Args:**
    - `vessel_type`: Vessel type: 'small', 'medium', 'large', 'vlcc' (default: 'medium')
    
    **Response:** Combined maritime data for demo dashboard
    """
    from app.services.plume_detection import get_plumes_geojson
    from app.services.port_siltation import get_port_risk_summary
    from app.services.grounding_risk_tiles import get_grounding_risk_features
    from sqlalchemy import select, desc, and_
    from geoalchemy2.shape import to_shape
    from shapely.geometry import mapping
    
    logger.info(f"Maritime demo data request for vessel_type={vessel_type}")
    
    try:
        # 1. Get vessel detections (last 7 days)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        vessels_query = select(VesselDetection).where(
            VesselDetection.detection_time >= seven_days_ago
        ).order_by(desc(VesselDetection.detection_time))
        vessels_result = await db.execute(vessels_query)
        vessels = vessels_result.scalars().all()
        
        vessels_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": mapping(to_shape(v.geom)),
                    "properties": {
                        "id": v.id,
                        "confidence": v.confidence,
                        "detection_time": v.detection_time.isoformat(),
                        "scene_id": v.scene_id,
                    }
                }
                for v in vessels
            ]
        }
        
        # 2. Get flood plumes (last 7 days)
        plumes_geojson = await get_plumes_geojson(db, days=7)
        
        # 3. Get port risk summary
        ports_summary = await get_port_risk_summary(db)
        
        # 4. Get grounding risk heatmap features
        vessel_draught = VESSEL_DRAUGHTS.get(vessel_type, VESSEL_DRAUGHTS["medium"])
        grounding_features = await get_grounding_risk_features(db, 5, 16, 10, vessel_draught)
        grounding_geojson = {
            "type": "FeatureCollection",
            "features": grounding_features,
            "metadata": {
                "vessel_draught_m": vessel_draught,
                "vessel_type": vessel_type,
            }
        }
        
        # 5. Get recent maritime alerts
        alerts_query = select(Alert).where(
            and_(
                Alert.level.in_(["warning", "severe", "extreme"]),
                Alert.created_at >= seven_days_ago
            )
        ).order_by(desc(Alert.created_at)).limit(10)
        alerts_result = await db.execute(alerts_query)
        alerts = alerts_result.scalars().all()
        
        alerts_list = [
            {
                "id": a.id,
                "station_id": a.station_id,
                "level": a.level,
                "message": a.message,
                "created_at": a.created_at.isoformat(),
                "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
            }
            for a in alerts
        ]
        
        # 6. Calculate summary statistics
        active_vessels = len([v for v in vessels if (datetime.now(timezone.utc) - v.detection_time).days < 1])
        active_plumes = len(plumes_geojson.get("features", []))
        high_risk_ports = len([p for p in ports_summary if p.get("safe_draught_m", 0) < 5.0])
        
        # Combine everything
        demo_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "vessel_type": vessel_type,
            "summary": {
                "active_vessels_24h": active_vessels,
                "total_vessels_7d": len(vessels),
                "active_plumes": active_plumes,
                "high_risk_ports": high_risk_ports,
                "total_ports": len(ports_summary),
                "recent_alerts": len(alerts_list),
            },
            "vessels": vessels_geojson,
            "plumes": plumes_geojson,
            "ports": ports_summary,
            "grounding_risk": grounding_geojson,
            "alerts": alerts_list,
        }
        
        logger.info(f"Maritime demo data generated: {len(vessels)} vessels, {active_plumes} plumes, {len(ports_summary)} ports")
        return demo_data
        
    except Exception as e:
        logger.error(f"Failed to generate maritime demo data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate maritime demo data: {str(e)}"
        )
