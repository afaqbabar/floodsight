"""API v1 endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
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
)
from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import Alert, Forecast, Station
from app.db.session import get_db
from app.services.glefas import (
    GlofasCredentialsError,
    GlofasIngestionError,
    ingest_fake_forecast,
    ingest_forecasts,
)
from app.services.alerts import compute_alerts_from_forecasts, create_alerts_from_forecasts

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

