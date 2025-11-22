#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Updating Cloudflare Tunnel for Backend API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Stop existing tunnel
echo "🛑 Stopping existing tunnel (port 8080)..."
pkill -f "cloudflared tunnel --url http://localhost:8080"
sleep 2

# Check backend is running
echo ""
echo "📊 Checking backend status..."
curl -s http://192.168.178.50:30636/v1/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend API is running"
else
    echo "❌ Backend API not responding!"
    echo "   Start it first: kubectl get pods -n floodsight"
    exit 1
fi

# Start new tunnel
echo ""
echo "🚀 Starting Cloudflare tunnel for backend API..."
echo "   Local: http://192.168.178.50:30636"
echo ""

# Use quick tunnel (no account needed)
cloudflared tunnel --url http://192.168.178.50:30636 &

sleep 5

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Tunnel Started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Check the Cloudflare tunnel URL above ☝️"
echo ""
echo "📋 Next steps:"
echo "  1. Copy the *.trycloudflare.com URL"
echo "  2. Add to Vercel environment variables:"
echo "     VITE_API_URL=https://YOUR_URL.trycloudflare.com"
echo "  3. Redeploy your Vercel frontend"
echo ""
echo "💡 To check tunnel status:"
echo "   ps aux | grep cloudflared"
echo ""
echo "💡 To stop tunnel:"
echo "   pkill cloudflared"
echo ""

