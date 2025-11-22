#!/usr/bin/env python3
"""
Manual Forecast Verification Tool

Simple script to compare forecasts and check accuracy.
"""

import sys
sys.path.insert(0, '/home/lenovo/scrimba/floodsight/backend')

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.db.models import Forecast, Station


async def compare_forecast_runs():
    """
    Compare older forecasts with newer ones for the same time period.
    This shows if forecasts converge (get more accurate) as we get closer.
    """
    print("=" * 80)
    print("📊 FORECAST CONVERGENCE ANALYSIS")
    print("=" * 80)
    print()
    
    async with async_session_maker() as db:
        # Get all unique target times that have multiple forecasts
        result = await db.execute(
            select(Forecast.ts, func.count(Forecast.id))
            .where(Forecast.source == 'GloFAS')
            .group_by(Forecast.ts)
            .having(func.count(Forecast.id) > 1)
            .order_by(Forecast.ts.desc())
            .limit(5)
        )
        target_times = [row[0] for row in result.all()]
        
        if not target_times:
            print("⚠️  No overlapping forecasts found yet.")
            print("   You need at least 2 forecast runs for the same target time.")
            print()
            return
        
        print(f"Found {len(target_times)} times with multiple forecasts\n")
        
        # Analyze first target time
        target = target_times[0]
        print(f"Target Time: {target}")
        print("-" * 80)
        
        # Get all forecasts for this target time
        result = await db.execute(
            select(Forecast, Station)
            .join(Station, Forecast.station_id == Station.id)
            .where(Forecast.ts == target)
            .where(Forecast.source == 'GloFAS')
            .order_by(Station.code, Forecast.lead_hours)
        )
        forecasts = result.all()
        
        # Group by station
        by_station = {}
        for forecast, station in forecasts:
            if station.code not in by_station:
                by_station[station.code] = []
            by_station[station.code].append(forecast)
        
        # Analyze each station
        for station_code, station_forecasts in by_station.items():
            print(f"\n📍 Station: {station_code}")
            print(f"   Number of forecasts: {len(station_forecasts)}")
            
            # Sort by lead time (shortest = closest to event)
            station_forecasts.sort(key=lambda f: f.lead_hours)
            
            # Show convergence
            print(f"   Lead Time | Discharge | Difference from shortest lead")
            print(f"   ----------|-----------|---------------------------")
            
            # Use shortest lead time as "truth"
            reference = station_forecasts[0].discharge_m3s
            
            for fc in station_forecasts[:5]:  # Show first 5
                diff = fc.discharge_m3s - reference
                diff_pct = (abs(diff) / reference * 100) if reference > 0 else 0
                
                print(f"   {fc.lead_hours:>6}h   | {fc.discharge_m3s:>7.2f}  | "
                      f"{diff:>+7.2f} ({diff_pct:>5.1f}%)")


async def show_forecast_statistics():
    """Show basic statistics about your forecasts."""
    print("\n")
    print("=" * 80)
    print("📈 FORECAST STATISTICS")
    print("=" * 80)
    print()
    
    async with async_session_maker() as db:
        # Count forecasts
        result = await db.execute(
            select(func.count(Forecast.id))
            .where(Forecast.source == 'GloFAS')
        )
        total = result.scalar()
        print(f"Total GloFAS forecasts: {total}")
        
        # Forecasts by station
        result = await db.execute(
            select(Station.code, Station.name, func.count(Forecast.id))
            .join(Forecast, Station.id == Forecast.station_id)
            .where(Forecast.source == 'GloFAS')
            .group_by(Station.id, Station.code, Station.name)
            .order_by(Station.code)
        )
        
        print("\nForecasts by Station:")
        print("-" * 60)
        for code, name, count in result.all():
            print(f"  {code:15} {name:20} {count:>5} forecasts")
        
        # Lead time distribution
        result = await db.execute(
            select(Forecast.lead_hours, func.count(Forecast.id))
            .where(Forecast.source == 'GloFAS')
            .group_by(Forecast.lead_hours)
            .order_by(Forecast.lead_hours)
        )
        
        print("\nLead Time Distribution:")
        print("-" * 60)
        for lead, count in result.all():
            bar = "█" * int(count / 2)
            print(f"  {lead:>3}h: {bar} ({count})")
        
        # Discharge range
        result = await db.execute(
            select(
                func.min(Forecast.discharge_m3s),
                func.max(Forecast.discharge_m3s),
                func.avg(Forecast.discharge_m3s)
            )
            .where(Forecast.source == 'GloFAS')
        )
        min_q, max_q, avg_q = result.one()
        
        print(f"\nDischarge Range:")
        print("-" * 60)
        print(f"  Minimum: {min_q:.2f} m³/s")
        print(f"  Maximum: {max_q:.2f} m³/s")
        print(f"  Average: {avg_q:.2f} m³/s")


async def show_sample_comparison():
    """Show example of how to manually verify accuracy."""
    print("\n")
    print("=" * 80)
    print("🔍 MANUAL VERIFICATION EXAMPLE")
    print("=" * 80)
    print()
    
    print("To manually verify forecast accuracy:")
    print()
    print("1. Pick a forecast from the past:")
    print("   - Model run: 2025-11-11")
    print("   - Predicted for: 2025-11-12 12:00")
    print("   - Discharge: 1200 m³/s")
    print()
    print("2. Get GloFAS Reanalysis for that time:")
    print("   - Go to: https://cds.climate.copernicus.eu")
    print("   - Dataset: CEMS GloFAS historical (reanalysis)")
    print("   - Date: 2025-11-12")
    print("   - Same location coordinates")
    print()
    print("3. Compare the values:")
    print("   - Forecast: 1200 m³/s")
    print("   - Reanalysis: 1150 m³/s")
    print("   - Error: 50 m³/s (4.2%)")
    print()
    print("4. Calculate metrics:")
    print("   - MAE (Mean Absolute Error) = |forecast - reanalysis|")
    print("   - Bias = forecast - reanalysis (positive = over-prediction)")
    print("   - Accuracy % = 100 - (error / reanalysis * 100)")
    print()


async def main():
    """Run all verification checks."""
    await show_forecast_statistics()
    await compare_forecast_runs()
    await show_sample_comparison()
    
    print("\n")
    print("=" * 80)
    print("💡 NEXT STEPS")
    print("=" * 80)
    print()
    print("For better verification, you need:")
    print()
    print("Option 1: Wait for more forecast runs")
    print("  - Multiple forecasts for same time → convergence analysis")
    print("  - Run ingestion hourly for best results")
    print()
    print("Option 2: Download GloFAS Reanalysis manually")
    print("  - Visit: https://cds.climate.copernicus.eu")
    print("  - Compare with your forecasts manually")
    print()
    print("Option 3: Implement automated verification")
    print("  - Auto-download reanalysis")
    print("  - Auto-calculate metrics")
    print("  - Dashboard showing accuracy over time")
    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())




