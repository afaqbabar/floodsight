#!/bin/bash
# Forecast Verification Using Real PEGELONLINE Gauge Data
# Compares GloFAS forecasts with actual measurements

echo "================================================================================"
echo "🎯 FORECAST VERIFICATION WITH REAL GAUGE DATA"
echo "================================================================================"
echo ""
echo "Comparing GloFAS forecasts vs actual PEGELONLINE measurements"
echo "Time: $(date '+%Y-%m-%d %H:%M')"
echo ""

# Function to get PEGELONLINE discharge
get_pegelonline_discharge() {
    local uuid=$1
    local name=$2
    
    response=$(curl -s "https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/$uuid/Q/currentmeasurement.json")
    
    if [ -z "$response" ] || [ "$response" == "null" ]; then
        echo "null|null"
        return
    fi
    
    timestamp=$(echo "$response" | jq -r '.timestamp // "null"')
    discharge=$(echo "$response" | jq -r '.value // "null"')
    
    echo "$timestamp|$discharge"
}

# Station mappings (Your FloodSight stations → PEGELONLINE gauges)
declare -A STATIONS
STATIONS["ELBE-DRESDEN"]="70272185-b2b3-4178-96b8-43bea330dcae"
STATIONS["RHINE-COLOGNE"]="a6ee8177-107b-47dd-bcfd-30960ccc6e9c"
STATIONS["MAIN-FRANKFURT"]="66ff3eb4-513b-478b-abd2-2f5126ea66fd"

echo "📊 REAL-TIME COMPARISON"
echo "--------------------------------------------------------------------------------"
printf "%-18s | %-12s | %-12s | %-10s | %-10s\n" "Station" "Actual (m³/s)" "Forecast" "Error" "Accuracy"
echo "--------------------------------------------------------------------------------"

cd /home/lenovo/scrimba/floodsight/backend

total_error=0
count=0

for station_code in "${!STATIONS[@]}"; do
    uuid="${STATIONS[$station_code]}"
    
    # Get actual measurement from PEGELONLINE
    result=$(get_pegelonline_discharge "$uuid" "$station_code")
    timestamp=$(echo "$result" | cut -d'|' -f1)
    actual_discharge=$(echo "$result" | cut -d'|' -f2)
    
    if [ "$actual_discharge" == "null" ]; then
        printf "%-18s | %-12s | %-12s | %-10s | %-10s\n" \
            "$station_code" "No data" "---" "---" "---"
        continue
    fi
    
    # Get forecast from database (shortest lead time = most recent forecast)
    forecast_discharge=$(docker compose exec -T db psql -U postgres -d floodsight -t -c \
        "SELECT ROUND(f.discharge_m3s::numeric, 2)
         FROM forecasts f
         JOIN stations s ON f.station_id = s.id
         WHERE s.code = '$station_code' 
         AND f.source = 'GloFAS'
         ORDER BY f.lead_hours ASC
         LIMIT 1;" 2>/dev/null | xargs)
    
    if [ -z "$forecast_discharge" ] || [ "$forecast_discharge" == "null" ]; then
        printf "%-18s | %12.0f | %-12s | %-10s | %-10s\n" \
            "$station_code" "$actual_discharge" "No forecast" "---" "---"
        continue
    fi
    
    # Calculate error and accuracy
    error=$(echo "scale=2; $forecast_discharge - $actual_discharge" | bc)
    abs_error=$(echo "scale=2; if ($error < 0) -1 * $error else $error" | bc)
    accuracy=$(echo "scale=1; 100 - ($abs_error / $actual_discharge * 100)" | bc)
    
    # Accumulate for overall statistics
    total_error=$(echo "scale=2; $total_error + $abs_error" | bc)
    count=$((count + 1))
    
    # Format output
    printf "%-18s | %12.0f | %12.0f | %+10.0f | %9.1f%%\n" \
        "$station_code" \
        "$actual_discharge" \
        "$forecast_discharge" \
        "$error" \
        "$accuracy"
done

echo "--------------------------------------------------------------------------------"

if [ $count -gt 0 ]; then
    avg_error=$(echo "scale=2; $total_error / $count" | bc)
    echo ""
    echo "📈 OVERALL STATISTICS"
    echo "--------------------------------------------------------------------------------"
    echo "  Stations verified: $count"
    echo "  Mean Absolute Error (MAE): ${avg_error} m³/s"
    echo ""
fi

echo ""
echo "================================================================================"
echo "📋 DETAILED ANALYSIS"
echo "================================================================================"
echo ""

for station_code in "${!STATIONS[@]}"; do
    uuid="${STATIONS[$station_code]}"
    
    # Get actual measurement
    result=$(get_pegelonline_discharge "$uuid" "$station_code")
    actual_discharge=$(echo "$result" | cut -d'|' -f2)
    
    if [ "$actual_discharge" == "null" ]; then
        continue
    fi
    
    echo "Station: $station_code"
    echo "----------------------------------------"
    
    # Get all forecasts for this station
    docker compose exec -T db psql -U postgres -d floodsight -q -c \
        "SELECT 
           f.lead_hours,
           ROUND(f.discharge_m3s::numeric, 2) as forecast,
           ROUND((f.discharge_m3s - $actual_discharge)::numeric, 2) as error,
           ROUND((100 - (ABS(f.discharge_m3s - $actual_discharge) / $actual_discharge * 100))::numeric, 1) as accuracy
         FROM forecasts f
         JOIN stations s ON f.station_id = s.id
         WHERE s.code = '$station_code' 
         AND f.source = 'GloFAS'
         ORDER BY f.lead_hours
         LIMIT 10;" 2>/dev/null
    
    echo ""
done

echo "================================================================================"
echo "💡 INTERPRETATION"
echo "================================================================================"
echo ""
echo "Accuracy Levels:"
echo "  ✅ Excellent: >95%  (Error < 5%)"
echo "  ✅ Good:      90-95% (Error 5-10%)"
echo "  ⚠️  Fair:      80-90% (Error 10-20%)"
echo "  ❌ Poor:      <80%   (Error >20%)"
echo ""
echo "Notes:"
echo "  • PEGELONLINE data is from physical gauges (ground truth)"
echo "  • Forecast accuracy typically decreases with lead time"
echo "  • Shorter lead times should have lower errors"
echo "  • Positive error = over-prediction, Negative = under-prediction"
echo ""

echo "================================================================================"
echo "📚 MORE DETAILS"
echo "================================================================================"
echo ""
echo "Real-time PEGELONLINE data:"
echo "  • Dresden Elbe:     https://www.pegelonline.wsv.de/gast/stammdaten?pegelnr=501060"
echo "  • Cologne Rhine:    https://www.pegelonline.wsv.de/gast/stammdaten?pegelnr=276430"
echo "  • Frankfurt Main:   https://www.pegelonline.wsv.de/gast/stammdaten?pegelnr=247100"
echo ""
echo "To run again: ./verify_with_gauges.sh"
echo "================================================================================"



