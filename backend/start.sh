#!/bin/bash

echo "🌊 FloodSight Backend - Quick Start"
echo "===================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Start services
echo "🚀 Starting services (API + PostgreSQL)..."
docker compose up -d

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 5

# Check if database is ready
until docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do
    echo "   Waiting for PostgreSQL..."
    sleep 2
done

echo "✅ Database is ready"
echo ""

# Run migrations
echo "🔄 Running database migrations..."
docker compose exec -T api alembic upgrade head

echo ""

# Seed database
echo "🌱 Seeding sample data..."
docker compose exec -T api python -m app.services.seed

echo ""
echo "=" * 60
echo "🎉 Backend is ready!"
echo "=" * 60
echo ""
echo "📖 API Documentation: http://localhost:8080/docs"
echo "💚 Health Check:      http://localhost:8080/v1/health"
echo "📊 Metrics:           http://localhost:8080/metrics"
echo ""
echo "🔍 View logs:  docker compose logs -f api"
echo "🛑 Stop:       docker compose down"
echo ""
