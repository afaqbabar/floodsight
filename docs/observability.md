# FloodSight Observability Guide

## 📊 Overview

FloodSight implements a comprehensive observability stack across both backend (FastAPI) and frontend (Vite/Vanilla JS) to enable monitoring, debugging, and performance analysis.

### Architecture

```
Frontend (Vite/JS)               Backend (FastAPI/Python)
┌─────────────────────┐         ┌──────────────────────────┐
│ Error Tracking      │────────▶│ /v1/telemetry           │
│ errorReporter.js    │         │ (receives client events) │
└─────────────────────┘         └──────────────────────────┘
                                           │
                                           ▼
┌─────────────────────┐         ┌──────────────────────────┐
│ Browser Console     │         │ Structured Logging       │
│ (Development)       │         │ • JSON (production)      │
└─────────────────────┘         │ • Colored (development)  │
                                └──────────────────────────┘
                                           │
                                           ▼
                                ┌──────────────────────────┐
                                │ /v1/health               │
                                │ (uptime, memory, CPU)    │
                                └──────────────────────────┘
                                           │
                                           ▼
                                ┌──────────────────────────┐
                                │ /metrics                 │
                                │ (Prometheus format)      │
                                └──────────────────────────┘
                                           │
                                           ▼
                                ┌──────────────────────────┐
                                │ Sentry (optional)        │
                                │ (error aggregation)      │
                                └──────────────────────────┘
```

---

## 🎯 Components

### 1. Backend Observability (FastAPI/Python)

#### Structured Logging

**Location:** `backend/app/core/logging.py`

**Features:**
- **Development mode:** Colored console logs for easy reading
- **Production mode:** JSON-structured logs for log aggregators (e.g., ELK, Splunk, CloudWatch)
- Configurable log levels
- Automatic exception tracking

**Usage:**

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

logger.info("Processing request")
logger.warning("High memory usage", extra={"memory_mb": 512})
logger.error("Failed to fetch data", exc_info=True)
```

#### Metrics (Prometheus)

**Location:** `backend/app/main.py`

**Endpoint:** `/metrics`

**Metrics Exposed:**
- `floodsight_requests_total` - Total HTTP requests (Counter)
- `floodsight_request_duration_seconds` - Request duration histogram
- `floodsight_process_memory_bytes` - Process memory usage (Gauge)
- `floodsight_process_cpu_percent` - Process CPU usage percentage (Gauge)

**Example output:**

```
# HELP floodsight_requests_total Total HTTP requests
# TYPE floodsight_requests_total counter
floodsight_requests_total{endpoint="/v1/stations",method="GET",status="200"} 142.0

# HELP floodsight_request_duration_seconds HTTP request duration in seconds
# TYPE floodsight_request_duration_seconds histogram
floodsight_request_duration_seconds_bucket{endpoint="/v1/stations",method="GET",le="0.005"} 45.0
floodsight_request_duration_seconds_bucket{endpoint="/v1/stations",method="GET",le="0.01"} 89.0
...

# HELP floodsight_process_memory_bytes Process memory usage in bytes
# TYPE floodsight_process_memory_bytes gauge
floodsight_process_memory_bytes 251658240.0

# HELP floodsight_process_cpu_percent Process CPU usage percentage
# TYPE floodsight_process_cpu_percent gauge
floodsight_process_cpu_percent 2.5
```

#### Health Check

**Endpoint:** `/v1/health`

**Response:**

```json
{
  "status": "ok",
  "app": "FloodSight Backend API",
  "version": "0.1.0",
  "environment": "production",
  "database": "connected",
  "uptime_seconds": 3600.5,
  "memory_mb": 240.2,
  "cpu_percent": 1.8
}
```

**Usage:**
- **Kubernetes:** Liveness and readiness probes
- **Monitoring:** Uptime checks (e.g., UptimeRobot, Pingdom)
- **Load balancer:** Health checks

#### Error Reporting (Sentry Integration)

**Location:** `backend/app/core/errors.py`

**Functions:**

```python
from app.core.errors import report_error, report_message, set_user_context

# Report an exception
try:
    risky_operation()
except Exception as e:
    report_error(e, context={"user_id": "123", "action": "data_sync"})

# Report a message (non-exception event)
report_message("Database migration completed", level="info")

# Set user context for error tracking
set_user_context(user_id="user_123", email="user@example.com")
```

#### Telemetry Endpoint

**Endpoint:** `/v1/telemetry` (POST)

**Purpose:** Receive client-side events from the frontend

**Request body:**

```json
{
  "event_name": "client_error",
  "timestamp": "2025-01-15T10:30:00Z",
  "page": "/dashboard",
  "user_agent": "Mozilla/5.0...",
  "context": {
    "error_message": "Failed to fetch stations",
    "stack": "Error: ...",
    "screen_width": 1920,
    "screen_height": 1080
  }
}
```

**Response:**

```json
{
  "status": "ok",
  "message": "Event received"
}
```

---

### 2. Frontend Observability (Vite/JavaScript)

#### Error Reporter

**Location:** `public/assets/js/errorReporter.js`

**Features:**
- Global error handler (window.onerror)
- Unhandled promise rejection handler
- Page load performance tracking
- Manual error reporting
- User action tracking

**Usage:**

```javascript
import { reportError, reportEvent, trackAction } from './errorReporter.js';

// Automatic error tracking (already initialized)
// All unhandled errors are automatically sent to backend

// Manual error reporting
try {
  riskyOperation();
} catch (error) {
  reportError(error, { context: 'station_fetch', station_id: 5 });
}

// Track custom events
reportEvent('map_zoomed', { zoom_level: 12, center: [50.1, 8.6] });

// Track user actions
trackAction('station_selected', { station_id: 3, station_name: 'Cologne Rhine' });
```

**Automatic Tracking:**

The error reporter automatically tracks:
- JavaScript errors (syntax, runtime)
- Unhandled promise rejections
- Page load performance
- Network errors (fetch failures)

---

## ⚙️ Configuration

### Environment Variables

#### Backend (FastAPI)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `DEBUG` | boolean | `false` | Enable debug mode (colored logs, auto-reload) |
| `ENVIRONMENT` | string | `development` | Environment name: `development`, `staging`, `production` |
| `METRICS_ENABLED` | boolean | `false` | Enable Prometheus metrics endpoint |
| `SENTRY_DSN` | string | ` ` | Sentry Data Source Name (optional, for error tracking) |
| `SENTRY_TRACES_SAMPLE_RATE` | float | `0.1` | Percentage of transactions to trace (0.0-1.0) |
| `SENTRY_PROFILES_SAMPLE_RATE` | float | `0.1` | Percentage of traces to profile (0.0-1.0) |

#### Frontend (Vite)

The frontend error reporter uses the `BASE_URL` from `api-service.js` to determine the backend API URL.

---

## 🚀 Getting Started

### Local Development

#### Backend

1. **Install dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

2. **Set environment variables:**

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
export METRICS_ENABLED=true
# Optionally, add Sentry DSN
export SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

3. **Run the backend:**

```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

4. **Test endpoints:**

```bash
# Health check
curl http://localhost:8080/v1/health | jq

# Metrics (if enabled)
curl http://localhost:8080/metrics
```

#### Frontend

1. **Install dependencies:**

```bash
npm install
```

2. **Run development server:**

```bash
npm run dev
```

3. **Open browser console:**
   - You should see: `[ErrorReporter] Initializing error tracking...`
   - Test error reporting: `throw new Error("Test error")`
   - Check backend logs for telemetry events

---

### Production Deployment

#### Backend (Kubernetes)

1. **Set environment variables in ConfigMap:**

```yaml
# deploy/k8s/base/backend-configmap.yaml
data:
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "production"
  METRICS_ENABLED: "true"
```

2. **Set secrets:**

```yaml
# deploy/k8s/base/backend-secrets.yaml
stringData:
  sentry-dsn: "https://your-sentry-dsn@sentry.io/project-id"
```

3. **Update deployment to inject secrets:**

```yaml
# deploy/k8s/base/backend-deployment.yaml
env:
  - name: SENTRY_DSN
    valueFrom:
      secretKeyRef:
        name: floodsight-backend-secrets
        key: sentry-dsn
        optional: true
```

4. **Deploy:**

```bash
kubectl apply -k deploy/k8s/base
```

5. **Verify health:**

```bash
kubectl port-forward -n floodsight svc/floodsight-backend 8080:8080
curl http://localhost:8080/v1/health | jq
```

#### Frontend (Vercel)

1. **Ensure `BASE_URL` in `api-service.js` points to production backend**

2. **Deploy:**

```bash
git push origin main  # Vercel auto-deploys from main branch
```

3. **Test error tracking:**
   - Open browser console on production site
   - Trigger an error
   - Check backend logs for telemetry events

---

## 📈 Monitoring Setup

### Prometheus + Grafana (Kubernetes)

1. **Install Prometheus Operator:**

```bash
kubectl create namespace monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
```

2. **Create ServiceMonitor:**

```yaml
# deploy/k8s/base/backend-servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: floodsight-backend
  namespace: floodsight
spec:
  selector:
    matchLabels:
      app: floodsight
      component: backend
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

3. **Apply:**

```bash
kubectl apply -f deploy/k8s/base/backend-servicemonitor.yaml
```

4. **Access Grafana:**

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Visit: http://localhost:3000 (default user/pass: `admin/prom-operator`)

5. **Import dashboard:**
   - Create a new dashboard
   - Add panels for:
     - Request rate: `rate(floodsight_requests_total[5m])`
     - Request duration (p95): `histogram_quantile(0.95, rate(floodsight_request_duration_seconds_bucket[5m]))`
     - Memory usage: `floodsight_process_memory_bytes / 1024 / 1024` (MB)
     - CPU usage: `floodsight_process_cpu_percent`

---

### Sentry Setup

1. **Create Sentry account:** https://sentry.io

2. **Create new project:** Select Python/FastAPI

3. **Copy DSN:** e.g., `https://abc123...@o123456.ingest.sentry.io/7891011`

4. **Set environment variable:**

```bash
# Local
export SENTRY_DSN=https://your-dsn@sentry.io/project-id

# Kubernetes
kubectl create secret generic floodsight-backend-secrets \
  --from-literal=sentry-dsn=https://your-dsn@sentry.io/project-id \
  -n floodsight
```

5. **Deploy and test:**

```bash
# Backend will log: "Sentry initialized successfully"
```

6. **Trigger test error:**

```python
# In any endpoint or function
from app.core.errors import report_error
report_error(Exception("Test error for Sentry"))
```

7. **Check Sentry dashboard:** You should see the error appear within seconds

---

## 🧪 Testing

### Manual Testing

#### Backend Health Check

```bash
curl -X GET http://localhost:8080/v1/health | jq
# Expected: 200 OK with status, uptime, memory, cpu
```

#### Backend Metrics

```bash
curl -X GET http://localhost:8080/metrics
# Expected: Prometheus text format with metrics
```

#### Backend Telemetry

```bash
curl -X POST http://localhost:8080/v1/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "test_event",
    "timestamp": "2025-01-15T10:00:00Z",
    "page": "/test",
    "user_agent": "curl",
    "context": {"test": true}
  }'
# Expected: 200 OK with {"status": "ok", "message": "Event received"}
# Check backend logs for telemetry event
```

#### Frontend Error Tracking

1. Open browser console on http://localhost:5173
2. Run: `throw new Error("Test error")`
3. Check browser console: `[ErrorReporter] Capturing error: ...`
4. Check backend logs: `Telemetry event: client_error`

---

## 🛠️ Troubleshooting

### Logs not showing in JSON format

**Problem:** Logs are still text-based in production

**Solution:** Ensure both conditions are met:
- `ENVIRONMENT=production`
- `DEBUG=false`

```bash
export ENVIRONMENT=production
export DEBUG=false
```

---

### Metrics endpoint returns 404

**Problem:** `/metrics` returns 404 Not Found

**Solution:** Enable metrics:

```bash
export METRICS_ENABLED=true
```

Restart backend and verify:

```bash
curl http://localhost:8080/metrics
```

---

### Sentry not receiving errors

**Problem:** Errors not appearing in Sentry dashboard

**Checklist:**
1. ✅ `SENTRY_DSN` is set correctly
2. ✅ Backend logs show: `Sentry initialized successfully`
3. ✅ `sentry-sdk` is installed: `pip install sentry-sdk`
4. ✅ DSN format is correct: `https://[key]@[org].ingest.sentry.io/[project]`

**Test:**

```python
from app.core.errors import report_error
report_error(Exception("Test Sentry integration"))
```

---

### Frontend errors not reaching backend

**Problem:** Browser shows errors but backend doesn't log them

**Checklist:**
1. ✅ `errorReporter.js` is imported in the page
2. ✅ `BASE_URL` in `api-service.js` points to the correct backend
3. ✅ CORS is configured correctly in backend
4. ✅ Network tab shows POST to `/v1/telemetry` (check for 200 OK)

**Test:**

```javascript
import { reportError } from './errorReporter.js';
reportError(new Error("Test frontend error"));
```

---

### High memory usage

**Problem:** Backend memory usage increasing over time

**Solution:**
1. Check metrics: `curl http://localhost:8080/metrics | grep memory`
2. Check health: `curl http://localhost:8080/v1/health | jq .memory_mb`
3. Investigate:
   - Database connection pooling
   - Large result sets
   - Memory leaks in async tasks

---

## 📚 Best Practices

### Logging

✅ **Do:**
- Use structured logging with context:
  ```python
  logger.info("User logged in", extra={"user_id": user_id, "ip": request.client.host})
  ```
- Use appropriate log levels:
  - `DEBUG`: Detailed diagnostic information
  - `INFO`: General informational messages
  - `WARNING`: Warning messages (recoverable issues)
  - `ERROR`: Error messages (exceptions, failures)
  - `CRITICAL`: Critical issues (system failure)

❌ **Don't:**
- Log sensitive information (passwords, tokens, credit cards)
- Use `print()` statements (use `logger` instead)
- Log in tight loops (high volume)

---

### Metrics

✅ **Do:**
- Use counters for totals (requests, errors)
- Use histograms for durations (request time, query time)
- Use gauges for current values (memory, connections)
- Add labels for dimensions (method, endpoint, status)

❌ **Don't:**
- Add high-cardinality labels (user_id, session_id)
- Create too many metrics (start small, add as needed)
- Use metrics for logging (use logger instead)

---

### Error Reporting

✅ **Do:**
- Add context to errors:
  ```python
  report_error(e, context={"user_id": user_id, "action": "checkout"})
  ```
- Set user context when available:
  ```python
  set_user_context(user_id="123", email="user@example.com")
  ```
- Report critical errors and warnings

❌ **Don't:**
- Report every minor error (use logging for debug issues)
- Include PII (Personally Identifiable Information) in context
- Swallow exceptions without logging

---

## 🔐 Security Considerations

1. **Metrics Endpoint:**
   - Protected by `METRICS_ENABLED` flag (default: `false`)
   - Consider adding authentication in production:
     ```python
     # Example: Simple token auth for /metrics
     @app.get("/metrics")
     async def metrics(token: str = Header(None)):
         if token != os.getenv("METRICS_AUTH_TOKEN"):
             raise HTTPException(status_code=403)
         ...
     ```

2. **Telemetry Endpoint:**
   - Rate limit to prevent abuse
   - Validate input data
   - Don't trust client-provided data

3. **Logging:**
   - Never log passwords, tokens, or sensitive data
   - Use `extra` fields for structured data
   - Redact sensitive fields before logging

4. **Sentry:**
   - Use `before_send` hook to scrub sensitive data
   - Set appropriate data retention policies
   - Configure IP address anonymization

---

## 📖 References

- [FastAPI Monitoring](https://fastapi.tiangolo.com/advanced/monitoring/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [Structured Logging Best Practices](https://www.structlog.org/en/stable/why.html)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

---

## ✅ Quick Reference

### Backend Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/health` | GET | Health check with metrics |
| `/metrics` | GET | Prometheus metrics (if enabled) |
| `/v1/telemetry` | POST | Receive frontend events |
| `/docs` | GET | API documentation (Swagger UI) |

### Backend Files

| File | Purpose |
|------|---------|
| `app/core/logging.py` | Logging configuration |
| `app/core/errors.py` | Error reporting (Sentry) |
| `app/main.py` | App initialization, metrics |
| `app/api/v1/endpoints.py` | API endpoints (health, telemetry) |

### Frontend Files

| File | Purpose |
|------|---------|
| `public/assets/js/errorReporter.js` | Error tracking & telemetry |
| `public/assets/js/api-service.js` | API client (BASE_URL) |

---

**Last Updated:** January 15, 2025  
**Version:** 1.0.0

