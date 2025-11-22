#!/bin/bash
# FloodSight System Monitoring Dashboard

clear
echo "════════════════════════════════════════════════════════════════════════════════"
echo "🌊 FLOODSIGHT SYSTEM MONITOR"
echo "════════════════════════════════════════════════════════════════════════════════"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cd /home/lenovo/scrimba/floodsight/backend

# Function to check service status
check_service() {
    service=$1
    if docker compose ps | grep -q "$service.*running"; then
        echo -e "${GREEN}●${NC} $service"
    else
        echo -e "${RED}○${NC} $service"
    fi
}

echo "📦 DOCKER SERVICES"
echo "────────────────────────────────────────────────────────────────────────────────"
check_service "floodsight-db"
check_service "floodsight-api"
check_service "floodsight-scheduler"
echo ""

echo "💾 DATABASE STATISTICS"
echo "────────────────────────────────────────────────────────────────────────────────"
docker compose exec -T db psql -U postgres -d floodsight -q -c \
  "SELECT 'Stations: ' || COUNT(*) FROM stations
   UNION ALL
   SELECT 'Forecasts: ' || COUNT(*) FROM forecasts WHERE source = 'GloFAS'
   UNION ALL
   SELECT 'Alerts: ' || COUNT(*) FROM alerts WHERE is_active = true;" 2>/dev/null
echo ""

echo "📊 FORECAST DATA STATUS"
echo "────────────────────────────────────────────────────────────────────────────────"
docker compose exec -T db psql -U postgres -d floodsight -q -c \
  "SELECT 
     'Latest Model Run: ' || MAX(model_run)::text as info
   FROM forecasts
   WHERE source = 'GloFAS'
   UNION ALL
   SELECT 
     'Data Age: ' || EXTRACT(HOUR FROM (NOW() - MAX(model_run))) || ' hours' as info
   FROM forecasts
   WHERE source = 'GloFAS';" 2>/dev/null
echo ""

echo "🚨 ACTIVE ALERTS BY LEVEL"
echo "────────────────────────────────────────────────────────────────────────────────"
docker compose exec -T db psql -U postgres -d floodsight -q -c \
  "SELECT 
     UPPER(level) as \"Alert Level\",
     COUNT(*) as \"Count\"
   FROM alerts
   WHERE is_active = true
   GROUP BY level
   ORDER BY 
     CASE level
       WHEN 'extreme' THEN 1
       WHEN 'severe' THEN 2
       WHEN 'warning' THEN 3
       WHEN 'info' THEN 4
     END;" 2>/dev/null || echo "  No active alerts"
echo ""

echo "🔄 SCHEDULER STATUS"
echo "────────────────────────────────────────────────────────────────────────────────"
if docker compose ps | grep -q "scheduler.*running"; then
    echo -e "${GREEN}✓${NC} Scheduler is running"
    echo "  Last run logs:"
    docker compose logs scheduler 2>/dev/null | grep "Ingested\|Created.*alerts\|Flow completed" | tail -n 3 | sed 's/^/  /'
else
    echo -e "${RED}✗${NC} Scheduler is not running"
    echo "  Start with: docker compose --profile scheduler up -d scheduler"
fi
echo ""

echo "💻 SYSTEM RESOURCES"
echo "────────────────────────────────────────────────────────────────────────────────"
# Container resource usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep floodsight | head -n 3
echo ""

# Disk usage
echo "Database size:"
docker compose exec -T db psql -U postgres -d floodsight -q -c \
  "SELECT 
     pg_size_pretty(pg_database_size('floodsight')) as \"Size\";" 2>/dev/null
echo ""

echo "⚡ API HEALTH CHECK"
echo "────────────────────────────────────────────────────────────────────────────────"
response=$(curl -s -w "\n%{http_code}" http://localhost:8080/v1/health 2>/dev/null)
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓${NC} API is healthy (200 OK)"
    echo "$body" | jq -r '"  Status: " + .status + ", Database: " + .database' 2>/dev/null
else
    echo -e "${RED}✗${NC} API is not responding (HTTP $http_code)"
fi
echo ""

echo "📈 FORECAST INGESTION METRICS (Last 24h)"
echo "────────────────────────────────────────────────────────────────────────────────"
docker compose exec -T db psql -U postgres -d floodsight -q -c \
  "SELECT 
     DATE_TRUNC('hour', created_at) as \"Hour\",
     COUNT(*) as \"Forecasts Ingested\"
   FROM forecasts
   WHERE created_at > NOW() - INTERVAL '24 hours'
   AND source = 'GloFAS'
   GROUP BY DATE_TRUNC('hour', created_at)
   ORDER BY \"Hour\" DESC
   LIMIT 5;" 2>/dev/null
echo ""

echo "🔍 QUICK COMMANDS"
echo "────────────────────────────────────────────────────────────────────────────────"
echo "  View logs:        docker compose logs -f api"
echo "  Restart API:      docker compose restart api"
echo "  Trigger ingest:   curl -X POST http://localhost:8080/v1/forecasts/ingest"
echo "  Compute alerts:   curl -X POST http://localhost:8080/v1/alerts/compute"
echo "  Run monitor:      ./monitor.sh"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"



