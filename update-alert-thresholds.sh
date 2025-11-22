#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚨 FloodSight Alert Threshold Updater"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Display current thresholds
echo "📊 Current Alert Thresholds:"
echo ""
kubectl get configmap floodsight-backend-config -n floodsight -o jsonpath='{.data.ALERT_THRESHOLD_INFO}' | xargs -I {} echo "  Info:     {} m³/s"
kubectl get configmap floodsight-backend-config -n floodsight -o jsonpath='{.data.ALERT_THRESHOLD_WARNING}' | xargs -I {} echo "  Warning:  {} m³/s"
kubectl get configmap floodsight-backend-config -n floodsight -o jsonpath='{.data.ALERT_THRESHOLD_SEVERE}' | xargs -I {} echo "  Severe:   {} m³/s"
kubectl get configmap floodsight-backend-config -n floodsight -o jsonpath='{.data.ALERT_THRESHOLD_EXTREME}' | xargs -I {} echo "  Extreme:  {} m³/s"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Preset Configurations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Small Rivers (Main, Elbe, Spree)"
echo "   Info: 300, Warning: 600, Severe: 1000, Extreme: 1500"
echo ""
echo "2. Medium Rivers (Balanced for all 5 rivers)"
echo "   Info: 600, Warning: 1500, Severe: 3000, Extreme: 5000"
echo ""
echo "3. Large Rivers (Rhine, Danube)"
echo "   Info: 2500, Warning: 4000, Severe: 6000, Extreme: 8000"
echo ""
echo "4. Custom (enter your own values)"
echo ""
echo "5. Cancel"
echo ""

read -p "Select preset (1-5): " PRESET

case $PRESET in
  1)
    INFO=300
    WARNING=600
    SEVERE=1000
    EXTREME=1500
    PRESET_NAME="Small Rivers"
    ;;
  2)
    INFO=600
    WARNING=1500
    SEVERE=3000
    EXTREME=5000
    PRESET_NAME="Medium Rivers (Balanced)"
    ;;
  3)
    INFO=2500
    WARNING=4000
    SEVERE=6000
    EXTREME=8000
    PRESET_NAME="Large Rivers"
    ;;
  4)
    echo ""
    read -p "Enter Info threshold (m³/s): " INFO
    read -p "Enter Warning threshold (m³/s): " WARNING
    read -p "Enter Severe threshold (m³/s): " SEVERE
    read -p "Enter Extreme threshold (m³/s): " EXTREME
    PRESET_NAME="Custom"
    ;;
  5)
    echo "Cancelled."
    exit 0
    ;;
  *)
    echo "Invalid selection."
    exit 1
    ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 New Configuration: $PRESET_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Info:     $INFO m³/s"
echo "  Warning:  $WARNING m³/s"
echo "  Severe:   $SEVERE m³/s"
echo "  Extreme:  $EXTREME m³/s"
echo ""

read -p "Apply these thresholds? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
  echo "Cancelled."
  exit 0
fi

echo ""
echo "🔄 Applying new thresholds..."

kubectl patch configmap floodsight-backend-config -n floodsight --type merge -p "{
  \"data\": {
    \"ALERT_THRESHOLD_INFO\": \"$INFO\",
    \"ALERT_THRESHOLD_WARNING\": \"$WARNING\",
    \"ALERT_THRESHOLD_SEVERE\": \"$SEVERE\",
    \"ALERT_THRESHOLD_EXTREME\": \"$EXTREME\"
  }
}"

echo "✅ ConfigMap updated"
echo ""
echo "🔄 Restarting services..."

kubectl rollout restart deployment floodsight-backend -n floodsight
kubectl rollout restart deployment floodsight-scheduler -n floodsight

echo "⏳ Waiting for pods to restart..."
sleep 15

echo "✅ Services restarted"
echo ""
echo "🧮 Recomputing alerts with new thresholds..."

curl -X POST http://192.168.178.50:30636/v1/alerts/compute 2>/dev/null | jq

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Alert Thresholds Updated!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 New Active Alerts:"
curl -s http://192.168.178.50:30636/v1/alerts | jq -r '.[] | "  \(.level | ascii_upcase): \(.message)"'
echo ""
echo "🌐 Refresh your dashboard: http://192.168.178.50:5173/dashboard-figma.html"
echo "   Press Ctrl + Shift + R to hard refresh"
echo ""

