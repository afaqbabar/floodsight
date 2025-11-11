"""Database seeding script."""
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.logging import get_logger
from app.db.models import Station, Forecast, Alert
from app.db.session import AsyncSessionLocal

logger = get_logger(__name__)

# Sample station data
SAMPLE_STATIONS = [
    {
        "code": "BERLIN-SPREE",
        "name": "Berlin Spree",
        "river_basin": "Elbe",
        "lat": 52.5200,
        "lon": 13.4050,
    },
    {
        "code": "ELBE-DRESDEN",
        "name": "Dresden Elbe",
        "river_basin": "Elbe",
        "lat": 51.0504,
        "lon": 13.7373,
    },
    {
        "code": "RHINE-COLOGNE",
        "name": "Cologne Rhine",
        "river_basin": "Rhine",
        "lat": 50.9375,
        "lon": 6.9603,
    },
    {
        "code": "DANUBE-VIENNA",
        "name": "Vienna Danube",
        "river_basin": "Danube",
        "lat": 48.2082,
        "lon": 16.3738,
    },
    {
        "code": "MAIN-FRANKFURT",
        "name": "Frankfurt Main",
        "river_basin": "Rhine",
        "lat": 50.1109,
        "lon": 8.6821,
    },
]


async def seed_stations() -> None:
    """Seed sample stations."""
    async with AsyncSessionLocal() as db:
        logger.info("Seeding stations...")
        
        for station_data in SAMPLE_STATIONS:
            # Check if station already exists
            result = await db.execute(
                select(Station).where(Station.code == station_data["code"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                station = Station(**station_data)
                db.add(station)
                logger.info(f"  ✓ Added station: {station.code} - {station.name}")
            else:
                logger.info(f"  - Station already exists: {station_data['code']}")
        
        await db.commit()
        logger.info(f"Seeded {len(SAMPLE_STATIONS)} stations")


async def seed_forecasts(num_forecasts: int = 50) -> None:
    """
    Seed sample forecasts.
    
    Args:
        num_forecasts: Number of forecast records to create per station
    """
    async with AsyncSessionLocal() as db:
        logger.info("Seeding forecasts...")
        
        # Get all stations
        result = await db.execute(select(Station))
        stations = result.scalars().all()
        
        if not stations:
            logger.warning("No stations found. Please seed stations first.")
            return
        
        total_forecasts = 0
        base_time = datetime.now(timezone.utc)
        
        for station in stations:
            for i in range(num_forecasts):
                # Create forecasts for different lead times
                lead_hours = [6, 12, 24, 48, 72][i % 5]
                forecast_time = base_time + timedelta(hours=i)
                
                # Simulate discharge values (100-2000 m³/s)
                import random
                discharge = random.uniform(100, 2000)
                
                forecast = Forecast(
                    station_id=station.id,
                    ts=forecast_time,
                    lead_hours=lead_hours,
                    discharge_m3s=discharge,
                    source="GloFAS",
                    model_run=base_time,
                )
                db.add(forecast)
                total_forecasts += 1
        
        await db.commit()
        logger.info(f"Seeded {total_forecasts} forecasts")


async def seed_alerts() -> None:
    """Seed sample alerts."""
    async with AsyncSessionLocal() as db:
        logger.info("Seeding alerts...")
        
        # Get all stations
        result = await db.execute(select(Station))
        stations = result.scalars().all()
        
        if not stations:
            logger.warning("No stations found. Please seed stations first.")
            return
        
        # Create one alert for the first station
        if stations:
            alert = Alert(
                station_id=stations[0].id,
                level="warning",
                probability=0.75,
                message="Elevated discharge forecast. Monitor conditions closely.",
                valid_from=datetime.now(timezone.utc),
                valid_until=datetime.now(timezone.utc) + timedelta(hours=48),
                is_active=True,
            )
            db.add(alert)
            await db.commit()
            logger.info(f"Seeded 1 alert for station: {stations[0].code}")


async def seed_all() -> None:
    """Seed all data."""
    logger.info("=" * 60)
    logger.info("SEEDING DATABASE")
    logger.info("=" * 60)
    
    await seed_stations()
    await seed_forecasts(num_forecasts=20)  # 20 forecasts per station
    await seed_alerts()
    
    logger.info("=" * 60)
    logger.info("DATABASE SEEDING COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    # Run seeding
    asyncio.run(seed_all())

