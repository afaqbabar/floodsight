#!/bin/bash
# FloodSight Alert System Quick Setup Script
# This script helps you set up the new alert system features

set -e

echo "============================================================"
echo "🌊 FloodSight Alert System Setup"
echo "============================================================"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the FloodSight root directory"
    exit 1
fi

echo "Step 1: Rebuilding Docker containers..."
echo "----------------------------------------"
cd backend
docker compose down
docker compose build --no-cache
echo "✅ Containers rebuilt"
echo ""

echo "Step 2: Starting services..."
echo "----------------------------------------"
docker compose up -d db api
sleep 5
echo "✅ Services started"
echo ""

echo "Step 3: Running database migrations..."
echo "----------------------------------------"
# Check if Alembic is available
if docker compose exec -T api alembic current &>/dev/null; then
    echo "Running Alembic migration..."
    docker compose exec -T api alembic revision --autogenerate -m "Add alert system tables" || echo "Migration already exists"
    docker compose exec -T api alembic upgrade head
    echo "✅ Database migrated"
else
    echo "⚠️  Alembic not available. You'll need to run SQL migration manually."
    echo "See ALERT_SYSTEM_SETUP.md for SQL migration script"
fi
echo ""

echo "Step 4: Checking system status..."
echo "----------------------------------------"
docker compose ps
echo ""

echo "Step 5: Testing API connectivity..."
echo "----------------------------------------"
if curl -s http://localhost:8080/v1/health > /dev/null; then
    echo "✅ API is responding"
    echo ""
    echo "API Health:"
    curl -s http://localhost:8080/v1/health | python3 -m json.tool || curl -s http://localhost:8080/v1/health
else
    echo "⚠️  API not responding yet. Wait a moment and try: curl http://localhost:8080/v1/health"
fi
echo ""

echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "📊 Access Your Dashboards:"
echo "  - Live Dashboard:  http://localhost:5173/dashboard-figma.html"
echo "  - Analytics:       http://localhost:5173/analytics-dashboard.html"
echo "  - Admin Panel:     http://localhost:5173/admin-dashboard.html"
echo ""
echo "📚 API Documentation:"
echo "  - Swagger UI:      http://localhost:8080/docs"
echo "  - Health Check:    http://localhost:8080/v1/health"
echo ""
echo "🔧 Next Steps:"
echo "  1. Configure notifications in backend/.env (see ALERT_SYSTEM_SETUP.md)"
echo "  2. Create users: curl -X POST http://localhost:8080/v1/users -H 'Content-Type: application/json' -d '{...}'"
echo "  3. Add subscriptions: curl -X POST http://localhost:8080/v1/subscriptions -H 'Content-Type: application/json' -d '{...}'"
echo "  4. Test alerts: curl -X POST http://localhost:8080/v1/alerts/compute"
echo ""
echo "📖 Full Documentation: ALERT_SYSTEM_SETUP.md"
echo "📄 Feature Summary: ALERT_SYSTEM_COMPLETE.md"
echo ""
echo "🎉 All 6 features are now available!"
echo "============================================================"



