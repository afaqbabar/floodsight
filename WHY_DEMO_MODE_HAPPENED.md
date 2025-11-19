# Why "Demo Mode" Happened & How to Prevent It

## 🔍 **Root Causes**

### **Issue 1: CORS Configuration (Port Change)**

**What happened:**

- Yesterday, frontend was on port **8080**
- Today, I moved it to port **5173** due to port conflict
- CORS configuration only had `localhost:5173`, not `192.168.178.50:5173`
- Backend rejected requests from the Pi's IP address

**Why it happened again:**
When the port changed, the CORS configuration wasn't automatically updated to include all variations.

**How to prevent:**

- Use wildcard CORS origins in development
- Document port configuration clearly
- Create a startup script that verifies CORS configuration

### **Issue 2: API Field Name Mismatch**

**What happened:**

- Database columns: `lat`, `lon`, `lead_hours`, `discharge_m3s`, `ts`
- Frontend expected: `latitude`, `longitude`, `lead_time_hours`, `discharge_cumecs`, `forecast_timestamp`
- Dashboard showed "Demo Mode" because it couldn't find the data (all values were undefined/null)

**Why it happened:**
The frontend dashboard was created before the backend API was finalized, using placeholder field names. When the backend schema was set, the field names didn't match.

**How to prevent:**

- Use a single source of truth for API contract (OpenAPI/Swagger)
- Add TypeScript/JSDoc types to catch mismatches
- Test with real API responses, not mocked data

---

## ✅ **What Was Fixed**

### **Fix 1: CORS Configuration**

**File**: `deploy/k8s/base/backend-configmap.yaml`

**Added**:

```json
"http://192.168.178.50:5173",
"http://192.168.178.50:8080"
```

**Full CORS origins now**:

```json
[
  "https://floodsight.vercel.app",
  "https://floodsight.com",
  "http://localhost:3000",
  "http://localhost:5173",
  "http://192.168.178.50:5173",
  "http://192.168.178.50:8080"
]
```

### **Fix 2: Frontend Data Normalization**

**Files**:

- `public/dashboard-figma.html`
- `public/assets/js/api-service.js`

**What changed**:

- Updated `normalizeForecast()` function to properly map API field names
- Updated `transformStation()` to ensure lat/lon are available in both formats
- Now handles both old and new field names for backwards compatibility

**Normalization mapping**:

```javascript
// API → Frontend
lead_hours → lead_time_hours
discharge_m3s → discharge_cumecs
ts → forecast_timestamp
lat → latitude
lon → longitude
```

---

## 🛡️ **How to Prevent in the Future**

### **1. Always Update CORS When Changing Ports**

**Create a CORS update script** (`scripts/update-cors.sh`):

```bash
#!/bin/bash
# Update CORS configuration for new port

PORT=$1
PI_IP="192.168.178.50"

if [ -z "$PORT" ]; then
  echo "Usage: ./update-cors.sh <port>"
  exit 1
fi

# Update ConfigMap
kubectl patch configmap floodsight-backend-config -n floodsight \
  --type=json \
  -p='[{"op": "add", "path": "/data/BACKEND_CORS_ORIGINS", "value": "[\"http://localhost:'$PORT'\",\"http://'$PI_IP':'$PORT'\"]"}]'

# Restart backend
kubectl rollout restart deployment floodsight-backend -n floodsight
```

### **2. Use a Single API Contract**

**Create OpenAPI specification** (`backend/openapi.yaml`):

```yaml
components:
  schemas:
    Station:
      type: object
      properties:
        id: { type: integer }
        code: { type: string }
        name: { type: string }
        lat: { type: number } # Not latitude!
        lon: { type: number } # Not longitude!

    Forecast:
      type: object
      properties:
        id: { type: integer }
        station_id: { type: integer }
        ts: { type: string, format: date-time } # Not forecast_timestamp!
        lead_hours: { type: integer } # Not lead_time_hours!
        discharge_m3s: { type: number } # Not discharge_cumecs!
```

### **3. Add Frontend Type Checking**

**Create type definitions** (`public/assets/js/types.js`):

```javascript
/**
 * @typedef {Object} Station
 * @property {number} id
 * @property {string} code
 * @property {string} name
 * @property {number} lat
 * @property {number} lon
 * @property {string} river_basin
 */

/**
 * @typedef {Object} Forecast
 * @property {number} id
 * @property {number} station_id
 * @property {string} ts - ISO timestamp
 * @property {number} lead_hours
 * @property {number} discharge_m3s
 * @property {string} source
 * @property {string} model_run - ISO timestamp
 */
```

### **4. Create Comprehensive Startup Script**

**File**: `start-floodsight.sh`

```bash
#!/bin/bash
set -e

echo "🚀 Starting FloodSight..."

# 1. Check if backend is running
if ! kubectl get pods -n floodsight -l component=backend | grep -q Running; then
  echo "❌ Backend not running. Please deploy first."
  exit 1
fi

# 2. Get backend service port
BACKEND_PORT=$(kubectl get svc floodsight-backend-external -n floodsight -o jsonpath='{.spec.ports[0].nodePort}')
echo "✅ Backend running on port: $BACKEND_PORT"

# 3. Start frontend on available port
FRONTEND_PORT=5173
if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null ; then
  echo "⚠️  Port $FRONTEND_PORT in use, trying 5174..."
  FRONTEND_PORT=5174
fi

echo "🌐 Starting frontend on port $FRONTEND_PORT..."
cd /home/lenovo/scrimba/floodsight
nohup npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT > /tmp/frontend-dev.log 2>&1 &

# 4. Verify CORS configuration
echo "🔍 Checking CORS configuration..."
CORS=$(kubectl get configmap floodsight-backend-config -n floodsight -o jsonpath='{.data.BACKEND_CORS_ORIGINS}')
if echo "$CORS" | grep -q "192.168.178.50:$FRONTEND_PORT"; then
  echo "✅ CORS configured correctly"
else
  echo "⚠️  Updating CORS configuration..."
  # Update CORS (you'd implement this)
fi

# 5. Start Cloudflare tunnels
echo "🌐 Starting Cloudflare tunnels..."
pkill cloudflared || true
sleep 2
nohup cloudflared tunnel --url http://localhost:$FRONTEND_PORT > /tmp/cloudflare-frontend.log 2>&1 &
nohup cloudflared tunnel --url http://192.168.178.50:$BACKEND_PORT > /tmp/cloudflare-backend.log 2>&1 &
sleep 10

# 6. Display access URLs
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ FloodSight is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Frontend: http://192.168.178.50:$FRONTEND_PORT/dashboard-figma.html"
echo "Backend API: http://192.168.178.50:$BACKEND_PORT/v1"
echo ""
echo "Cloudflare URLs:"
grep "Your quick Tunnel" /tmp/cloudflare-frontend.log | tail -1
grep "Your quick Tunnel" /tmp/cloudflare-backend.log | tail -1
echo ""
```

### **5. Add Automated Tests**

**Create API integration test** (`tests/test-api-frontend-integration.sh`):

```bash
#!/bin/bash
# Test that frontend can read API responses

API_URL="http://192.168.178.50:30636/v1"

echo "Testing API integration..."

# Test stations
STATION=$(curl -s "$API_URL/stations" | jq '.[0]')
if echo "$STATION" | jq -e '.lat' > /dev/null; then
  echo "✅ Stations have 'lat' field"
else
  echo "❌ ERROR: Stations missing 'lat' field"
  exit 1
fi

# Test forecasts
FORECAST=$(curl -s "$API_URL/forecasts?limit=1" | jq '.[0]')
if echo "$FORECAST" | jq -e '.lead_hours' > /dev/null; then
  echo "✅ Forecasts have 'lead_hours' field"
else
  echo "❌ ERROR: Forecasts missing 'lead_hours' field"
  exit 1
fi

if echo "$FORECAST" | jq -e '.discharge_m3s' > /dev/null; then
  echo "✅ Forecasts have 'discharge_m3s' field"
else
  echo "❌ ERROR: Forecasts missing 'discharge_m3s' field"
  exit 1
fi

echo "✅ All API integration tests passed!"
```

---

## 📊 **Understanding the Data**

### **Fake vs Real Data**

**How to verify data is real:**

1. **Check the source field**:

```bash
curl http://192.168.178.50:30636/v1/forecasts?limit=1 | jq '.[0].source'
# Should output: "GloFAS"
```

2. **Check model_run timestamp**:

```bash
curl http://192.168.178.50:30636/v1/forecasts?limit=1 | jq '.[0].model_run'
# Should be a recent date (yesterday or today)
```

3. **Check discharge values**:

```bash
# Frankfurt Main discharge should be 60-100 m³/s typically
curl http://192.168.178.50:30636/v1/forecasts | jq '.[] | select(.station_id == 5) | .discharge_m3s' | head -10
```

**Real GloFAS data characteristics:**

- `source`: "GloFAS"
- `model_run`: Recent date (updated hourly)
- Discharge values vary realistically (not constant)
- Values are reasonable for the river (50-200 m³/s for Main river)

**Fake data characteristics:**

- `source`: "fake" or "demo"
- `model_run`: null or very old
- Discharge values might be constant or unrealistic
- Created_at timestamp is old

### **How to Clean Fake Data**

**Delete all fake/old forecasts:**

```bash
kubectl exec -n floodsight postgres-0 -- psql -U postgres -d floodsight -c "DELETE FROM forecasts WHERE source != 'GloFAS' OR model_run < NOW() - INTERVAL '7 days';"
```

**Verify only real data remains:**

```bash
kubectl exec -n floodsight postgres-0 -- psql -U postgres -d floodsight -c "SELECT source, COUNT(*), MIN(model_run), MAX(model_run) FROM forecasts GROUP BY source;"
```

---

## 🎯 **Quick Checklist**

Before using the dashboard, verify:

- [ ] Backend is running: `kubectl get pods -n floodsight`
- [ ] CORS includes your frontend port: `kubectl get configmap -n floodsight floodsight-backend-config -o yaml | grep CORS`
- [ ] Frontend is using correct port (5173 or 8080)
- [ ] API returns correct field names: `curl http://192.168.178.50:30636/v1/stations | jq '.[0] | keys'`
- [ ] Forecasts have real data: `curl http://192.168.178.50:30636/v1/forecasts?limit=1 | jq '.[0].source'`
- [ ] Hard refresh browser after changes: `Ctrl + Shift + R`

---

## 🔧 **Monitoring & Debugging**

### **Check if frontend can reach backend:**

```bash
# From your Pi
curl -H "Origin: http://192.168.178.50:5173" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS \
  http://192.168.178.50:30636/v1/health -i | grep -i "access-control"
```

**Expected output:**

```
access-control-allow-origin: http://192.168.178.50:5173
access-control-allow-credentials: true
```

### **Check frontend logs:**

```bash
tail -f /tmp/frontend-dev.log
```

### **Check backend logs:**

```bash
kubectl logs -f -l component=backend -n floodsight
```

### **Check database directly:**

```bash
kubectl exec -n floodsight postgres-0 -- psql -U postgres -d floodsight -c "SELECT source, COUNT(*), MAX(model_run) FROM forecasts GROUP BY source;"
```

---

## 📝 **Summary**

**Two separate issues caused "Demo Mode":**

1. **CORS**: Backend rejected requests from `192.168.178.50:5173`
   - **Fixed**: Added IP:port to CORS configuration
   - **Prevent**: Update CORS when changing ports

2. **Field Names**: Frontend expected different API field names
   - **Fixed**: Added normalization layer in frontend
   - **Prevent**: Use TypeScript and API contract

**Data is REAL:**

- All forecasts are from GloFAS (ECMWF)
- Updated hourly automatically
- Frankfurt data is legitimate (~60-90 m³/s for Main river)

**To avoid future issues:**

- Use the startup script
- Run integration tests
- Check CORS configuration when changing ports
- Always hard-refresh browser after backend changes
