#!/bin/bash
# FloodSight Backend - Local Docker Testing Script
# This script starts the backend locally and runs comprehensive tests

set -e  # Exit on error

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the backend directory
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:8080"
MAX_WAIT_TIME=60  # seconds

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FloodSight Backend - Local Testing  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if service is up
wait_for_service() {
    local url=$1
    local max_wait=$2
    local elapsed=0
    
    echo -e "${YELLOW}⏳ Waiting for service at ${url}...${NC}"
    
    while [ $elapsed -lt $max_wait ]; do
        if curl -s -f "${url}/v1/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Service is ready!${NC}"
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        echo -n "."
    done
    
    echo -e "${RED}❌ Service failed to start within ${max_wait}s${NC}"
    return 1
}

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local expected_code=${4:-200}
    
    echo -e "${YELLOW}Testing: ${description}${NC}"
    
    response=$(curl -s -w "\n%{http_code}" -X ${method} "${BACKEND_URL}${endpoint}")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq "$expected_code" ]; then
        echo -e "${GREEN}✅ ${description} - Success (${http_code})${NC}"
        return 0
    else
        echo -e "${RED}❌ ${description} - Failed (expected ${expected_code}, got ${http_code})${NC}"
        echo "Response: $body"
        return 1
    fi
}

# Step 1: Check if Docker is running
echo -e "${BLUE}Step 1: Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Step 2: Stop any existing containers
echo -e "${BLUE}Step 2: Cleaning up existing containers...${NC}"
docker compose down -v 2>/dev/null || true
echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

# Step 3: Build and start services
echo -e "${BLUE}Step 3: Building and starting services...${NC}"
docker compose up -d --build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start services${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Step 4: Wait for services to be ready
echo -e "${BLUE}Step 4: Waiting for services to be ready...${NC}"
if ! wait_for_service "${BACKEND_URL}" ${MAX_WAIT_TIME}; then
    echo -e "${RED}Services failed to start. Checking logs...${NC}"
    docker compose logs api
    exit 1
fi
echo ""

# Step 5: Run database migrations
echo -e "${BLUE}Step 5: Running database migrations...${NC}"
docker compose exec -T api alembic upgrade head
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations complete${NC}"
else
    echo -e "${RED}❌ Migrations failed${NC}"
    exit 1
fi
echo ""

# Step 6: Seed sample data
echo -e "${BLUE}Step 6: Seeding sample data...${NC}"
docker compose exec -T api python -m app.services.seed
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Seeding complete${NC}"
else
    echo -e "${RED}❌ Seeding failed${NC}"
    exit 1
fi
echo ""

# Step 7: Run API tests
echo -e "${BLUE}Step 7: Testing API endpoints...${NC}"
echo ""

# Health check
test_endpoint "GET" "/v1/health" "Health check"

# Root endpoint
test_endpoint "GET" "/" "Root endpoint"

# Metrics endpoint
test_endpoint "GET" "/metrics" "Prometheus metrics"

# Stations endpoint
test_endpoint "GET" "/v1/stations" "List stations"

# Forecasts endpoint
test_endpoint "GET" "/v1/forecasts" "List forecasts"

# Alerts endpoint
test_endpoint "GET" "/v1/alerts" "List alerts"

echo ""

# Step 8: Test data ingestion flow
echo -e "${BLUE}Step 8: Testing data ingestion flow...${NC}"

# Trigger forecast ingestion
test_endpoint "POST" "/v1/forecasts/ingest-dev" "Trigger forecast ingestion (fake data)" 201

# Wait a moment for data to be processed
sleep 2

# Check if forecasts were created
forecast_count=$(curl -s "${BACKEND_URL}/v1/forecasts?limit=1" | grep -o '"id"' | wc -l)
if [ "$forecast_count" -gt 0 ]; then
    echo -e "${GREEN}✅ Forecasts created successfully${NC}"
else
    echo -e "${RED}❌ No forecasts found after ingestion${NC}"
fi

# Compute alerts
test_endpoint "POST" "/v1/alerts/compute" "Compute alerts from forecasts" 201

# Wait a moment for alerts to be processed
sleep 2

# Check if alerts were created
alert_count=$(curl -s "${BACKEND_URL}/v1/alerts?active_only=true" | grep -o '"id"' | wc -l)
if [ "$alert_count" -gt 0 ]; then
    echo -e "${GREEN}✅ Alerts created successfully${NC}"
else
    echo -e "${YELLOW}⚠️  No alerts created (may be normal if thresholds not exceeded)${NC}"
fi

echo ""

# Step 9: Display summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}         Test Summary                   ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get station count
station_count=$(curl -s "${BACKEND_URL}/v1/stations" | grep -o '"id"' | wc -l)
echo -e "📍 Stations: ${GREEN}${station_count}${NC}"

# Get forecast count
forecast_count=$(curl -s "${BACKEND_URL}/v1/forecasts?limit=1000" | grep -o '"id"' | wc -l)
echo -e "📊 Forecasts: ${GREEN}${forecast_count}${NC}"

# Get alert count
alert_count=$(curl -s "${BACKEND_URL}/v1/alerts" | grep -o '"id"' | wc -l)
echo -e "🚨 Alerts: ${GREEN}${alert_count}${NC}"

echo ""
echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}         Quick Links                    ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "📖 API Documentation: ${BLUE}http://localhost:8080/docs${NC}"
echo -e "📊 Metrics: ${BLUE}http://localhost:8080/metrics${NC}"
echo -e "💚 Health: ${BLUE}http://localhost:8080/v1/health${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}         Useful Commands                ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "View logs:"
echo "  docker compose logs -f api"
echo ""
echo "View scheduler logs:"
echo "  docker compose logs -f scheduler"
echo ""
echo "Stop services:"
echo "  docker compose down"
echo ""
echo "Stop and remove volumes:"
echo "  docker compose down -v"
echo ""
echo "Restart services:"
echo "  docker compose restart"
echo ""
echo -e "${GREEN}🎉 Backend is ready for local development!${NC}"

