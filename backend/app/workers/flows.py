"""
Scheduled workflows for automated data ingestion and alert computation.

This module provides scheduled tasks using APScheduler (alternative to Prefect
due to version conflicts with FastAPI).

Usage:
    # Run manually
    python -m app.workers.flows

    # Or via Docker
    docker compose up scheduler
"""
import asyncio
import signal
import sys
from datetime import datetime, timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.session import AsyncSessionLocal
from app.services.alerts import create_alerts_from_forecasts
from app.services.glefas import ingest_forecasts
from app.services.sentinel1 import ingest_sentinel1_with_vessels

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def fetch_and_store_forecasts() -> int:
    """
    Fetch and store forecast data.
    
    Returns:
        Number of forecasts ingested
    """
    logger.info("=" * 60)
    logger.info(f"FORECAST INGESTION STARTED - {datetime.now(timezone.utc)}")
    logger.info("=" * 60)
    
    try:
        async with AsyncSessionLocal() as db:
            forecast_count, ingestion_mode = await ingest_forecasts(db)
            logger.info(
                "✅ Ingested %s forecasts (mode=%s)", forecast_count, ingestion_mode
            )
            return forecast_count
    except Exception as e:
        logger.error(f"❌ Forecast ingestion failed: {e}", exc_info=True)
        return 0


async def compute_and_store_alerts() -> int:
    """
    Compute and store alert data.
    
    Returns:
        Number of alerts created
    """
    logger.info("=" * 60)
    logger.info(f"ALERT COMPUTATION STARTED - {datetime.now(timezone.utc)}")
    logger.info("=" * 60)
    
    try:
        async with AsyncSessionLocal() as db:
            alerts_count = await create_alerts_from_forecasts(db)
            logger.info(f"✅ Created {alerts_count} alerts")
            return alerts_count
    except Exception as e:
        logger.error(f"❌ Alert computation failed: {e}", exc_info=True)
        return 0


async def process_sentinel1_vessels() -> int:
    """
    Process Sentinel-1 SAR scenes for vessel detection.
    
    Returns:
        Number of vessel detections
    """
    logger.info("=" * 60)
    logger.info(f"SENTINEL-1 VESSEL DETECTION STARTED - {datetime.now(timezone.utc)}")
    logger.info("=" * 60)
    
    try:
        async with AsyncSessionLocal() as db:
            vessel_count = await ingest_sentinel1_with_vessels(db)
            logger.info(f"✅ Detected {vessel_count} vessels")
            return vessel_count
    except Exception as e:
        logger.error(f"❌ Sentinel-1 vessel detection failed: {e}", exc_info=True)
        return 0


async def run_complete_flow() -> tuple[int, int, int]:
    """
    Complete ingestion flow: Ingest forecasts + Compute alerts + Detect vessels.
    
    Returns:
        Tuple of (forecast_count, alerts_count, vessel_count)
    """
    logger.info("🌊 FloodSight Complete Ingestion Flow Started")
    
    try:
        # Step 1: Ingest forecasts
        forecast_count = await fetch_and_store_forecasts()
        
        # Step 2: Compute alerts from new forecasts
        alerts_count = 0
        if forecast_count > 0:
            alerts_count = await compute_and_store_alerts()
        else:
            logger.warning("⚠️ No forecasts ingested, skipping alert computation")
        
        # Step 3: Process Sentinel-1 for vessel detection (maritime extension)
        vessel_count = await process_sentinel1_vessels()
        
        logger.info(
            f"🎉 Flow completed: {forecast_count} forecasts, {alerts_count} alerts, {vessel_count} vessels"
        )
        
        logger.info("=" * 60)
        logger.info(f"FLOW COMPLETED - {datetime.now(timezone.utc)}")
        logger.info("=" * 60)
        
        return forecast_count, alerts_count, vessel_count
        
    except Exception as e:
        logger.error(f"❌ Flow failed: {e}", exc_info=True)
        return 0, 0, 0


def floodsight_ingest_flow() -> None:
    """
    Main ingestion flow wrapper for scheduler.
    
    This is the scheduled job that runs periodically.
    """
    asyncio.run(run_complete_flow())


def run_scheduler() -> None:
    """
    Run the scheduler with configured jobs.
    
    Default schedule:
    - Hourly ingestion (every hour at :00)
    - Can be customized via environment variables
    """
    scheduler = BlockingScheduler()
    
    # Schedule the ingestion flow
    # Default: Every hour at the top of the hour
    # Can be changed to: "0 */3 * * *" for every 3 hours, etc.
    schedule = "0 * * * *"  # Cron format: minute hour day month weekday
    
    scheduler.add_job(
        floodsight_ingest_flow,
        trigger=CronTrigger.from_crontab(schedule),
        id="floodsight_ingest_flow",
        name="FloodSight Forecast Ingestion & Alert Computation",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
    )
    
    logger.info("🚀 FloodSight Scheduler Starting")
    logger.info(f"📅 Schedule: {schedule} (hourly at :00)")
    logger.info(f"⚙️  Environment: {settings.ENVIRONMENT}")
    logger.info(f"🗄️  Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    logger.info("=" * 60)
    logger.info("Press Ctrl+C to stop the scheduler")
    logger.info("=" * 60)
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("🛑 Shutdown signal received, stopping scheduler...")
        scheduler.shutdown(wait=True)
        logger.info("👋 Scheduler stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run initial job immediately on startup
        logger.info("▶️  Running initial ingestion job...")
        floodsight_ingest_flow()
        
        # Start scheduler
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # If run directly, can accept arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "once":
            # Run once and exit (useful for testing)
            logger.info("Running ingestion flow once...")
            floodsight_ingest_flow()
        elif command == "schedule":
            # Run scheduler (default)
            run_scheduler()
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Usage: python -m app.workers.flows [once|schedule]")
            sys.exit(1)
    else:
        # Default: run scheduler
        run_scheduler()

