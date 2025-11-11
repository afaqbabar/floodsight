"""GloFAS (Global Flood Awareness System) data ingestion service."""
from datetime import datetime, timedelta, timezone
import random
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.logging import get_logger
from app.db.models import Station, Forecast

logger = get_logger(__name__)


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


# TODO: Implement real GloFAS data ingestion
# 
# async def ingest_glofas_forecast(db: AsyncSession) -> int:
#     """
#     Ingest real GloFAS forecast data from ECMWF.
#     
#     Steps:
#     1. Authenticate with ECMWF CDS API
#     2. Download latest GloFAS GRIB files
#     3. Parse with xarray + cfgrib
#     4. Extract discharge at station coordinates
#     5. Store forecasts in database
#     
#     Example:
#         import xarray as xr
#         import cfgrib
#         
#         # Open GRIB file
#         ds = xr.open_dataset('glofas_forecast.grib', engine='cfgrib')
#         
#         # Extract discharge at station location
#         for station in stations:
#             discharge = ds.sel(
#                 latitude=station.lat,
#                 longitude=station.lon,
#                 method='nearest'
#             )['dis24'].values
#             
#             # Store forecast...
#     
#     Returns:
#         Number of forecasts ingested
#     """
#     pass

