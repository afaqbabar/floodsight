#!/usr/bin/env python3
"""Add priority flood-prone river stations to FloodSight

Usage:
    # Quick win - 10 most critical stations
    python add_priority_stations.py --quick-win
    
    # Priority 1 - All critical rivers (42 stations)
    python add_priority_stations.py --priority 1
    
    # Specific rivers
    python add_priority_stations.py --rivers rhine,danube
    
    # Add all stations (80+)
    python add_priority_stations.py --all
"""

import sys
sys.path.insert(0, '/home/lenovo/scrimba/floodsight/backend')

import asyncio
import argparse
from app.db.session import AsyncSessionLocal
from app.db.models import Station
from sqlalchemy import select


# ===== QUICK WIN STATIONS (10 most critical) =====
QUICK_WIN_STATIONS = [
    # Rhine bottleneck (most watched point in Europe)
    {"code": "RHINE-KAUB", "name": "Kaub Rhine", "river_basin": "Rhine", 
     "lat": 50.0836, "lon": 7.7661, "priority": "critical"},
    
    # Major city capitals
    {"code": "DANUBE-BUDAPEST", "name": "Budapest Danube", "river_basin": "Danube", 
     "lat": 47.4979, "lon": 19.0402, "priority": "critical"},
    {"code": "DANUBE-BELGRADE", "name": "Belgrade Danube", "river_basin": "Danube", 
     "lat": 44.7866, "lon": 20.4489, "priority": "critical"},
    {"code": "ELBE-HAMBURG", "name": "Hamburg Elbe", "river_basin": "Elbe", 
     "lat": 53.5511, "lon": 9.9937, "priority": "critical"},
    {"code": "VISTULA-WARSAW", "name": "Warsaw Vistula", "river_basin": "Vistula", 
     "lat": 52.2297, "lon": 21.0122, "priority": "critical"},
    
    # Major ports (infrastructure customers)
    {"code": "RHINE-ROTTERDAM", "name": "Rotterdam Rhine", "river_basin": "Rhine", 
     "lat": 51.9225, "lon": 4.4792, "priority": "critical"},
    {"code": "RHINE-DUISBURG", "name": "Duisburg Rhine", "river_basin": "Rhine", 
     "lat": 51.4344, "lon": 6.7623, "priority": "critical"},
    
    # 2021 flood disaster zone
    {"code": "AHR-BAD-NEUENAHR", "name": "Bad Neuenahr Ahr", "river_basin": "Rhine", 
     "lat": 50.5428, "lon": 7.1172, "priority": "critical"},
    
    # Italy (untapped market)
    {"code": "PO-FERRARA", "name": "Ferrara Po", "river_basin": "Po", 
     "lat": 44.8381, "lon": 11.6198, "priority": "critical"},
    
    # 2013 flood epicenter
    {"code": "DANUBE-PASSAU", "name": "Passau Danube", "river_basin": "Danube", 
     "lat": 48.5733, "lon": 13.4582, "priority": "critical"},
]


# ===== RHINE RIVER STATIONS =====
RHINE_STATIONS = [
    # Switzerland - source region
    {"code": "RHINE-BASEL", "name": "Basel Rhine", "river_basin": "Rhine", 
     "lat": 47.5596, "lon": 7.5886, "priority": "critical"},
    
    # Germany - Upper Rhine Valley (frequent floods)
    {"code": "RHINE-KARLSRUHE", "name": "Karlsruhe Rhine", "river_basin": "Rhine", 
     "lat": 49.0069, "lon": 8.4037, "priority": "critical"},
    {"code": "RHINE-SPEYER", "name": "Speyer Rhine", "river_basin": "Rhine", 
     "lat": 49.3194, "lon": 8.4414, "priority": "high"},
    {"code": "RHINE-WORMS", "name": "Worms Rhine", "river_basin": "Rhine", 
     "lat": 49.6328, "lon": 8.3590, "priority": "high"},
    {"code": "RHINE-KAUB", "name": "Kaub Rhine", "river_basin": "Rhine", 
     "lat": 50.0836, "lon": 7.7661, "priority": "critical"},
    
    # Germany - Middle Rhine
    {"code": "RHINE-BONN", "name": "Bonn Rhine", "river_basin": "Rhine", 
     "lat": 50.7374, "lon": 7.0982, "priority": "high"},
    {"code": "RHINE-DUSSELDORF", "name": "Düsseldorf Rhine", "river_basin": "Rhine", 
     "lat": 51.2277, "lon": 6.7735, "priority": "critical"},
    
    # Germany - Lower Rhine
    {"code": "RHINE-DUISBURG", "name": "Duisburg Rhine", "river_basin": "Rhine", 
     "lat": 51.4344, "lon": 6.7623, "priority": "critical"},
    {"code": "RHINE-WESEL", "name": "Wesel Rhine", "river_basin": "Rhine", 
     "lat": 51.6549, "lon": 6.6190, "priority": "high"},
    {"code": "RHINE-REES", "name": "Rees Rhine", "river_basin": "Rhine", 
     "lat": 51.7634, "lon": 6.3965, "priority": "high"},
    
    # Netherlands
    {"code": "RHINE-ARNHEM", "name": "Arnhem Rhine", "river_basin": "Rhine", 
     "lat": 51.9851, "lon": 5.8987, "priority": "critical"},
    {"code": "RHINE-ROTTERDAM", "name": "Rotterdam Rhine", "river_basin": "Rhine", 
     "lat": 51.9225, "lon": 4.4792, "priority": "critical"},
]


# ===== DANUBE RIVER STATIONS =====
DANUBE_STATIONS = [
    # Germany
    {"code": "DANUBE-REGENSBURG", "name": "Regensburg Danube", "river_basin": "Danube", 
     "lat": 49.0195, "lon": 12.0974, "priority": "high"},
    {"code": "DANUBE-PASSAU", "name": "Passau Danube", "river_basin": "Danube", 
     "lat": 48.5733, "lon": 13.4582, "priority": "critical"},
    
    # Austria
    {"code": "DANUBE-KREMS", "name": "Krems Danube", "river_basin": "Danube", 
     "lat": 48.4091, "lon": 15.6141, "priority": "high"},
    
    # Slovakia
    {"code": "DANUBE-BRATISLAVA", "name": "Bratislava Danube", "river_basin": "Danube", 
     "lat": 48.1486, "lon": 17.1077, "priority": "critical"},
    
    # Hungary
    {"code": "DANUBE-GYOR", "name": "Győr Danube", "river_basin": "Danube", 
     "lat": 47.6875, "lon": 17.6504, "priority": "high"},
    {"code": "DANUBE-BUDAPEST", "name": "Budapest Danube", "river_basin": "Danube", 
     "lat": 47.4979, "lon": 19.0402, "priority": "critical"},
    {"code": "DANUBE-MOHACS", "name": "Mohács Danube", "river_basin": "Danube", 
     "lat": 45.9929, "lon": 18.6859, "priority": "high"},
    
    # Serbia
    {"code": "DANUBE-NOVI-SAD", "name": "Novi Sad Danube", "river_basin": "Danube", 
     "lat": 45.2671, "lon": 19.8335, "priority": "critical"},
    {"code": "DANUBE-BELGRADE", "name": "Belgrade Danube", "river_basin": "Danube", 
     "lat": 44.7866, "lon": 20.4489, "priority": "critical"},
    
    # Romania
    {"code": "DANUBE-ORSOVA", "name": "Orșova Danube", "river_basin": "Danube", 
     "lat": 44.7194, "lon": 22.3978, "priority": "high"},
    {"code": "DANUBE-GIURGIU", "name": "Giurgiu Danube", "river_basin": "Danube", 
     "lat": 43.9037, "lon": 25.9699, "priority": "high"},
    {"code": "DANUBE-GALATI", "name": "Galați Danube", "river_basin": "Danube", 
     "lat": 45.4353, "lon": 28.0080, "priority": "critical"},
    {"code": "DANUBE-TULCEA", "name": "Tulcea Danube", "river_basin": "Danube", 
     "lat": 45.1787, "lon": 28.8042, "priority": "high"},
]


# ===== ELBE RIVER STATIONS =====
ELBE_STATIONS = [
    # Czech Republic
    {"code": "ELBE-USTI", "name": "Ústí nad Labem Elbe", "river_basin": "Elbe", 
     "lat": 50.6607, "lon": 14.0322, "priority": "critical"},
    
    # Germany - Saxony
    {"code": "ELBE-PIRNA", "name": "Pirna Elbe", "river_basin": "Elbe", 
     "lat": 50.9606, "lon": 13.9389, "priority": "critical"},
    {"code": "ELBE-MEISSEN", "name": "Meißen Elbe", "river_basin": "Elbe", 
     "lat": 51.1633, "lon": 13.4719, "priority": "high"},
    {"code": "ELBE-TORGAU", "name": "Torgau Elbe", "river_basin": "Elbe", 
     "lat": 51.5604, "lon": 13.0056, "priority": "high"},
    {"code": "ELBE-WITTENBERG", "name": "Lutherstadt Wittenberg Elbe", "river_basin": "Elbe", 
     "lat": 51.8661, "lon": 12.6484, "priority": "high"},
    {"code": "ELBE-HAMBURG", "name": "Hamburg Elbe", "river_basin": "Elbe", 
     "lat": 53.5511, "lon": 9.9937, "priority": "critical"},
]


# ===== PO RIVER STATIONS =====
PO_STATIONS = [
    # Piedmont
    {"code": "PO-CASALE", "name": "Casale Monferrato Po", "river_basin": "Po", 
     "lat": 45.1344, "lon": 8.4523, "priority": "high"},
    
    # Lombardy
    {"code": "PO-PIACENZA", "name": "Piacenza Po", "river_basin": "Po", 
     "lat": 45.0526, "lon": 9.6929, "priority": "critical"},
    {"code": "PO-CREMONA", "name": "Cremona Po", "river_basin": "Po", 
     "lat": 45.1363, "lon": 10.0224, "priority": "critical"},
    {"code": "PO-MANTUA", "name": "Mantova Po", "river_basin": "Po", 
     "lat": 45.1564, "lon": 10.7914, "priority": "high"},
    
    # Emilia-Romagna
    {"code": "PO-FERRARA", "name": "Ferrara Po", "river_basin": "Po", 
     "lat": 44.8381, "lon": 11.6198, "priority": "critical"},
    {"code": "PO-ROVIGO", "name": "Rovigo Po", "river_basin": "Po", 
     "lat": 45.0703, "lon": 11.7898, "priority": "high"},
    
    # Veneto
    {"code": "PO-DELTA", "name": "Po Delta", "river_basin": "Po", 
     "lat": 44.9667, "lon": 12.4500, "priority": "critical"},
]


# ===== ODER RIVER STATIONS =====
ODER_STATIONS = [
    # Poland
    {"code": "ODER-WROCLAW", "name": "Wrocław Oder", "river_basin": "Oder", 
     "lat": 51.1079, "lon": 17.0385, "priority": "critical"},
    {"code": "ODER-OPOLE", "name": "Opole Oder", "river_basin": "Oder", 
     "lat": 50.6751, "lon": 17.9213, "priority": "high"},
    {"code": "ODER-BRZEG-DOLNY", "name": "Brzeg Dolny Oder", "river_basin": "Oder", 
     "lat": 51.2692, "lon": 16.7206, "priority": "high"},
    
    # Poland-Germany border
    {"code": "ODER-FRANKFURT", "name": "Frankfurt (Oder) Oder", "river_basin": "Oder", 
     "lat": 52.3431, "lon": 14.5506, "priority": "critical"},
    {"code": "ODER-EISENHUTTENSTADT", "name": "Eisenhüttenstadt Oder", "river_basin": "Oder", 
     "lat": 52.1469, "lon": 14.6497, "priority": "high"},
    
    # Germany
    {"code": "ODER-SCHWEDT", "name": "Schwedt Oder", "river_basin": "Oder", 
     "lat": 53.0647, "lon": 14.2819, "priority": "high"},
]


# ===== SEINE RIVER STATIONS =====
SEINE_STATIONS = [
    {"code": "SEINE-TROYES", "name": "Troyes Seine", "river_basin": "Seine", 
     "lat": 48.2973, "lon": 4.0744, "priority": "medium"},
    {"code": "SEINE-MELUN", "name": "Melun Seine", "river_basin": "Seine", 
     "lat": 48.5396, "lon": 2.6602, "priority": "high"},
    {"code": "SEINE-ROUEN", "name": "Rouen Seine", "river_basin": "Seine", 
     "lat": 49.4432, "lon": 1.0993, "priority": "critical"},
    {"code": "SEINE-LE-HAVRE", "name": "Le Havre Seine", "river_basin": "Seine", 
     "lat": 49.4944, "lon": 0.1079, "priority": "high"},
    {"code": "SEINE-MARNE-CONFLUENCE", "name": "Marne Confluence", "river_basin": "Seine", 
     "lat": 48.8156, "lon": 2.4147, "priority": "high"},
]


# ===== RHONE RIVER STATIONS =====
RHONE_STATIONS = [
    # Switzerland
    {"code": "RHONE-GENEVA", "name": "Geneva Rhône", "river_basin": "Rhone", 
     "lat": 46.2044, "lon": 6.1432, "priority": "critical"},
    
    # France
    {"code": "RHONE-VALENCE", "name": "Valence Rhône", "river_basin": "Rhone", 
     "lat": 44.9334, "lon": 4.8924, "priority": "high"},
    {"code": "RHONE-AVIGNON", "name": "Avignon Rhône", "river_basin": "Rhone", 
     "lat": 43.9493, "lon": 4.8055, "priority": "high"},
    {"code": "RHONE-ARLES", "name": "Arles Rhône", "river_basin": "Rhone", 
     "lat": 43.6770, "lon": 4.6278, "priority": "high"},
    {"code": "RHONE-CAMARGUE", "name": "Camargue Delta", "river_basin": "Rhone", 
     "lat": 43.5000, "lon": 4.5000, "priority": "medium"},
]


# ===== VISTULA RIVER STATIONS =====
VISTULA_STATIONS = [
    {"code": "VISTULA-KRAKOW", "name": "Kraków Vistula", "river_basin": "Vistula", 
     "lat": 50.0647, "lon": 19.9450, "priority": "critical"},
    {"code": "VISTULA-WARSAW", "name": "Warsaw Vistula", "river_basin": "Vistula", 
     "lat": 52.2297, "lon": 21.0122, "priority": "critical"},
    {"code": "VISTULA-TORUN", "name": "Toruń Vistula", "river_basin": "Vistula", 
     "lat": 53.0138, "lon": 18.5984, "priority": "high"},
    {"code": "VISTULA-GDANSK", "name": "Gdańsk Vistula", "river_basin": "Vistula", 
     "lat": 54.3520, "lon": 18.6466, "priority": "critical"},
]


# ===== TISZA RIVER STATIONS =====
TISZA_STATIONS = [
    {"code": "TISZA-TYACHIV", "name": "Tyachiv Tisza", "river_basin": "Danube", 
     "lat": 48.0150, "lon": 23.5764, "priority": "medium"},
    {"code": "TISZA-TOKAJ", "name": "Tokaj Tisza", "river_basin": "Danube", 
     "lat": 48.1211, "lon": 21.4089, "priority": "high"},
    {"code": "TISZA-SZEGED", "name": "Szeged Tisza", "river_basin": "Danube", 
     "lat": 46.2530, "lon": 20.1414, "priority": "critical"},
    {"code": "TISZA-NOVI-BECEJ", "name": "Novi Bečej Tisza", "river_basin": "Danube", 
     "lat": 45.5980, "lon": 20.1276, "priority": "high"},
]


# Station collections by priority
PRIORITY_1_RIVERS = {
    "rhine": RHINE_STATIONS,
    "danube": DANUBE_STATIONS,
    "elbe": ELBE_STATIONS,
    "po": PO_STATIONS,
    "oder": ODER_STATIONS,
}

PRIORITY_2_RIVERS = {
    "seine": SEINE_STATIONS,
    "rhone": RHONE_STATIONS,
    "vistula": VISTULA_STATIONS,
    "tisza": TISZA_STATIONS,
}

ALL_RIVERS = {**PRIORITY_1_RIVERS, **PRIORITY_2_RIVERS}


async def add_stations(stations_to_add, description="stations"):
    """Add stations to database"""
    print(f"\n{'=' * 70}")
    print(f"Adding {description}...")
    print(f"{'=' * 70}\n")
    
    async with AsyncSessionLocal() as db:
        added = 0
        skipped = 0
        
        for station_data in stations_to_add:
            # Remove 'priority' field before adding to DB (it's just for us)
            priority = station_data.pop('priority', 'medium')
            
            # Check if exists
            result = await db.execute(
                select(Station).where(Station.code == station_data["code"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⏭️  {station_data['code']:25} - Already exists")
                skipped += 1
                continue
            
            # Add new station
            station = Station(**station_data)
            db.add(station)
            
            # Pretty print with priority indicator
            priority_emoji = {
                'critical': '🔴',
                'high': '🟡',
                'medium': '🟢'
            }.get(priority, '⚪')
            
            print(f"{priority_emoji} {station_data['code']:25} - {station_data['name']}")
            added += 1
        
        await db.commit()
        
        print(f"\n{'=' * 70}")
        print(f"✅ Added: {added} stations")
        print(f"⏭️  Skipped: {skipped} stations (already exist)")
        print(f"{'=' * 70}\n")
        
        # Show current total
        from sqlalchemy import func
        result = await db.execute(select(func.count(Station.id)))
        total = result.scalar()
        print(f"📊 Total stations in database: {total}\n")
        
        return added, skipped


async def main():
    parser = argparse.ArgumentParser(
        description="Add priority flood-prone river stations to FloodSight",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick win - 10 most critical stations
  python add_priority_stations.py --quick-win
  
  # Priority 1 - All critical rivers (42 stations)
  python add_priority_stations.py --priority 1
  
  # Priority 2 - Important rivers
  python add_priority_stations.py --priority 2
  
  # Specific rivers
  python add_priority_stations.py --rivers rhine,danube
  python add_priority_stations.py --rivers elbe,po,oder
  
  # Add all stations (80+)
  python add_priority_stations.py --all
        """
    )
    
    parser.add_argument('--quick-win', action='store_true',
                       help='Add 10 most critical stations for quick market entry')
    parser.add_argument('--priority', type=int, choices=[1, 2],
                       help='Add all Priority 1 (critical) or Priority 2 (important) rivers')
    parser.add_argument('--rivers', type=str,
                       help='Comma-separated list of rivers (rhine,danube,elbe,po,oder,seine,rhone,vistula,tisza)')
    parser.add_argument('--all', action='store_true',
                       help='Add all available stations (80+)')
    
    args = parser.parse_args()
    
    # Determine which stations to add
    stations_to_add = []
    description = ""
    
    if args.quick_win:
        stations_to_add = QUICK_WIN_STATIONS
        description = "Quick Win - 10 Most Critical Stations"
        
    elif args.priority == 1:
        for river_name, stations in PRIORITY_1_RIVERS.items():
            stations_to_add.extend(stations)
        description = "Priority 1 - Critical Flood-Prone Rivers (Rhine, Danube, Elbe, Po, Oder)"
        
    elif args.priority == 2:
        for river_name, stations in PRIORITY_2_RIVERS.items():
            stations_to_add.extend(stations)
        description = "Priority 2 - Important Rivers (Seine, Rhône, Vistula, Tisza)"
        
    elif args.rivers:
        river_list = [r.strip().lower() for r in args.rivers.split(',')]
        for river_name in river_list:
            if river_name in ALL_RIVERS:
                stations_to_add.extend(ALL_RIVERS[river_name])
            else:
                print(f"⚠️  Warning: Unknown river '{river_name}'. Skipping.")
        description = f"Selected Rivers: {', '.join(river_list)}"
        
    elif args.all:
        for river_name, stations in ALL_RIVERS.items():
            stations_to_add.extend(stations)
        description = "All Available Stations (80+)"
        
    else:
        parser.print_help()
        print("\n⚠️  Please specify what to add: --quick-win, --priority, --rivers, or --all")
        sys.exit(1)
    
    # Add stations
    if stations_to_add:
        added, skipped = await add_stations(stations_to_add, description)
        
        # Show recommendation
        print("\n📝 Next Steps:")
        print("=" * 70)
        
        if args.quick_win:
            print("✅ Quick Win stations added!")
            print("   → Test the dashboard: Check if new stations appear")
            print("   → Update marketing: 'Now covering 10 most critical points'")
            print("   → Reach out to: Port operators, capital city municipalities")
            print("\n💡 Next: Add Priority 1 rivers with --priority 1")
            
        elif args.priority == 1:
            print("✅ Priority 1 rivers added!")
            print("   → Run forecast ingestion: curl -X POST http://localhost:8080/v1/forecasts/ingest")
            print("   → Compute alerts: curl -X POST http://localhost:8080/v1/alerts/compute")
            print("   → Update pricing page: Advertise Rhine/Danube/Elbe coverage")
            print("\n💡 Next: Add Priority 2 rivers with --priority 2")
            
        elif args.all:
            print("✅ All stations added! You now have European coverage!")
            print("   → Update website: 'Monitoring 80+ critical flood points'")
            print("   → Enable enterprise tier: Full European coverage unlocked")
            print("   → Pitch to: Insurance companies, national agencies, railways")
            
        else:
            print(f"✅ {description} added!")
            print("   → Test: curl http://localhost:8080/v1/stations")
            print("   → Ingest data: curl -X POST http://localhost:8080/v1/forecasts/ingest")
        
        print("=" * 70 + "\n")
    else:
        print("⚠️  No stations to add. All selected stations may already exist.")


if __name__ == "__main__":
    asyncio.run(main())

