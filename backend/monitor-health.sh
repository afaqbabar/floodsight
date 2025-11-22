#!/bin/bash
# FloodSight - Health Check and Monitoring Script
# Continuous monitoring of backend health and metrics

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"
CHECK_INTERVAL="${CHECK_INTERVAL:-30}"  # seconds
LOG_FILE="${LOG_FILE:-/tmp/floodsight-health.log}"

# Initialize counters
TOTAL_CHECKS=0
SUCCESSFUL_CHECKS=0
FAILED_CHECKS=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FloodSight Health Monitor Started   ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Backend URL: ${BACKEND_URL}"
echo "Check Interval: ${CHECK_INTERVAL}s"
echo "Log File: ${LOG_FILE}"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""

# Function to check health
check_health() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Make health check request
    response=$(curl -s -w "\n%{http_code}" "${BACKEND_URL}/v1/health" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ "$http_code" -eq 200 ]; then
        SUCCESSFUL_CHECKS=$((SUCCESSFUL_CHECKS + 1))
        
        # Parse health response
        status=$(echo "$body" | grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
        db_status=$(echo "$body" | grep -o '"database"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
        
        echo -e "${GREEN}✅ [$timestamp] Health OK${NC} - Status: $status, DB: $db_status"
        echo "[$timestamp] HEALTH_OK status=$status db=$db_status" >> "$LOG_FILE"
        
        return 0
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        
        echo -e "${RED}❌ [$timestamp] Health FAILED${NC} - HTTP $http_code"
        echo "[$timestamp] HEALTH_FAILED http_code=$http_code" >> "$LOG_FILE"
        
        # Send alert (placeholder - implement actual alerting)
        if command -v notify-send &> /dev/null; then
            notify-send "FloodSight Alert" "Backend health check failed!"
        fi
        
        return 1
    fi
}

# Function to get metrics
get_metrics() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    metrics=$(curl -s "${BACKEND_URL}/metrics" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        # Extract key metrics
        request_count=$(echo "$metrics" | grep "floodsight_requests_total" | grep -v "#" | head -n1 | awk '{print $2}')
        
        if [ -n "$request_count" ]; then
            echo "  📊 Total Requests: $request_count"
            echo "[$timestamp] METRIC requests=$request_count" >> "$LOG_FILE"
        fi
    fi
}

# Function to check data freshness
check_data_freshness() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Get latest forecast
    latest_forecast=$(curl -s "${BACKEND_URL}/v1/forecasts?limit=1" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$latest_forecast" ]; then
        forecast_ts=$(echo "$latest_forecast" | grep -o '"ts"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4 | head -n1)
        
        if [ -n "$forecast_ts" ]; then
            echo "  📅 Latest Forecast: $forecast_ts"
            
            # Calculate age (simplified - assumes ISO format)
            # In production, use proper date parsing
            echo "[$timestamp] DATA_FRESHNESS latest=$forecast_ts" >> "$LOG_FILE"
        fi
    fi
}

# Function to check database connectivity
check_database() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Try to query stations (lightweight check)
    stations=$(curl -s "${BACKEND_URL}/v1/stations?limit=1" 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$stations" | grep -q '"id"'; then
        echo "  💾 Database: Connected"
        echo "[$timestamp] DB_CHECK status=connected" >> "$LOG_FILE"
        return 0
    else
        echo -e "  ${RED}💾 Database: Connection issues${NC}"
        echo "[$timestamp] DB_CHECK status=failed" >> "$LOG_FILE"
        return 1
    fi
}

# Function to display stats
display_stats() {
    local uptime_percent=0
    if [ $TOTAL_CHECKS -gt 0 ]; then
        uptime_percent=$((SUCCESSFUL_CHECKS * 100 / TOTAL_CHECKS))
    fi
    
    echo ""
    echo -e "${BLUE}--- Statistics ---${NC}"
    echo "  Total Checks: $TOTAL_CHECKS"
    echo "  Successful: ${GREEN}$SUCCESSFUL_CHECKS${NC}"
    echo "  Failed: ${RED}$FAILED_CHECKS${NC}"
    echo "  Uptime: ${BLUE}${uptime_percent}%${NC}"
    echo ""
}

# Trap Ctrl+C to display final stats
trap 'echo ""; echo "Monitoring stopped"; display_stats; exit 0' INT TERM

# Main monitoring loop
while true; do
    check_health
    
    # Every 5th check, get additional metrics
    if [ $((TOTAL_CHECKS % 5)) -eq 0 ]; then
        get_metrics
        check_data_freshness
        check_database
        display_stats
    fi
    
    sleep "$CHECK_INTERVAL"
done

