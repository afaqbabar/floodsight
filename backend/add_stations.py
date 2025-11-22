#!/usr/bin/env python3
"""Add more European stations to FloodSight"""

import sys
sys.path.insert(0, '/home/lenovo/scrimba/floodsight/backend')

import asyncio
from app.db.session import async_session_maker
from app.db.models import Station


# Major European river stations
NEW_STATIONS = [
    # Germany
    {"code": "RHINE-KOBLENZ", "name": "Koblenz Rhine", "river_basin": "Rhine", "lat": 50.3569, "lon": 7.5976},
    {"code": "RHINE-MAINZ", "name": "Mainz Rhine", "river_basin": "Rhine", "lat": 49.9929, "lon": 8.2473},
    {"code": "ELBE-MAGDEBURG", "name": "Magdeburg Elbe", "river_basin": "Elbe", "lat": 52.1205, "lon": 11.6276},
    
    # Netherlands
    {"code": "RHINE-LOBITH", "name": "Lobith Rhine", "river_basin": "Rhine", "lat": 51.8631, "lon": 6.1129},
    {"code": "MEUSE-MAASTRICHT", "name": "Maastricht Meuse", "river_basin": "Meuse", "lat": 50.8514, "lon": 5.6909},
    
    # France  
    {"code": "SEINE-PARIS", "name": "Paris Seine", "river_basin": "Seine", "lat": 48.8566, "lon": 2.3522},
    {"code": "RHONE-LYON", "name": "Lyon Rhone", "river_basin": "Rhone", "lat": 45.7640, "lon": 4.8357},
    {"code": "LOIRE-ORLEANS", "name": "Orleans Loire", "river_basin": "Loire", "lat": 47.9029, "lon": 1.9093},
    
    # Austria/Czech
    {"code": "DANUBE-LINZ", "name": "Linz Danube", "river_basin": "Danube", "lat": 48.3069, "lon": 14.2858},
    {"code": "ELBE-PRAGUE", "name": "Prague Vltava", "river_basin": "Elbe", "lat": 50.0755, "lon": 14.4378},
    
    # Italy
    {"code": "PO-TURIN", "name": "Turin Po", "river_basin": "Po", "lat": 45.0703, "lon": 7.6869},
    
    # Spain
    {"code": "EBRO-ZARAGOZA", "name": "Zaragoza Ebro", "river_basin": "Ebro", "lat": 41.6488, "lon": -0.8891},
]


async def add_stations():
    """Add new stations to database"""
    print("Adding new European stations...")
    print("=" * 60)
    
    async with async_session_maker() as db:
        added = 0
        skipped = 0
        
        for station_data in NEW_STATIONS:
            # Check if exists
            from sqlalchemy import select
            result = await db.execute(
                select(Station).where(Station.code == station_data["code"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⏭️  {station_data['code']:20} - Already exists")
                skipped += 1
                continue
            
            # Add new station
            station = Station(**station_data)
            db.add(station)
            print(f"✅ {station_data['code']:20} - {station_data['name']}")
            added += 1
        
        await db.commit()
        
        print("=" * 60)
        print(f"Added: {added} stations")
        print(f"Skipped: {skipped} stations (already exist)")
        print(f"Total new stations: {added}")
        
        # Show current total
        from sqlalchemy import func
        result = await db.execute(select(func.count(Station.id)))
        total = result.scalar()
        print(f"Total stations in database: {total}")


if __name__ == "__main__":
    asyncio.run(add_stations())



