#!/bin/bash
# Historical Forecast Verification with PEGELONLINE
# Compares old forecasts with actual measurements at the forecast target time

echo "================================================================================"
echo "📅 HISTORICAL FORECAST VERIFICATION"
echo "================================================================================"
echo ""
echo "This script compares forecasts made in the past with actual gauge measurements"
echo "at the time the forecast predicted."
echo ""

# Get PEGELONLINE historical data (last 30 days)
get_historical_discharge() {
    local uuid=$1
    local start_date=$2  # Format: P30D (last 30 days)
    
    curl -s "https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/$uuid/Q/measurements.json?start=$start_date" | \
        jq -r '.[] | "\(.timestamp)|\(.value)"'
}

echo "🔍 CHECKING FORECAST VS ACTUAL (Example)"
echo "--------------------------------------------------------------------------------"
echo ""
echo "EXAMPLE: Dresden Elbe"
echo ""
echo "Step 1: Find an old forecast"
echo "  Forecast made: 2025-11-11 09:00"
echo "  Predicted for: 2025-11-12 09:00 (+24h)"
echo "  Predicted discharge: XXX m³/s"
echo ""
echo "Step 2: Get actual measurement at 2025-11-12 09:00"
echo "  Actual discharge: YYY m³/s"
echo ""
echo "Step 3: Calculate accuracy"
echo "  Error = |XXX - YYY|"
echo "  Accuracy = 100 - (error / actual × 100)"
echo ""

echo "================================================================================"
echo "📊 AVAILABLE PEGELONLINE DATA"
echo "================================================================================"
echo ""

# Station UUIDs
DRESDEN_UUID="70272185-b2b3-4178-96b8-43bea330dcae"
COLOGNE_UUID="a6ee8177-107b-47dd-bcfd-30960ccc6e9c"
FRANKFURT_UUID="66ff3eb4-513b-478b-abd2-2f5126ea66fd"

echo "Getting last 7 days of measurements from PEGELONLINE..."
echo ""

for station in "Dresden:$DRESDEN_UUID" "Cologne:$COLOGNE_UUID" "Frankfurt:$FRANKFURT_UUID"; do
    name=$(echo "$station" | cut -d: -f1)
    uuid=$(echo "$station" | cut -d: -f2)
    
    echo "Station: $name"
    echo "Latest measurements:"
    
    # Get last 10 measurements
    curl -s "https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/$uuid/Q/measurements.json?start=P7D" 2>/dev/null | \
        jq -r '.[-10:] | .[] | "\(.timestamp): \(.value) m³/s"' 2>/dev/null | head -n 5 || echo "  No historical data available"
    
    echo ""
done

echo "================================================================================"
echo "🎯 HOW TO PROPERLY VERIFY"
echo "================================================================================"
echo ""
echo "Manual Verification Process:"
echo ""
echo "1. Pick a forecast from your database (for a time in the past):"
echo "   $ docker compose exec db psql -U postgres -d floodsight -c"
echo "     \"SELECT s.code, f.ts, f.lead_hours, f.discharge_m3s, f.model_run"
echo "      FROM forecasts f JOIN stations s ON f.station_id = s.id"
echo "      WHERE f.ts < NOW() AND s.code = 'ELBE-DRESDEN'"
echo "      LIMIT 5;\""
echo ""
echo "2. Get PEGELONLINE data for that exact time:"
echo "   $ curl \"https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/"
echo "     $DRESDEN_UUID/Q/measurements.json?start=P30D\" | jq"
echo ""
echo "3. Find the measurement closest to your forecast time"
echo ""
echo "4. Calculate: Error = |Forecast - Actual|"
echo ""
echo "Example:"
echo "--------"
echo "  Your forecast (made Nov 11, 09:00):"
echo "    For: Nov 12, 09:00 (+24h lead)"
echo "    Predicted: 850 m³/s"
echo ""
echo "  PEGELONLINE actual (Nov 12, 09:00):"
echo "    Measured: 820 m³/s"
echo ""
echo "  Accuracy:"
echo "    Error: |850 - 820| = 30 m³/s"
echo "    Percentage: 100 - (30/820 × 100) = 96.3% ✅"
echo ""

echo "================================================================================"
echo "⏰ CURRENT LIMITATION"
echo "================================================================================"
echo ""
echo "Your forecasts are too new! They predict the FUTURE."
echo ""
echo "  Current time: $(date '+%Y-%m-%d %H:%M')"
echo "  Your oldest forecast from: 2025-11-11"
echo "  Forecast target times: 2025-11-13 and later"
echo ""
echo "To verify accuracy:"
echo "  1. Wait until forecast target times pass (e.g., Nov 13+)"
echo "  2. Then run this comparison"
echo "  3. OR compare with GloFAS Reanalysis (model vs model)"
echo ""
echo "For now, you can:"
echo "  • Use convergence analysis (compare multiple forecasts)"
echo "  • Use GloFAS Reanalysis (download from ECMWF)"
echo "  • Wait 24-48 hours for your forecasts to 'mature'"
echo ""

echo "================================================================================"
echo "💡 AUTOMATED VERIFICATION"
echo "================================================================================"
echo ""
echo "Want automated verification?"
echo "  I can implement a system that:"
echo "  • Stores forecasts in database ✅ (already doing)"
echo "  • Waits for forecast time to pass"
echo "  • Auto-fetches PEGELONLINE data"
echo "  • Calculates accuracy automatically"
echo "  • Shows results in dashboard"
echo ""
echo "Time to implement: ~2-3 hours"
echo "Would provide: Real accuracy metrics updated daily"
echo ""
echo "================================================================================"



