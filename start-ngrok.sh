#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 FloodSight API - ngrok Tunnel"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if backend is running
echo "📊 Checking backend status..."
kubectl get pods -n floodsight | grep backend | grep -q Running
if [ $? -eq 0 ]; then
    echo "✅ Backend is running"
else
    echo "❌ Backend not running! Start it first:"
    echo "   kubectl get pods -n floodsight"
    exit 1
fi

# Test backend locally
echo ""
echo "🧪 Testing backend locally..."
curl -s http://192.168.178.50:30636/v1/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend API responding"
else
    echo "❌ Backend API not responding!"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Setup Instructions:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Get your ngrok authtoken:"
echo "   → Visit: https://dashboard.ngrok.com/get-started/your-authtoken"
echo ""
echo "2. Configure ngrok (first time only):"
echo "   → Run: ngrok config add-authtoken YOUR_TOKEN"
echo ""
echo "3. This script will start the tunnel"
echo ""
echo "4. Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)"
echo ""
echo "5. Add to Vercel environment variables:"
echo "   → Variable: VITE_API_URL or NEXT_PUBLIC_API_URL"
echo "   → Value: https://abc123.ngrok-free.app"
echo ""
echo "6. Redeploy your Vercel frontend"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press Enter to start ngrok tunnel..."
echo ""

# Start ngrok
echo "🌐 Starting ngrok tunnel..."
echo "   Local: http://192.168.178.50:30636"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Copy the HTTPS URL below and add to Vercel!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ngrok http 192.168.178.50:30636

