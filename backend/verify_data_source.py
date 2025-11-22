#!/usr/bin/env python3
"""
FloodSight Data Source Verification Script

This script checks whether your system is using REAL GloFAS data
from ECMWF Copernicus or FAKE synthetic data.

Usage:
    python verify_data_source.py
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

# Add app to path
sys.path.insert(0, '/home/lenovo/scrimba/floodsight/backend')

from app.db.session import async_session_maker
from app.db.models import Forecast, Station
from app.core.config import settings


async def verify_data_source():
    """Check if forecasts are real or fake."""
    
    print("=" * 70)
    print("🔍 FLOODSIGHT DATA SOURCE VERIFICATION")
    print("=" * 70)
    print()
    
    async with async_session_maker() as db:
        # 1. Check configuration
        print("📋 CONFIGURATION CHECK")
        print("-" * 70)
        print(f"GLOFAS_INGEST_MODE: {settings.GLOFAS_INGEST_MODE}")
        print(f"CDS_API_URL: {settings.CDS_API_URL}")
        print(f"CDS_API_KEY: {'✅ SET' if settings.CDS_API_KEY else '❌ NOT SET'}")
        print(f"CDS_API_KEY (first 10 chars): {settings.CDS_API_KEY[:10]}..." if settings.CDS_API_KEY else "")
        print()
        
        # 2. Check database forecasts
        print("📊 DATABASE FORECAST CHECK")
        print("-" * 70)
        
        # Count total forecasts
        result = await db.execute(select(func.count(Forecast.id)))
        total_forecasts = result.scalar()
        print(f"Total forecasts in database: {total_forecasts}")
        
        if total_forecasts == 0:
            print("⚠️  No forecasts found! Run ingestion first.")
            return
        
        # Count by source
        result = await db.execute(
            select(Forecast.source, func.count(Forecast.id))
            .group_by(Forecast.source)
        )
        sources = result.all()
        
        print("\nForecasts by source:")
        for source, count in sources:
            emoji = "✅" if source == "GloFAS" else "⚠️"
            print(f"  {emoji} {source}: {count} records")
        
        # 3. Check most recent forecast
        print("\n🕒 MOST RECENT FORECAST")
        print("-" * 70)
        
        result = await db.execute(
            select(Forecast)
            .order_by(Forecast.created_at.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        
        if latest:
            print(f"Source: {latest.source}")
            print(f"Model Run: {latest.model_run}")
            print(f"Forecast Time: {latest.ts}")
            print(f"Lead Hours: {latest.lead_hours}")
            print(f"Discharge: {latest.discharge_m3s} m³/s")
            print(f"Created At: {latest.created_at}")
            
            # 4. Data pattern analysis
            print("\n🔬 DATA PATTERN ANALYSIS")
            print("-" * 70)
            
            # Check if model_run is recent (real data should be from latest GloFAS run)
            now = datetime.now(timezone.utc)
            if latest.model_run:
                age_hours = (now - latest.model_run).total_seconds() / 3600
                print(f"Model run age: {age_hours:.1f} hours")
                
                if age_hours < 48:
                    print("✅ Model run is recent (< 48 hours old)")
                else:
                    print("⚠️  Model run is old (> 48 hours) - may need update")
            
            # Check discharge values (fake data has specific patterns)
            result = await db.execute(
                select(
                    func.min(Forecast.discharge_m3s),
                    func.max(Forecast.discharge_m3s),
                    func.avg(Forecast.discharge_m3s),
                )
                .where(Forecast.station_id == latest.station_id)
                .where(Forecast.model_run == latest.model_run)
            )
            min_q, max_q, avg_q = result.one()
            
            print(f"\nDischarge statistics for station {latest.station_id}:")
            print(f"  Min: {min_q:.2f} m³/s")
            print(f"  Max: {max_q:.2f} m³/s")
            print(f"  Avg: {avg_q:.2f} m³/s")
            
            # Fake data has high variability (random), real data is smoother
            result = await db.execute(
                select(Forecast.discharge_m3s, Forecast.lead_hours)
                .where(Forecast.station_id == latest.station_id)
                .where(Forecast.model_run == latest.model_run)
                .order_by(Forecast.lead_hours)
            )
            values = [(row[0], row[1]) for row in result.all()]
            
            if len(values) > 1:
                # Calculate variance
                changes = [abs(values[i][0] - values[i-1][0]) for i in range(1, len(values))]
                avg_change = sum(changes) / len(changes) if changes else 0
                print(f"  Avg change between timesteps: {avg_change:.2f} m³/s")
                
                if avg_change > 100:
                    print("  ⚠️  High variability - may be synthetic data")
                else:
                    print("  ✅ Smooth progression - typical of real forecasts")
        
        # 5. Check all stations
        print("\n🗺️  STATION COVERAGE")
        print("-" * 70)
        
        result = await db.execute(
            select(Station.code, Station.name, func.count(Forecast.id))
            .join(Forecast, Station.id == Forecast.station_id)
            .group_by(Station.id, Station.code, Station.name)
        )
        station_counts = result.all()
        
        for code, name, count in station_counts:
            print(f"  {code} ({name}): {count} forecasts")
        
        # 6. Final verdict
        print("\n" + "=" * 70)
        print("🎯 VERDICT")
        print("=" * 70)
        
        if not settings.CDS_API_KEY:
            print("❌ FAKE DATA - No CDS API key configured")
            print("\nTo enable real data:")
            print("1. Get API key from https://cds.climate.copernicus.eu")
            print("2. Add to backend/.env or docker-compose.yml")
            print("3. Restart backend")
        elif latest and latest.source == "GloFAS-fake":
            print("❌ FAKE DATA - Source field indicates synthetic data")
            print("\nPossible reasons:")
            print("- API credentials invalid")
            print("- CDS service unavailable")
            print("- GLOFAS_INGEST_MODE set to 'fake'")
            print("\nCheck backend logs: docker compose logs api | grep -i glofas")
        elif latest and latest.source == "GloFAS":
            print("✅ REAL DATA - Using live GloFAS forecasts from ECMWF!")
            print("\nData characteristics:")
            print(f"- Latest model run: {latest.model_run}")
            print(f"- Total forecasts: {total_forecasts}")
            print(f"- Stations covered: {len(station_counts)}")
            print("\n🎉 Your system is operational with real flood data!")
        else:
            print("⚠️  UNKNOWN - Unable to determine data source")
        
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(verify_data_source())





