#!/bin/bash
# Quick Start: Expose Pi Backend to Vercel

echo "🚀 FloodSight - Cloudflare Tunnel Quick Start"
echo "=============================================="
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Installing cloudflared..."
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
    sudo dpkg -i cloudflared-linux-arm64.deb
    rm cloudflared-linux-arm64.deb
    echo "✅ cloudflared installed"
else
    echo "✅ cloudflared already installed"
fi

echo ""
echo "🌐 Starting Cloudflare Tunnel..."
echo "📋 Copy the URL shown below and use it in your frontend"
echo ""
echo "To stop: Press Ctrl+C"
echo "=========================================="
echo ""

cloudflared tunnel --url http://localhost:8080
