#!/bin/bash

# Quick script to update design tokens and see changes
# Usage: ./UPDATE_DESIGN.sh

echo "🎨 FloodSight Design Token Updater"
echo "=================================="
echo ""

# Step 1: Check if figma-tokens.json exists
if [ ! -f "design/figma-tokens.json" ]; then
    echo "❌ Error: design/figma-tokens.json not found!"
    exit 1
fi

echo "✅ Found design/figma-tokens.json"
echo ""

# Step 2: Generate CSS from tokens
echo "🔄 Generating CSS from tokens..."
npm run tokens:apply

if [ $? -eq 0 ]; then
    echo "✅ CSS generated successfully!"
else
    echo "❌ Failed to generate CSS"
    exit 1
fi

echo ""

# Step 3: Check if dev server is running
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Dev server is running"
    echo "🌐 View changes at: http://192.168.178.50:5173"
    echo ""
    echo "💡 Tip: The page should auto-refresh. If not, press Ctrl+Shift+R"
else
    echo "⚠️  Dev server is not running"
    echo "Starting dev server..."
    npm run dev &
    sleep 3
    echo "✅ Dev server started"
    echo "🌐 View at: http://192.168.178.50:5173"
fi

echo ""
echo "📝 Changes applied! Check your browser."
echo ""
echo "To revert changes, run: git checkout design/figma-tokens.json"

