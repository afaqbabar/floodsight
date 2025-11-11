# FloodSight Backend API

> **Real-time flood monitoring and forecasting API**  
> FastAPI + PostgreSQL + APScheduler orchestration

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

---

## 🏗️ Architecture

```
backend/
├── app/
│   ├── core/           # Configuration, logging, security
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── db/             # Database layer
│   │   ├── base.py     # SQLAlchemy base
│   │   ├── session.py  # Async session management
│   │   └── models.py   # Station, Forecast, Alert models
│   ├── api/v1/         # API endpoints
│   │   ├── endpoints.py
│   │   └── schemas.py
│   ├── services/       # Business logic
│   │   ├── glefas.py   # GloFAS data ingestion
│   │   ├── alerts.py   # Alert computation
│   │   └── seed.py     # Database seeding
│   ├── workers/        # Scheduled ingestion flows
│   │   └── flows.py    # APScheduler jobs
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
├── tests/              # Test suite
├── Dockerfile          # Production container
├── docker-compose.yml  # Local development
├── pyproject.toml      # Dependencies (Poetry)
└── alembic.ini         # Alembic configuration
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- **OR** Python 3.11+ and PostgreSQL 16+ with PostGIS

### Option 1: Docker (Recommended)

```bash
# Clone repository
cd floodsight/backend

# Start services (API + PostgreSQL)
docker compose up -d

# Wait for database to be ready (check logs)
docker compose logs -f db

# Run migrations
docker compose exec api alembic upgrade head

# Seed sample data
docker compose exec api python -m app.services.seed

# (Optional) Start the automated scheduler
docker compose --profile scheduler up -d scheduler

# Open API documentation
open http://localhost:8080/docs
```

### Option 2: Local Development

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Edit .env with your database URL
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/floodsight

# Run PostgreSQL with PostGIS (Docker)
docker run -d --name floodsight-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=floodsight \
  -p 5432:5432 \
  postgis/postgis:16-3.4-alpine

# Run migrations
poetry run alembic upgrade head

# Seed database
poetry run python -m app.services.seed

# Start development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Open API documentation
open http://localhost:8080/docs
```

---

## 📡 API Endpoints

### Health

| Method | Endpoint     | Description                                         |
| ------ | ------------ | --------------------------------------------------- |
| `GET`  | `/v1/health` | Health check (returns app status + DB connectivity) |
| `GET`  | `/metrics`   | Prometheus metrics                                  |

### Stations

| Method | Endpoint            | Description        |
| ------ | ------------------- | ------------------ |
| `GET`  | `/v1/stations`      | List all stations  |
| `GET`  | `/v1/stations/{id}` | Get station by ID  |
| `POST` | `/v1/stations`      | Create new station |

### Forecasts

| Method | Endpoint                   | Description                                                        |
| ------ | -------------------------- | ------------------------------------------------------------------ |
| `GET`  | `/v1/forecasts`            | List forecasts (filter by station_id)                              |
| `POST` | `/v1/forecasts`            | Create forecast                                                    |
| `POST` | `/v1/forecasts/ingest-dev` | **[NEW]** Manually trigger fake forecast ingestion (72h lead time) |

### Alerts

| Method  | Endpoint                     | Description                                     |
| ------- | ---------------------------- | ----------------------------------------------- |
| `GET`   | `/v1/alerts`                 | List alerts (filter by station_id, active_only) |
| `POST`  | `/v1/alerts`                 | Create alert                                    |
| `POST`  | `/v1/alerts/compute`         | **[NEW]** Compute alerts from recent forecasts  |
| `PATCH` | `/v1/alerts/{id}/deactivate` | Deactivate alert                                |

### Interactive API Docs

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

---

## 🗄️ Database Models

### Station

Hydrological monitoring stations

```python
{
  "id": 1,
  "code": "BERLIN-SPREE",
  "name": "Berlin Spree",
  "river_basin": "Elbe",
  "lat": 52.5200,
  "lon": 13.4050,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### Forecast

Discharge forecasts from GloFAS

```python
{
  "id": 1,
  "station_id": 1,
  "ts": "2025-01-01T12:00:00Z",
  "lead_hours": 24,
  "discharge_m3s": 1250.5,
  "water_level_m": 3.2,
  "return_period_years": 5,
  "source": "GloFAS",
  "model_run": "2025-01-01T00:00:00Z",
  "created_at": "2025-01-01T06:00:00Z"
}
```

### Alert

Flood alerts/warnings

```python
{
  "id": 1,
  "station_id": 1,
  "issued_at": "2025-01-01T12:00:00Z",
  "level": "warning",  // "info" | "warning" | "severe" | "extreme"
  "probability": 0.75,
  "message": "Elevated discharge forecast. Monitor closely.",
  "valid_from": "2025-01-01T12:00:00Z",
  "valid_until": "2025-01-03T12:00:00Z",
  "is_active": true
}
```

---

## 🔄 Database Migrations

We use **Alembic** for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "add user table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

---

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_api.py

# Run with verbose output
poetry run pytest -v
```

---

## 🌊 Data Ingestion & Alert Computation

### Phase B - Data Flow (✅ Complete)

**End-to-End Workflow:**

```bash
# 1. Seed sample stations (if not already done)
docker compose exec api python -m app.services.seed

# 2. Ingest fake forecasts (72-hour lead time)
curl -X POST http://localhost:8080/v1/forecasts/ingest-dev

# 3. Compute alerts from forecasts
curl -X POST http://localhost:8080/v1/alerts/compute

# 4. View active alerts
curl http://localhost:8080/v1/alerts?active_only=true
```

### Alert Computation Logic

**Discharge Thresholds:**

- **Info**: 800+ m³/s
- **Warning**: 1200+ m³/s
- **Severe**: 1600+ m³/s
- **Extreme**: 2000+ m³/s

**Probability Calculation:**

- ≤24h lead time: 85% probability
- 25-48h lead time: 70% probability
- 49-72h lead time: 55% probability

**Process:**

1. Analyzes recent forecasts (last 6 hours of model runs)
2. Finds maximum discharge for each station
3. Determines alert level based on thresholds
4. Calculates probability based on forecast lead time
5. Deactivates old alerts and creates new ones

### Phase B2 - Automated Scheduler (✅ Complete)

**Scheduler Service:**

The scheduler automatically runs the ingestion flow hourly using APScheduler:

```bash
# Start the scheduler (runs hourly at :00)
docker compose --profile scheduler up -d scheduler

# View scheduler logs
docker compose logs -f scheduler

# Stop the scheduler
docker compose stop scheduler

# Run ingestion manually (once)
docker compose run --rm scheduler python -m app.workers.flows once
```

**Features:**

- ✅ **Hourly Ingestion**: Runs at the top of every hour (`0 * * * *`)
- ✅ **Automatic Alert Computation**: Computes alerts immediately after ingestion
- ✅ **Startup Job**: Runs ingestion once on startup, then schedules future runs
- ✅ **Graceful Shutdown**: Handles SIGTERM/SIGINT signals
- ✅ **Error Resilience**: Continues scheduling even if a job fails
- ✅ **Single Instance**: Prevents overlapping runs

**Scheduler Architecture:**

- **Technology**: APScheduler (alternative to Prefect due to version conflicts)
- **Schedule**: Hourly cron job (`0 * * * *`)
- **Flow**: Ingest forecasts → Compute alerts → Store results
- **Logging**: Detailed logs with timestamps and emojis for readability

**Customizing the Schedule:**

Edit `app/workers/flows.py`:

```python
# Change from hourly to every 3 hours
schedule = "0 */3 * * *"

# Or every 30 minutes
schedule = "*/30 * * * *"

# Or daily at 3 AM
schedule = "0 3 * * *"
```

### Manual Ingestion (Fake Data)

```bash
# Via API
curl -X POST http://localhost:8080/v1/forecasts/ingest-dev

# Via Python script (inside container)
docker compose exec api python -m app.services.glefas
```

### Real GloFAS Data (TODO - Phase C)

```python
# app/services/glefas.py will be extended to:
# 1. Download GRIB files from ECMWF CDS
# 2. Parse with xarray + cfgrib
# 3. Extract discharge at station coordinates
# 4. Store forecasts in database

# Example workflow:
# import xarray as xr
# ds = xr.open_dataset('glofas.grib', engine='cfgrib')
# discharge = ds.sel(latitude=lat, longitude=lon, method='nearest')
```

---

## 📊 Monitoring

### Prometheus Metrics

```bash
# Access metrics endpoint
curl http://localhost:8080/metrics

# Example metrics:
# - floodsight_requests_total{method="GET",endpoint="/v1/stations",status="200"} 42
# - floodsight_request_duration_seconds_bucket{method="GET",endpoint="/v1/stations"} 0.025
```

### Health Check

```bash
curl http://localhost:8080/v1/health
```

---

## 🐳 Docker

### Build Image

```bash
docker build -t floodsight-backend:latest .
```

### Run Container

```bash
docker run -d \
  --name floodsight-api \
  -p 8080:8080 \
  -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/floodsight \
  floodsight-backend:latest
```

### Docker Compose Profiles

```bash
# Default: API + Database
docker compose up

# Development mode (hot reload)
docker compose --profile dev up

# With Prefect orchestration
docker compose --profile prefect up

# With Redis caching
docker compose --profile cache up

# All services
docker compose --profile dev --profile prefect --profile cache up
```

---

## 🔐 Security

### Authentication (Development)

- Auth is **optional** in dev mode (`DEBUG=true`)
- Requests without auth token get a mock user

### Authentication (Production - TODO)

```python
# Integrate with Supabase JWKS
# See app/core/security.py for implementation notes
```

### Environment Variables

Never commit `.env` files! Always use `.env.example` as a template.

```bash
# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🚀 Deployment

### Kubernetes (K3s on Raspberry Pi)

```bash
# Deployment manifests are in /deploy/k8s/
# See root README for full deployment instructions

# Quick deploy
kubectl apply -k deploy/k8s/overlays/production
```

### Environment Variables

Set these in Kubernetes secrets or ConfigMaps:

- `DATABASE_URL`
- `SECRET_KEY`
- `SUPABASE_JWKS_URL` (for production auth)
- `PREFECT_API_URL` (if using Prefect)

---

## 📝 Development Workflow

### 1. Make Changes

```bash
# Edit code in app/
# FastAPI will auto-reload in dev mode
```

### 2. Create Migration

```bash
alembic revision --autogenerate -m "description"
```

### 3. Test Locally

```bash
docker compose up
# Test endpoints at http://localhost:8080/docs
```

### 4. Run Tests

```bash
poetry run pytest
```

### 5. Format Code

```bash
poetry run black app/
poetry run ruff check app/
```

---

## 🔧 Troubleshooting

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker compose ps

# Check database logs
docker compose logs db

# Reset database
docker compose down -v
docker compose up -d
```

### Migration Errors

```bash
# Drop all tables and recreate
docker compose exec api alembic downgrade base
docker compose exec api alembic upgrade head
```

### Port Conflicts

```bash
# If port 8080 is in use, change in docker-compose.yml
ports:
  - "8081:8080"  # Use 8081 instead
```

---

## 📦 Dependencies

### Core

- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM with async support
- **asyncpg** - Async PostgreSQL driver
- **alembic** - Database migrations
- **pydantic-settings** - Settings management

### Data

- **GeoAlchemy2** - PostGIS integration
- **httpx** - Async HTTP client

### Monitoring

- **prometheus-client** - Metrics

### Orchestration

- **Prefect** - Workflow orchestration (Phase B2)

---

## 🛣️ Roadmap

### ✅ Phase A - Complete

- [x] FastAPI + SQLAlchemy (async)
- [x] PostgreSQL (Alpine, ARM64-compatible)
- [x] Database models (Station, Forecast, Alert)
- [x] API endpoints (/health, /stations, /forecasts, /alerts)
- [x] Alembic migrations
- [x] Docker + Docker Compose
- [x] Prometheus metrics
- [x] Seed script

### ✅ Phase B - Data Flow (Complete)

- [x] `POST /v1/forecasts/ingest-dev` endpoint
- [x] `POST /v1/alerts/compute` endpoint
- [x] Alert computation logic with thresholds
- [x] Probability calculation based on lead time
- [x] End-to-end test flow working

### ✅ Phase B2 - Automated Scheduler (Complete)

- [x] APScheduler integration (alternative to Prefect)
- [x] Scheduled ingestion flow (hourly)
- [x] Automated alert computation after ingestion
- [x] Docker Compose scheduler service
- [x] Manual run capability
- [x] Graceful shutdown handling

### ⏳ Phase C - DevSecOps

- [ ] GitHub Actions CI/CD
- [ ] Container scanning (Trivy)
- [ ] K8s deployment manifests
- [ ] Vercel API proxy configuration

---

## 📞 Support

- **Issues**: https://github.com/afaqbabar/floodsight/issues
- **Email**: hello@floodsight.com

---

## 📄 License

MIT License - see [LICENSE](../LICENSE)

---

Built with ❤️ for climate resilience.
