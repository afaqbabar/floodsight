#!/bin/bash
# Performance Optimization Script for FloodSight

echo "════════════════════════════════════════════════════════════════════════════════"
echo "⚡ FLOODSIGHT PERFORMANCE OPTIMIZATION"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

cd /home/lenovo/scrimba/floodsight/backend

echo "1️⃣  DATABASE OPTIMIZATION"
echo "────────────────────────────────────────────────────────────────────────────────"

# Vacuum and analyze
echo "Running VACUUM ANALYZE (cleanup & optimize)..."
docker compose exec -T db psql -U postgres -d floodsight -c "VACUUM ANALYZE;" 2>&1 | grep -v "warning"
echo "✓ Done"
echo ""

# Create indexes if missing
echo "Checking/creating database indexes..."
docker compose exec -T db psql -U postgres -d floodsight -c "
-- Forecast indexes (for fast queries)
CREATE INDEX IF NOT EXISTS idx_forecasts_station_ts ON forecasts(station_id, ts);
CREATE INDEX IF NOT EXISTS idx_forecasts_model_run_station ON forecasts(model_run, station_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_source_created ON forecasts(source, created_at);

-- Alert indexes
CREATE INDEX IF NOT EXISTS idx_alerts_station_active ON alerts(station_id, is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_issued_at ON alerts(issued_at DESC);

-- Show all indexes
SELECT 
  schemaname,
  tablename,
  indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
" 2>&1 | grep -E "idx_|tablename" | tail -n 20
echo "✓ Indexes created/verified"
echo ""

echo "2️⃣  DATABASE STATISTICS"
echo "────────────────────────────────────────────────────────────────────────────────"
docker compose exec -T db psql -U postgres -d floodsight -c "
SELECT 
  relname as \"Table\",
  n_live_tup as \"Rows\",
  pg_size_pretty(pg_total_relation_size(relid)) as \"Total Size\"
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
" 2>&1 | grep -v "warning"
echo ""

echo "3️⃣  CLEANUP OLD DATA"
echo "────────────────────────────────────────────────────────────────────────────────"

# Count old forecasts (> 30 days)
old_count=$(docker compose exec -T db psql -U postgres -d floodsight -t -c \
  "SELECT COUNT(*) FROM forecasts WHERE created_at < NOW() - INTERVAL '30 days';" 2>/dev/null | xargs)

echo "Old forecasts (> 30 days): $old_count"

if [ "$old_count" -gt 0 ]; then
  echo "To clean up old data:"
  echo "  docker compose exec db psql -U postgres -d floodsight -c \"DELETE FROM forecasts WHERE created_at < NOW() - INTERVAL '30 days';\""
else
  echo "✓ No old data to clean up"
fi
echo ""

# Deactivate old alerts
old_alerts=$(docker compose exec -T db psql -U postgres -d floodsight -t -c \
  "SELECT COUNT(*) FROM alerts WHERE is_active = true AND valid_until < NOW();" 2>/dev/null | xargs)

echo "Expired active alerts: $old_alerts"
if [ "$old_alerts" -gt 0 ]; then
  echo "Deactivating expired alerts..."
  docker compose exec -T db psql -U postgres -d floodsight -c \
    "UPDATE alerts SET is_active = false WHERE is_active = true AND valid_until < NOW();" 2>&1 | grep -v "warning"
  echo "✓ Deactivated $old_alerts alerts"
else
  echo "✓ No expired alerts"
fi
echo ""

echo "4️⃣  DOCKER OPTIMIZATION"
echo "────────────────────────────────────────────────────────────────────────────────"

# Remove unused images
echo "Removing unused Docker images..."
docker image prune -f 2>&1 | tail -n 1

# Remove unused volumes
echo "Removing unused Docker volumes..."
docker volume prune -f 2>&1 | tail -n 1
echo ""

echo "5️⃣  MEMORY OPTIMIZATION"
echo "────────────────────────────────────────────────────────────────────────────────"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep floodsight

# Check if containers are using too much memory
high_mem=$(docker stats --no-stream --format "{{.Name}}\t{{.MemPerc}}" | grep floodsight | awk -F'%' '$2 > 70 {print $1}')
if [ -n "$high_mem" ]; then
  echo ""
  echo "⚠️  High memory usage detected in:"
  echo "$high_mem"
  echo "Consider restarting containers: docker compose restart"
else
  echo ""
  echo "✓ Memory usage is healthy"
fi
echo ""

echo "6️⃣  API RESPONSE TIME CHECK"
echo "────────────────────────────────────────────────────────────────────────────────"

# Test API response times
echo "Testing API endpoints..."
echo ""

for endpoint in "/v1/health" "/v1/stations" "/v1/forecasts?limit=10" "/v1/alerts"; do
  response_time=$(curl -o /dev/null -s -w '%{time_total}' "http://localhost:8080$endpoint" 2>/dev/null)
  if [ -n "$response_time" ]; then
    # Convert to milliseconds
    ms=$(echo "$response_time * 1000" | bc)
    printf "  %-30s %6.0f ms\n" "$endpoint" "$ms"
  fi
done
echo ""

echo "7️⃣  OPTIMIZATION RECOMMENDATIONS"
echo "────────────────────────────────────────────────────────────────────────────────"

# Check forecast count
forecast_count=$(docker compose exec -T db psql -U postgres -d floodsight -t -c \
  "SELECT COUNT(*) FROM forecasts;" 2>/dev/null | xargs)

if [ "$forecast_count" -gt 10000 ]; then
  echo "⚠️  Large forecast table ($forecast_count rows)"
  echo "    Consider implementing data retention policy"
fi

# Check if scheduler is running
if docker compose ps | grep -q "scheduler.*running"; then
  echo "✓ Scheduler is running (hourly updates)"
else
  echo "⚠️  Scheduler is not running"
  echo "    Start with: docker compose --profile scheduler up -d scheduler"
fi

# Check API health
api_health=$(curl -s http://localhost:8080/v1/health 2>/dev/null | jq -r '.status' 2>/dev/null)
if [ "$api_health" = "ok" ]; then
  echo "✓ API is healthy"
else
  echo "⚠️  API health check failed"
fi

# Database size check
db_size=$(docker compose exec -T db psql -U postgres -d floodsight -t -c \
  "SELECT pg_database_size('floodsight');" 2>/dev/null | xargs)

if [ "$db_size" -gt 104857600 ]; then  # > 100MB
  size_mb=$((db_size / 1048576))
  echo "ℹ️  Database size: ${size_mb}MB"
  echo "    Monitor growth and implement archiving if needed"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "✅ OPTIMIZATION COMPLETE"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Performance Tips:"
echo "  • Run this script weekly: ./optimize.sh"
echo "  • Monitor with: ./monitor.sh"
echo "  • Keep Docker images updated"
echo "  • Archive old forecasts periodically"
echo "  • Restart containers monthly: docker compose restart"
echo ""



