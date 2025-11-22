#!/bin/bash
set -e

API_URL="http://192.168.178.50:30636/v1"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌍 Adding Global Flood Monitoring Stations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Array of stations to add
# Format: code|name|river_basin|lat|lon|country|region

stations=(
  # Asia
  "GANGES-PATNA|Patna Ganges|Ganges|25.59|85.13|India|Bihar"
  "MEKONG-PHNOMPENH|Phnom Penh Mekong|Mekong|11.56|104.93|Cambodia|Phnom Penh"
  "YANGTZE-WUHAN|Wuhan Yangtze|Yangtze|30.59|114.31|China|Hubei"
  "INDUS-HYDERABAD|Hyderabad Indus|Indus|25.39|68.37|Pakistan|Sindh"
  "BRAHMAPUTRA-GUWAHATI|Guwahati Brahmaputra|Brahmaputra|26.18|91.75|India|Assam"
  
  # Africa
  "NIGER-NIAMEY|Niamey Niger|Niger|13.51|2.11|Niger|Niamey"
  "NILE-KHARTOUM|Khartoum Nile|Nile|15.59|32.53|Sudan|Khartoum"
  "CONGO-KINSHASA|Kinshasa Congo|Congo|4.32|15.31|DR Congo|Kinshasa"
  "ZAMBEZI-TETE|Tete Zambezi|Zambezi|-16.16|33.59|Mozambique|Tete"
  
  # South America
  "AMAZON-MANAUS|Manaus Amazon|Amazon|-3.11|-60.02|Brazil|Amazonas"
  "PARANA-CORRIENTES|Corrientes Paraná|Paraná|-27.47|-58.83|Argentina|Corrientes"
  "ORINOCO-CIUDADBOLIVAR|Ciudad Bolívar Orinoco|Orinoco|8.12|-63.54|Venezuela|Bolívar"
  
  # North America
  "MISSISSIPPI-MEMPHIS|Memphis Mississippi|Mississippi|35.15|-90.05|USA|Tennessee"
  "MISSOURI-KANSASCITY|Kansas City Missouri|Missouri|39.09|-94.58|USA|Missouri"
  
  # Europe (additional)
  "PO-FERRARA|Ferrara Po|Po|44.84|11.62|Italy|Emilia-Romagna"
  "RHONE-LYON|Lyon Rhône|Rhône|45.76|4.84|France|Auvergne-Rhône-Alpes"
  "VISTULA-WARSAW|Warsaw Vistula|Vistula|52.23|21.01|Poland|Masovian"
  "DNIEPER-KIEV|Kiev Dnieper|Dnieper|50.45|30.52|Ukraine|Kiev"
  "VOLGA-NIZHNY|Nizhny Novgorod Volga|Volga|56.33|44.00|Russia|Nizhny Novgorod"
  
  # Australia
  "MURRAY-ECHUCA|Echuca Murray|Murray|-36.14|144.75|Australia|Victoria"
  
  # Southeast Asia
  "IRRAWADDY-MANDALAY|Mandalay Irrawaddy|Irrawaddy|21.98|96.08|Myanmar|Mandalay"
  "SALWEEN-MOULMEIN|Moulmein Salween|Salween|16.49|97.63|Myanmar|Mon State"
)

count=0
success=0
failed=0

for station in "${stations[@]}"; do
  IFS='|' read -r code name river_basin lat lon country region <<< "$station"
  
  count=$((count + 1))
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "[$count/${#stations[@]}] Adding: $name ($country)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  response=$(curl -s -X POST "$API_URL/stations" \
    -H "Content-Type: application/json" \
    -d "{
      \"code\": \"$code\",
      \"name\": \"$name\",
      \"river_basin\": \"$river_basin\",
      \"lat\": $lat,
      \"lon\": $lon
    }")
  
  if echo "$response" | jq -e '.id' > /dev/null 2>&1; then
    station_id=$(echo "$response" | jq -r '.id')
    echo "✅ Added: ID $station_id - $name"
    success=$((success + 1))
  else
    echo "❌ Failed: $name"
    echo "   Error: $response"
    failed=$((failed + 1))
  fi
  echo ""
  sleep 0.5
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total attempted: $count"
echo "✅ Successful:   $success"
echo "❌ Failed:       $failed"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌍 Global Coverage"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Continents covered:"
echo "  🌏 Asia:          5 stations"
echo "  🌍 Africa:        4 stations"
echo "  🌎 South America: 3 stations"
echo "  🌎 North America: 2 stations"
echo "  🌍 Europe:        5 stations"
echo "  🌏 Australia:     1 station"
echo "  🌏 Southeast Asia: 2 stations"
echo ""
echo "Total global stations: $success + 5 existing = $((success + 5))"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏰ Next Steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Wait for next GloFAS ingestion (hourly)"
echo "2. Forecasts will populate for all stations"
echo "3. Refresh dashboard to see global coverage!"
echo ""
echo "Dashboard: http://192.168.178.50:5173/dashboard-figma.html"
echo ""

