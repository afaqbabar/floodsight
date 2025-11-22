#!/bin/bash
# FloodSight - Test GloFAS Real Data Integration
# This script verifies that real ECMWF GloFAS data ingestion is working

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GloFAS Real Data Integration Test   ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to test API endpoint
test_api() {
    local url=$1
    if curl -s -f "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if backend is accessible
echo -e "${BLUE}Step 1: Checking backend connectivity...${NC}"
if ! test_api "${BACKEND_URL}/v1/health"; then
    echo -e "${RED}❌ Backend is not accessible at ${BACKEND_URL}${NC}"
    echo "Please ensure backend is running:"
    echo "  • Local: docker compose up -d"
    echo "  • K8s: kubectl port-forward svc/floodsight-backend 8080:8080"
    exit 1
fi
echo -e "${GREEN}✅ Backend is accessible${NC}"
echo ""

# Check configuration
echo -e "${BLUE}Step 2: Checking GloFAS configuration...${NC}"

# This would require an endpoint to check config, so we'll just check health
HEALTH=$(curl -s "${BACKEND_URL}/v1/health")
echo "Health status: $HEALTH"
echo ""

# Get current forecast count
echo -e "${BLUE}Step 3: Getting current forecast count...${NC}"
BEFORE_COUNT=$(curl -s "${BACKEND_URL}/v1/forecasts?limit=1000" | grep -o '"id"' | wc -l)
echo -e "Current forecasts: ${YELLOW}${BEFORE_COUNT}${NC}"
echo ""

# Trigger real data ingestion
echo -e "${BLUE}Step 4: Triggering GloFAS real data ingestion...${NC}"
echo -e "${YELLOW}⏳ This may take 5-15 minutes (CDS API processing)...${NC}"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BACKEND_URL}/v1/forecasts/ingest")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" -eq 201 ]; then
    echo -e "${GREEN}✅ Ingestion triggered successfully${NC}"
    echo ""
    echo "Response:"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    echo ""
    
    # Check if it was real data
    MODE=$(echo "$BODY" | grep -o '"mode"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
    
    if [ "$MODE" = "real" ]; then
        echo -e "${GREEN}🌍 Successfully ingested REAL GloFAS data!${NC}"
    elif [ "$MODE" = "fake" ]; then
        echo -e "${YELLOW}⚠️  Fell back to FAKE data${NC}"
        echo ""
        echo "Possible reasons:"
        echo "  • CDS API credentials not configured"
        echo "  • GloFAS license not accepted"
        echo "  • CDS API request failed"
        echo "  • Network connectivity issues"
        echo ""
        echo "Check logs for details:"
        echo "  docker compose logs api"
        echo "  kubectl logs -l component=backend"
    else
        echo -e "${YELLOW}⚠️  Unknown mode: ${MODE}${NC}"
    fi
else
    echo -e "${RED}❌ Ingestion failed (HTTP ${HTTP_CODE})${NC}"
    echo "Response: $BODY"
    exit 1
fi

echo ""

# Wait a moment for data to be processed
sleep 2

# Get new forecast count
echo -e "${BLUE}Step 5: Verifying new forecasts...${NC}"
AFTER_COUNT=$(curl -s "${BACKEND_URL}/v1/forecasts?limit=1000" | grep -o '"id"' | wc -l)
echo -e "Forecasts after ingestion: ${YELLOW}${AFTER_COUNT}${NC}"

NEW_FORECASTS=$((AFTER_COUNT - BEFORE_COUNT))
echo -e "New forecasts added: ${GREEN}${NEW_FORECASTS}${NC}"
echo ""

if [ "$NEW_FORECASTS" -gt 0 ]; then
    echo -e "${GREEN}✅ New forecasts were created${NC}"
else
    echo -e "${YELLOW}⚠️  No new forecasts (may already exist)${NC}"
fi

echo ""

# Get sample forecast to check data source
echo -e "${BLUE}Step 6: Checking forecast data source...${NC}"
SAMPLE=$(curl -s "${BACKEND_URL}/v1/forecasts?limit=1")
SOURCE=$(echo "$SAMPLE" | grep -o '"source"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4 | head -n1)
MODEL_RUN=$(echo "$SAMPLE" | grep -o '"model_run"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4 | head -n1)

echo "Data source: ${YELLOW}${SOURCE:-Unknown}${NC}"
echo "Model run: ${YELLOW}${MODEL_RUN:-Unknown}${NC}"
echo ""

if [ "$SOURCE" = "GloFAS" ]; then
    echo -e "${GREEN}✅ Data source is GloFAS (real data)${NC}"
else
    echo -e "${YELLOW}⚠️  Data source is not GloFAS${NC}"
fi

echo ""

# Show recent forecasts
echo -e "${BLUE}Step 7: Showing recent forecasts...${NC}"
echo ""
curl -s "${BACKEND_URL}/v1/forecasts?limit=5" | \
    python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        for f in data[:5]:
            print(f\"  • Station {f.get('station_id')}: {f.get('discharge_m3s')} m³/s at lead {f.get('lead_hours')}h (source: {f.get('source')})\")
    else:
        print('  No forecast data available')
except:
    print('  Could not parse forecast data')
" 2>/dev/null || echo "  Could not display forecasts"

echo ""

# Test alert computation
echo -e "${BLUE}Step 8: Computing alerts from forecasts...${NC}"
ALERT_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/v1/alerts/compute")
echo "$ALERT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ALERT_RESPONSE"
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}         Integration Summary            ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ "$MODE" = "real" ] && [ "$NEW_FORECASTS" -gt 0 ] && [ "$SOURCE" = "GloFAS" ]; then
    echo -e "${GREEN}✅ SUCCESS: Real GloFAS data integration is working!${NC}"
    echo ""
    echo "Your FloodSight backend is now ingesting real flood forecast data from ECMWF."
    echo ""
else
    echo -e "${YELLOW}⚠️  PARTIAL SUCCESS or USING FAKE DATA${NC}"
    echo ""
    
    if [ "$MODE" = "fake" ]; then
        echo "The system fell back to fake data. To use real GloFAS data:"
        echo ""
        echo "1. Register at: https://cds.climate.copernicus.eu/"
        echo "2. Accept GloFAS license"
        echo "3. Get your API credentials"
        echo "4. Configure CDS_API_KEY environment variable"
        echo "5. Restart backend and try again"
        echo ""
        echo "See: backend/GLOFAS_INTEGRATION_GUIDE.md"
    fi
fi

echo -e "${BLUE}========================================${NC}"
echo ""

# Provide next steps
echo -e "${YELLOW}📚 Documentation:${NC}"
echo "  • GloFAS Integration Guide: backend/GLOFAS_INTEGRATION_GUIDE.md"
echo "  • API Docs: ${BACKEND_URL}/docs"
echo ""

echo -e "${YELLOW}🔍 Verify Data:${NC}"
echo "  • Check forecasts: curl ${BACKEND_URL}/v1/forecasts"
echo "  • Check alerts: curl ${BACKEND_URL}/v1/alerts"
echo "  • View API docs: open ${BACKEND_URL}/docs"
echo ""

echo -e "${YELLOW}📊 Monitor Ingestion:${NC}"
echo "  • Docker: docker compose logs -f api scheduler"
echo "  • K8s: kubectl logs -f -l component=scheduler"
echo ""

