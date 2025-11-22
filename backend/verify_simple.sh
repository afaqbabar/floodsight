#!/bin/bash
# Simple Forecast Verification Script
# Uses SQL queries to analyze forecast accuracy

echo "================================================================================"
echo "📊 FLOODSIGHT FORECAST VERIFICATION (Manual)"
echo "================================================================================"
echo ""

cd /home/lenovo/scrimba/floodsight/backend

echo "1️⃣  FORECAST INVENTORY"
echo "--------------------------------------------------------------------------------"
echo "Total forecasts by source:"
docker compose exec -T db psql -U postgres -d floodsight -q -c \
  "SELECT source, COUNT(*) as count FROM forecasts GROUP BY source;"
echo ""

echo "Forecasts by station:"
docker compose exec -T db psql -U postgres -d floodsight -q -c \
  "SELECT s.code, s.name, COUNT(f.id) as forecasts 
   FROM stations s 
   LEFT JOIN forecasts f ON s.id = f.station_id AND f.source = 'GloFAS'
   GROUP BY s.id, s.code, s.name 
   ORDER BY s.code;"
echo ""

echo "2️⃣  FORECAST LEAD TIMES"
echo "--------------------------------------------------------------------------------"
echo "Distribution of forecast lead times:"
docker compose exec -T db psql -U postgres -d floodsight -q -c \
  "SELECT lead_hours, COUNT(*) as count 
   FROM forecasts 
   WHERE source = 'GloFAS' 
   GROUP BY lead_hours 
   ORDER BY lead_hours;"
echo ""

echo "3️⃣  DISCHARGE STATISTICS"
echo "--------------------------------------------------------------------------------"
echo "Discharge range by station:"
docker compose exec -T db psql -U postgres -d floodsight -q -c \
  "SELECT 
     s.code,
     MIN(f.discharge_m3s) as min_discharge,
     MAX(f.discharge_m3s) as max_discharge,
     ROUND(AVG(f.discharge_m3s)::numeric, 2) as avg_discharge,
     ROUND(STDDEV(f.discharge_m3s)::numeric, 2) as std_dev
   FROM forecasts f
   JOIN stations s ON f.station_id = s.id
   WHERE f.source = 'GloFAS'
   GROUP BY s.id, s.code
   ORDER BY s.code;"
echo ""

echo "4️⃣  FORECAST CONVERGENCE CHECK"
echo "--------------------------------------------------------------------------------"
echo "Times with multiple forecasts (for convergence analysis):"
docker compose exec -T db psql -U postgres -d floodsight -q -c \
  "SELECT 
     ts as target_time,
     COUNT(*) as num_forecasts,
     MIN(lead_hours) as shortest_lead,
     MAX(lead_hours) as longest_lead
   FROM forecasts 
   WHERE source = 'GloFAS'
   GROUP BY ts
   HAVING COUNT(*) > 1
   ORDER BY ts DESC
   LIMIT 10;"
echo ""

echo "5️⃣  SAMPLE COMPARISON (if available)"
echo "--------------------------------------------------------------------------------"
# Find a target time with multiple forecasts
TARGET_TIME=$(docker compose exec -T db psql -U postgres -d floodsight -t -c \
  "SELECT ts FROM forecasts WHERE source = 'GloFAS' GROUP BY ts HAVING COUNT(*) > 1 ORDER BY ts DESC LIMIT 1;" | xargs)

if [ ! -z "$TARGET_TIME" ]; then
  echo "Comparing forecasts for: $TARGET_TIME"
  echo ""
  docker compose exec -T db psql -U postgres -d floodsight -q -c \
    "SELECT 
       s.code as station,
       f.lead_hours,
       ROUND(f.discharge_m3s::numeric, 2) as discharge,
       f.model_run,
       f.created_at
     FROM forecasts f
     JOIN stations s ON f.station_id = s.id
     WHERE f.ts = '$TARGET_TIME' AND f.source = 'GloFAS'
     ORDER BY s.code, f.lead_hours;"
  
  echo ""
  echo "Analysis:"
  echo "- Compare forecasts with different lead times for same target"
  echo "- Shorter lead times should be more accurate"
  echo "- Large differences indicate forecast uncertainty"
else
  echo "⚠️  No overlapping forecasts found yet."
  echo "   Run ingestion multiple times to get convergence data."
fi
echo ""

echo "================================================================================"
echo "📋 HOW TO MANUALLY VERIFY ACCURACY"
echo "================================================================================"
echo ""
echo "Method 1: Compare with newer forecasts (Convergence)"
echo "----------------------------------------------------------------------"
echo "  Pick an old forecast for time T:"
echo "    • Forecast A: 72h lead, predicted 1200 m³/s"
echo "    • Forecast B: 24h lead, predicted 1180 m³/s (more recent)"
echo "    • Forecast C: 6h lead, predicted 1150 m³/s (most recent)"
echo ""
echo "  Error estimate: |1200 - 1150| = 50 m³/s (4.3% error)"
echo "  → Forecasts converged, good stability"
echo ""

echo "Method 2: Compare with GloFAS Reanalysis (Ground Truth)"
echo "----------------------------------------------------------------------"
echo "  Step 1: Export your forecasts"
echo "    $ docker compose exec db psql -U postgres -d floodsight -c"
echo "      \"SELECT * FROM forecasts WHERE model_run = '2025-11-11' AND lead_hours = 24;\""
echo ""
echo "  Step 2: Download GloFAS Reanalysis from ECMWF"
echo "    • Go to: https://cds.climate.copernicus.eu"
echo "    • Dataset: CEMS GloFAS historical (reanalysis)"
echo "    • Date: Same as your forecast target date"
echo "    • Coordinates: Same as your stations"
echo ""
echo "  Step 3: Compare values manually"
echo "    Forecast: 1200 m³/s"
echo "    Reanalysis: 1150 m³/s"
echo "    Error: 50 m³/s"
echo "    Accuracy: 95.8%"
echo ""

echo "Method 3: Visual inspection"
echo "----------------------------------------------------------------------"
echo "  Export forecast time series:"
echo "    $ curl http://localhost:8080/v1/forecasts?station_id=1 | jq ."
echo ""
echo "  Look for:"
echo "    • Unrealistic jumps (sudden changes)"
echo "    • Negative values (impossible)"
echo "    • Values outside normal range for river"
echo "    • Consistent over/under prediction (bias)"
echo ""

echo "================================================================================"
echo "⏭️  NEXT STEPS"
echo "================================================================================"
echo ""
echo "For automated verification:"
echo "  1. Start scheduler for regular ingestion:"
echo "     $ cd backend && docker compose --profile scheduler up -d scheduler"
echo ""
echo "  2. Wait 24-48 hours to accumulate overlapping forecasts"
echo ""
echo "  3. Run this script again to see convergence analysis"
echo ""
echo "  4. (Optional) Implement automated reanalysis comparison"
echo ""
echo "================================================================================"




