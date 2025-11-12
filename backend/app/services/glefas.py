"""GloFAS (Global Flood Awareness System) data ingestion service."""
from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, List, Tuple

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import Forecast, Station

logger = get_logger(__name__)


class GlofasCredentialsError(RuntimeError):
    """Raised when GloFAS ingestion lacks required credentials."""


class GlofasIngestionError(RuntimeError):
    """Raised when the GloFAS ingestion fails unexpectedly."""


@dataclass(slots=True)
class ForecastRecord:
    """Normalized forecast record ready for persistence."""

    station_id: int
    ts: datetime
    lead_hours: int
    discharge_m3s: float
    model_run: datetime
    water_level_m: float | None = None
    source: str = "GloFAS"


async def ingest_fake_forecast(db: AsyncSession) -> int:
    """
    Ingest fake forecast data for testing.
    
    In production, this will:
    - Download GRIB files from ECMWF GloFAS
    - Parse using xarray + cfgrib
    - Extract discharge forecasts for each station
    - Store in database
    
    Args:
        db: Database session
        
    Returns:
        Number of forecasts ingested
    """
    logger.info("Starting fake forecast ingestion...")
    
    # Get all stations
    result = await db.execute(select(Station))
    stations = result.scalars().all()
    
    if not stations:
        logger.warning("No stations found in database")
        return 0
    
    base_time = datetime.now(timezone.utc)
    model_run = base_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    forecast_count = 0
    
    # Generate forecasts for 72-hour lead time (6-hour intervals)
    lead_times = [6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72]
    
    for station in stations:
        for lead_hours in lead_times:
            forecast_time = model_run + timedelta(hours=lead_hours)
            
            # Simulate discharge (100-2500 m³/s with some variability)
            base_discharge = random.uniform(200, 1500)
            # Add some trend (increasing discharge over time)
            trend = lead_hours * random.uniform(0, 5)
            discharge = max(50, base_discharge + trend)
            
            # Simulate water level (rough correlation: discharge / 100)
            water_level = discharge / 100 + random.uniform(-0.5, 0.5)
            
            forecast = Forecast(
                station_id=station.id,
                ts=forecast_time,
                lead_hours=lead_hours,
                discharge_m3s=round(discharge, 2),
                water_level_m=round(water_level, 2),
                source="GloFAS-fake",
                model_run=model_run,
            )
            db.add(forecast)
            forecast_count += 1
    
    await db.commit()
    
    logger.info(f"Ingested {forecast_count} fake forecasts for {len(stations)} stations")
    logger.info(f"Model run: {model_run}")
    logger.info(f"Lead times: {lead_times} hours")
    
    return forecast_count


async def ingest_glofas_forecast(db: AsyncSession) -> int:
    """
    Ingest real GloFAS forecast data from the Copernicus Data Store.
    
    Raises:
        GlofasCredentialsError: if CDS credentials are missing.
        GlofasIngestionError: if ingestion fails.
    """
    logger.info("Starting real GloFAS forecast ingestion...")
    
    if not settings.CDS_API_KEY or not settings.CDS_API_EMAIL:
        raise GlofasCredentialsError(
            "CDS_API_KEY and CDS_API_EMAIL must be configured for real GloFAS ingestion."
        )
    
    result = await db.execute(select(Station))
    stations = result.scalars().all()
    
    if not stations:
        logger.warning("No stations found in database")
        return 0
    
    try:
        records = await asyncio.to_thread(
            _download_and_prepare_glofas_forecasts,
            stations,
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        raise GlofasIngestionError(f"GloFAS ingestion failed: {exc}") from exc
    
    if not records:
        logger.warning("No GloFAS forecast records returned from CDS")
        return 0
    
    model_run = records[0].model_run
    
    # Remove previous forecasts from the same model run to avoid duplication
    await db.execute(
        delete(Forecast).where(
            Forecast.model_run == model_run,
            Forecast.source == "GloFAS",
        )
    )
    
    for record in records:
        db.add(
            Forecast(
                station_id=record.station_id,
                ts=record.ts,
                lead_hours=record.lead_hours,
                discharge_m3s=record.discharge_m3s,
                water_level_m=record.water_level_m,
                source=record.source,
                model_run=record.model_run,
            )
        )
    
    await db.commit()
    
    logger.info(
        "Ingested %s GloFAS forecasts across %s stations (model run %s)",
        len(records),
        len({r.station_id for r in records}),
        model_run.isoformat(),
    )
    
    return len(records)


async def ingest_forecasts(db: AsyncSession) -> Tuple[int, str]:
    """
    Ingest forecasts based on configured mode.
    
    Returns:
        Tuple of (forecast_count, ingestion_mode)
    """
    mode = (settings.GLOFAS_INGEST_MODE or "auto").lower().strip()
    logger.info("Selected GloFAS ingestion mode: %s", mode)
    
    if mode not in {"auto", "real", "fake"}:
        logger.warning("Unknown GLOFAS_INGEST_MODE '%s', defaulting to 'auto'", mode)
        mode = "auto"
    
    if mode == "fake":
        count = await ingest_fake_forecast(db)
        return count, "fake"
    
    try:
        count = await ingest_glofas_forecast(db)
        return count, "real"
    except GlofasCredentialsError as cred_err:
        logger.warning("GloFAS credentials missing: %s", cred_err)
        if mode == "real":
            raise
    except GlofasIngestionError as ingestion_err:
        logger.error("GloFAS ingestion error: %s", ingestion_err, exc_info=True)
        if mode == "real":
            raise
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.error("Unexpected GloFAS ingestion failure: %s", exc, exc_info=True)
        if mode == "real":
            raise
    
    logger.info("Falling back to fake forecast ingestion")
    count = await ingest_fake_forecast(db)
    return count, "fake"


def _download_and_prepare_glofas_forecasts(stations: Iterable[Station]) -> List[ForecastRecord]:
    """Download the latest GloFAS forecast and convert to normalized records."""
    import cdsapi
    import pandas as pd
    import xarray as xr

    stations_list = [s for s in stations if s.lat is not None and s.lon is not None]
    if not stations_list:
        logger.warning("No stations with lat/lon available for GloFAS ingestion")
        return []
    
    now_utc = datetime.now(timezone.utc)
    model_run_dt = _determine_model_run(now_utc, settings.GLOFAS_RUN_LAG_HOURS)
    leadtimes = sorted({int(lt) for lt in settings.GLOFAS_LEADTIMES})
    
    north, south, west, east = _compute_download_bounds(stations_list)
    
    request = {
        "system_version": settings.GLOFAS_SYSTEM_VERSION,
        "product_type": settings.GLOFAS_PRODUCT_TYPE,
        "variable": settings.GLOFAS_VARIABLE,
        "format": "netcdf",
        "date": model_run_dt.strftime("%Y-%m-%d"),
        "time": model_run_dt.strftime("%H:%M"),
        "leadtime_hour": [str(lt) for lt in leadtimes],
        "area": [north, west, south, east],
    }
    
    logger.info("Requesting GloFAS forecast: %s", request)
    
    with TemporaryDirectory() as tmp_dir:
        target = Path(tmp_dir) / "glofas.nc"
        client = cdsapi.Client(
            url=settings.CDS_API_URL,
            key=f"{settings.CDS_API_EMAIL}:{settings.CDS_API_KEY}",
            verify=settings.CDS_API_VERIFY,
            timeout=settings.CDS_API_TIMEOUT,
        )
        client.retrieve("cems-glofas-forecast", request, str(target))
        
        ds = xr.open_dataset(target)
        try:
            variable_name = _resolve_variable_name(ds)
            dataset_model_run = _extract_model_run(ds, model_run_dt)
            records: List[ForecastRecord] = []
            
            uses_positive_lon = float(ds["longitude"].min()) >= 0  # type: ignore[index]
            
            for station in stations_list:
                lon = station.lon if not uses_positive_lon else (station.lon + 360) % 360
                
                try:
                    series = ds[variable_name].sel(
                        latitude=station.lat,
                        longitude=lon,
                        method="nearest",
                    )
                except Exception as exc:  # pragma: no cover - xarray edge case
                    logger.warning(
                        "Failed to extract series for station %s (%s, %s): %s",
                        station.code,
                        station.lat,
                        station.lon,
                        exc,
                    )
                    continue
                
                station_records = _normalize_station_series(
                    series=series,
                    station_id=station.id,
                    model_run=dataset_model_run,
                )
                records.extend(station_records)
        finally:
            ds.close()
    
    # Limit total records per station
    records = _cap_records_per_station(records, settings.GLOFAS_MAX_RECORDS_PER_STATION)
    
    return records


def _determine_model_run(now: datetime, lag_hours: int) -> datetime:
    """Determine the most recent model run (00 or 12 UTC) with a safety lag."""
    shifted = now - timedelta(hours=max(lag_hours, 0))
    run_hour = 12 if shifted.hour >= 12 else 0
    candidate = shifted.replace(hour=run_hour, minute=0, second=0, microsecond=0)
    
    # Ensure we never move into the future
    if candidate > now:
        candidate -= timedelta(hours=12)
    
    return candidate.replace(tzinfo=timezone.utc)


def _compute_download_bounds(stations: Iterable[Station]) -> Tuple[float, float, float, float]:
    """Compute bounding box (north, south, west, east) for CDS request."""
    lats = [station.lat for station in stations if station.lat is not None]
    lons = [station.lon for station in stations if station.lon is not None]
    
    buffer_deg = max(settings.GLOFAS_BUFFER_DEGREES, 0.5)
    
    north = min(90.0, max(lats) + buffer_deg)
    south = max(-90.0, min(lats) - buffer_deg)
    west = max(-180.0, min(lons) - buffer_deg)
    east = min(180.0, max(lons) + buffer_deg)
    
    return north, south, west, east


def _resolve_variable_name(dataset) -> str:
    """Attempt to find the discharge variable within the dataset."""
    candidates = [
        settings.GLOFAS_VARIABLE,
        "discharge",
        "river_discharge_in_the_last_6_hours",
        "river_discharge_in_the_last_24_hours",
    ]
    for name in candidates:
        if name in dataset.data_vars:
            return name
    raise KeyError(
        f"Unable to locate discharge variable in dataset. Tried: {', '.join(candidates)}"
    )


def _extract_model_run(dataset, fallback: datetime) -> datetime:
    """Extract model run datetime from dataset coordinates."""
    import pandas as pd

    if "time" in dataset.coords:
        timestamp = pd.to_datetime(dataset["time"].values[0], utc=True)
        return timestamp.to_pydatetime()
    return fallback


def _normalize_station_series(series, station_id: int, model_run: datetime) -> List[ForecastRecord]:
    """Convert xarray station series to normalized forecast records."""
    import pandas as pd

    df = series.to_dataframe(name="discharge").reset_index()
    if df.empty:
        return []
    
    if "discharge" not in df.columns:
        # Fallback rename for unexpected column names
        for candidate in ["value", settings.GLOFAS_VARIABLE]:
            if candidate in df.columns:
                df = df.rename(columns={candidate: "discharge"})
                break
    
    if "valid_time" in df.columns:
        df["ts"] = pd.to_datetime(df["valid_time"], utc=True)
    else:
        df["time"] = pd.to_datetime(df.get("time"), utc=True)
        if "step" in df.columns:
            df["ts"] = df["time"] + pd.to_timedelta(df["step"])
        else:
            df["ts"] = df["time"]
    
    df = df.dropna(subset=["ts", "discharge"])
    df["lead_hours"] = (
        (df["ts"] - pd.Timestamp(model_run, tz="UTC")) / pd.Timedelta(hours=1)
    ).round().astype(int)
    df = df[df["lead_hours"] >= 0]
    df = df.sort_values("ts").drop_duplicates(subset="ts")
    
    records: List[ForecastRecord] = []
    for row in df.itertuples():
        discharge = float(row.discharge)
        water_level = round(discharge / 120, 2)
        records.append(
            ForecastRecord(
                station_id=station_id,
                ts=row.ts.to_pydatetime(),
                lead_hours=int(row.lead_hours),
                discharge_m3s=round(discharge, 2),
                water_level_m=water_level,
                model_run=model_run,
            )
        )
    
    return records


def _cap_records_per_station(records: List[ForecastRecord], limit: int) -> List[ForecastRecord]:
    """Limit number of forecast records per station."""
    if limit <= 0:
        return records
    
    capped: List[ForecastRecord] = []
    counts: dict[int, int] = {}
    
    for record in sorted(records, key=lambda r: (r.station_id, r.ts)):
        counts.setdefault(record.station_id, 0)
        if counts[record.station_id] >= limit:
            continue
        capped.append(record)
        counts[record.station_id] += 1
    
    return capped
