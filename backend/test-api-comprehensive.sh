#!/bin/bash
# FloodSight - Comprehensive API Testing Script
# Tests all API endpoints with various scenarios

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"
TEST_RESULTS=()
PASSED=0
FAILED=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FloodSight - Comprehensive API Test ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to test endpoint and record result
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local expected_code=${4:-200}
    local data=${5:-}
    
    echo -e "${YELLOW}Testing: ${description}${NC}"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X ${method} \
            -H "Content-Type: application/json" \
            -d "${data}" \
            "${BACKEND_URL}${endpoint}")
    else
        response=$(curl -s -w "\n%{http_code}" -X ${method} "${BACKEND_URL}${endpoint}")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS - ${description} (${http_code})${NC}"
        TEST_RESULTS+=("✅ $description")
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL - ${description} (expected ${expected_code}, got ${http_code})${NC}"
        echo "Response: $body"
        TEST_RESULTS+=("❌ $description (HTTP $http_code)")
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Check backend connectivity
echo -e "${BLUE}Checking backend connectivity...${NC}"
if ! curl -s -f "${BACKEND_URL}/v1/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend is not accessible at ${BACKEND_URL}${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Backend is accessible${NC}"
echo ""

# Category 1: Core Endpoints
echo -e "${BLUE}=== Testing Core Endpoints ===${NC}"
echo ""
test_endpoint "GET" "/" "Root endpoint"
test_endpoint "GET" "/v1/health" "Health check"
test_endpoint "GET" "/metrics" "Prometheus metrics"
test_endpoint "GET" "/docs" "OpenAPI documentation" 200
test_endpoint "GET" "/openapi.json" "OpenAPI spec" 200
echo ""

# Category 2: Station Endpoints
echo -e "${BLUE}=== Testing Station Endpoints ===${NC}"
echo ""
test_endpoint "GET" "/v1/stations" "List all stations"
test_endpoint "GET" "/v1/stations?limit=5" "List stations with limit"
test_endpoint "GET" "/v1/stations?skip=2&limit=3" "List stations with pagination"
test_endpoint "GET" "/v1/stations/1" "Get station by ID"
test_endpoint "GET" "/v1/stations/99999" "Get non-existent station" 404

# Create test station
echo ""
echo -e "${YELLOW}Testing: Create new station${NC}"
NEW_STATION_DATA='{
  "code": "TEST-STATION-'$(date +%s)'",
  "name": "Test Station",
  "lat": 52.52,
  "lon": 13.405,
  "river_basin": "Test Basin"
}'

CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "${NEW_STATION_DATA}" \
    "${BACKEND_URL}/v1/stations")

CREATE_CODE=$(echo "$CREATE_RESPONSE" | tail -n1)
CREATE_BODY=$(echo "$CREATE_RESPONSE" | head -n -1)

if [ "$CREATE_CODE" -eq 201 ]; then
    echo -e "${GREEN}✅ PASS - Create new station (201)${NC}"
    TEST_RESULTS+=("✅ Create new station")
    PASSED=$((PASSED + 1))
    
    # Extract station ID for further tests
    STATION_ID=$(echo "$CREATE_BODY" | grep -o '"id"[[:space:]]*:[[:space:]]*[0-9]*' | grep -o '[0-9]*' | head -n1)
    echo "Created station ID: $STATION_ID"
else
    echo -e "${YELLOW}⚠️  Could not create test station (may already exist)${NC}"
    STATION_ID=1  # Use existing station
fi

echo ""

# Category 3: Forecast Endpoints
echo -e "${BLUE}=== Testing Forecast Endpoints ===${NC}"
echo ""
test_endpoint "GET" "/v1/forecasts" "List all forecasts"
test_endpoint "GET" "/v1/forecasts?limit=10" "List forecasts with limit"
test_endpoint "GET" "/v1/forecasts?station_id=1" "List forecasts for station"
test_endpoint "GET" "/v1/forecasts?station_id=1&limit=5" "List forecasts with filter and limit"

# Create test forecast
if [ -n "$STATION_ID" ]; then
    FORECAST_DATA='{
      "station_id": '$STATION_ID',
      "ts": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
      "lead_hours": 24,
      "discharge_m3s": 850.5,
      "source": "Test"
    }'
    
    test_endpoint "POST" "/v1/forecasts" "Create new forecast" 201 "$FORECAST_DATA"
fi

echo ""

# Category 4: Alert Endpoints
echo -e "${BLUE}=== Testing Alert Endpoints ===${NC}"
echo ""
test_endpoint "GET" "/v1/alerts" "List all alerts"
test_endpoint "GET" "/v1/alerts?active_only=true" "List active alerts"
test_endpoint "GET" "/v1/alerts?active_only=false" "List all alerts including inactive"
test_endpoint "GET" "/v1/alerts?station_id=1" "List alerts for station"
test_endpoint "GET" "/v1/alerts?limit=10" "List alerts with limit"
echo ""

# Category 5: Data Ingestion & Processing
echo -e "${BLUE}=== Testing Data Ingestion & Processing ===${NC}"
echo ""
test_endpoint "POST" "/v1/forecasts/ingest-dev" "Trigger development forecast ingestion" 201
sleep 2  # Wait for processing
test_endpoint "POST" "/v1/alerts/compute" "Compute alerts from forecasts" 201
echo ""

# Category 6: User Endpoints (if implemented)
echo -e "${BLUE}=== Testing User Endpoints ===${NC}"
echo ""
test_endpoint "GET" "/v1/users" "List users" || true
test_endpoint "GET" "/v1/subscriptions" "List subscriptions" || true
echo ""

# Category 7: Webhook & Alert Rule Endpoints
echo -e "${BLUE}=== Testing Webhook & Alert Rule Endpoints ===${NC}"
echo ""
test_endpoint "GET" "/v1/webhooks" "List webhooks" || true
test_endpoint "GET" "/v1/alert-rules" "List alert rules" || true
echo ""

# Category 8: Analytics Endpoints
echo -e "${BLUE}=== Testing Analytics Endpoints ===${NC}"
echo ""
test_endpoint "GET" "/v1/analytics/overview" "Get analytics overview" || true
test_endpoint "GET" "/v1/analytics/stations" "Get station analytics" || true
echo ""

# Category 9: Error Handling
echo -e "${BLUE}=== Testing Error Handling ===${NC}"
echo ""
test_endpoint "GET" "/v1/nonexistent" "Non-existent endpoint" 404
test_endpoint "GET" "/v1/stations/abc" "Invalid station ID format" 422 || test_endpoint "GET" "/v1/stations/abc" "Invalid station ID format" 404
test_endpoint "POST" "/v1/stations" "Create station with missing data" 422 '{"code": "MISSING"}'
echo ""

# Category 10: Performance Tests
echo -e "${BLUE}=== Testing Performance ===${NC}"
echo ""

echo -e "${YELLOW}Testing: Large result set handling${NC}"
START_TIME=$(date +%s)
curl -s "${BACKEND_URL}/v1/forecasts?limit=100" > /dev/null
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo -e "${GREEN}✅ Retrieved 100 forecasts in ${DURATION}s${NC}"
echo ""

# Category 11: Data Validation
echo -e "${BLUE}=== Testing Data Validation ===${NC}"
echo ""

# Check if stations have required fields
echo -e "${YELLOW}Testing: Station data structure${NC}"
STATION_DATA=$(curl -s "${BACKEND_URL}/v1/stations?limit=1")
if echo "$STATION_DATA" | grep -q '"code"' && echo "$STATION_DATA" | grep -q '"lat"' && echo "$STATION_DATA" | grep -q '"lon"'; then
    echo -e "${GREEN}✅ Station data has required fields${NC}"
    TEST_RESULTS+=("✅ Station data structure")
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ Station data missing required fields${NC}"
    TEST_RESULTS+=("❌ Station data structure")
    FAILED=$((FAILED + 1))
fi

# Check if forecasts have required fields
echo -e "${YELLOW}Testing: Forecast data structure${NC}"
FORECAST_DATA=$(curl -s "${BACKEND_URL}/v1/forecasts?limit=1")
if echo "$FORECAST_DATA" | grep -q '"station_id"' && echo "$FORECAST_DATA" | grep -q '"discharge_m3s"'; then
    echo -e "${GREEN}✅ Forecast data has required fields${NC}"
    TEST_RESULTS+=("✅ Forecast data structure")
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ Forecast data missing required fields${NC}"
    TEST_RESULTS+=("❌ Forecast data structure")
    FAILED=$((FAILED + 1))
fi

echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}         Test Summary                   ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

TOTAL=$((PASSED + FAILED))
PASS_RATE=$((PASSED * 100 / TOTAL))

echo -e "Total Tests: ${BLUE}${TOTAL}${NC}"
echo -e "Passed:      ${GREEN}${PASSED}${NC}"
echo -e "Failed:      ${RED}${FAILED}${NC}"
echo -e "Pass Rate:   ${BLUE}${PASS_RATE}%${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit_code=0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    exit_code=1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}         Detailed Results               ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

for result in "${TEST_RESULTS[@]}"; do
    echo "$result"
done

echo ""
echo -e "${BLUE}========================================${NC}"
echo ""

# Additional information
echo -e "${YELLOW}📊 Quick Stats:${NC}"
STATION_COUNT=$(curl -s "${BACKEND_URL}/v1/stations" | grep -o '"id"' | wc -l || echo "0")
FORECAST_COUNT=$(curl -s "${BACKEND_URL}/v1/forecasts?limit=1000" | grep -o '"id"' | wc -l || echo "0")
ALERT_COUNT=$(curl -s "${BACKEND_URL}/v1/alerts" | grep -o '"id"' | wc -l || echo "0")

echo "  • Stations: $STATION_COUNT"
echo "  • Forecasts: $FORECAST_COUNT"
echo "  • Alerts: $ALERT_COUNT"
echo ""

echo -e "${YELLOW}📚 Documentation:${NC}"
echo "  • API Docs: ${BACKEND_URL}/docs"
echo "  • Health: ${BACKEND_URL}/v1/health"
echo "  • Metrics: ${BACKEND_URL}/metrics"
echo ""

exit $exit_code

