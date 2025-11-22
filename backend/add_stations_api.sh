#!/bin/bash
# Add more European stations via API

echo "Adding new European stations via API..."
echo "======================================"
echo ""

API_URL="http://localhost:8080/v1"

# Array of stations to add
declare -a stations=(
  # Germany
  '{"code":"RHINE-KOBLENZ","name":"Koblenz Rhine","river_basin":"Rhine","lat":50.3569,"lon":7.5976}'
  '{"code":"RHINE-MAINZ","name":"Mainz Rhine","river_basin":"Rhine","lat":49.9929,"lon":8.2473}'
  '{"code":"ELBE-MAGDEBURG","name":"Magdeburg Elbe","river_basin":"Elbe","lat":52.1205,"lon":11.6276}'
  
  # Netherlands
  '{"code":"RHINE-LOBITH","name":"Lobith Rhine","river_basin":"Rhine","lat":51.8631,"lon":6.1129}'
  '{"code":"MEUSE-MAASTRICHT","name":"Maastricht Meuse","river_basin":"Meuse","lat":50.8514,"lon":5.6909}'
  
  # France
  '{"code":"SEINE-PARIS","name":"Paris Seine","river_basin":"Seine","lat":48.8566,"lon":2.3522}'
  '{"code":"RHONE-LYON","name":"Lyon Rhone","river_basin":"Rhone","lat":45.7640,"lon":4.8357}'
  '{"code":"LOIRE-ORLEANS","name":"Orleans Loire","river_basin":"Loire","lat":47.9029,"lon":1.9093}'
  
  # Austria/Czech
  '{"code":"DANUBE-LINZ","name":"Linz Danube","river_basin":"Danube","lat":48.3069,"lon":14.2858}'
  '{"code":"ELBE-PRAGUE","name":"Prague Vltava","river_basin":"Elbe","lat":50.0755,"lon":14.4378}'
  
  # Italy
  '{"code":"PO-TURIN","name":"Turin Po","river_basin":"Po","lat":45.0703,"lon":7.6869}'
  
  # Spain
  '{"code":"EBRO-ZARAGOZA","name":"Zaragoza Ebro","river_basin":"Ebro","lat":41.6488,"lon":-0.8891}'
)

added=0
skipped=0

for station in "${stations[@]}"; do
  code=$(echo "$station" | jq -r '.code')
  name=$(echo "$station" | jq -r '.name')
  
  response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/stations" \
    -H "Content-Type: application/json" \
    -d "$station")
  
  http_code=$(echo "$response" | tail -n 1)
  body=$(echo "$response" | head -n -1)
  
  if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
    echo "✅ $code - $name"
    added=$((added + 1))
  else
    echo "⏭️  $code - Already exists or error"
    skipped=$((skipped + 1))
  fi
done

echo ""
echo "======================================"
echo "Added: $added stations"
echo "Skipped: $skipped stations"
echo ""

# Show total count
total=$(curl -s "$API_URL/stations" | jq 'length')
echo "Total stations in database: $total"
echo "======================================"



