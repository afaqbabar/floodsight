#!/bin/bash
# Quick verification script for FloodSight data source

echo "🔍 FloodSight Data Source Verification"
echo "========================================"
echo ""

# Change to backend directory
cd "$(dirname "$0")/backend" || exit 1

# Check if Docker is running
if ! docker compose ps | grep -q "api.*running"; then
    echo "❌ Backend is not running!"
    echo "Start it with: cd backend && docker compose up -d"
    exit 1
fi

echo "1️⃣  Checking backend logs for ingestion mode..."
echo "------------------------------------------------"
docker compose logs api | grep -i "GloFAS ingestion mode\|Starting.*forecast ingestion\|Ingested.*forecast" | tail -n 5
echo ""

echo "2️⃣  Checking database for forecast sources..."
echo "------------------------------------------------"
docker compose exec -T db psql -U floodsight -d floodsight -c \
    "SELECT source, COUNT(*) as count, MAX(created_at) as latest 
     FROM forecasts 
     GROUP BY source 
     ORDER BY latest DESC;"
echo ""

echo "3️⃣  Checking most recent forecast details..."
echo "------------------------------------------------"
docker compose exec -T db psql -U floodsight -d floodsight -c \
    "SELECT 
        f.source, 
        f.model_run, 
        f.lead_hours,
        f.discharge_m3s,
        s.code as station,
        f.created_at
     FROM forecasts f
     JOIN stations s ON f.station_id = s.id
     ORDER BY f.created_at DESC 
     LIMIT 5;" -x
echo ""

echo "4️⃣  Running Python verification script..."
echo "------------------------------------------------"
docker compose exec -T api python /app/verify_data_source.py

echo ""
echo "✅ Verification complete!"
echo ""
echo "💡 Tips:"
echo "  - 'GloFAS' source = REAL data from ECMWF"
echo "  - 'GloFAS-fake' source = Synthetic test data"
echo "  - Check logs: docker compose logs api | grep -i glofas"
echo "  - Force real ingestion: curl -X POST http://localhost:8080/v1/forecasts/ingest"





