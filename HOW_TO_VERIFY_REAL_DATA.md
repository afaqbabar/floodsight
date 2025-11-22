# How to Verify Your Data is Real (Not Fake)

This guide shows you **5 ways** to verify whether FloodSight is using **real GloFAS data** from ECMWF Copernicus or **synthetic test data**.

---

## 🚀 Quick Verification (Run This First!)

```bash
cd /home/lenovo/scrimba/floodsight
./verify-data.sh
```

This script checks everything automatically. Look for:

- ✅ **`source: GloFAS`** = REAL data
- ❌ **`source: GloFAS-fake`** = Synthetic data

---

## Method 1: Check the Database (Fastest)

### Query the forecasts table directly:

```bash
cd /home/lenovo/scrimba/floodsight/backend

# Check what data sources are in the database
docker compose exec db psql -U floodsight -d floodsight -c \
  "SELECT source, COUNT(*) as count FROM forecasts GROUP BY source;"
```

**Expected output:**

**✅ REAL DATA:**

```
   source   | count
------------+-------
 GloFAS     |   360
```

**❌ FAKE DATA:**

```
   source      | count
---------------+-------
 GloFAS-fake   |    60
```

---

## Method 2: Check Backend Logs

### Look for ingestion messages:

```bash
cd /home/lenovo/scrimba/floodsight/backend

# Check recent ingestion logs
docker compose logs api | grep -i "forecast ingestion" | tail -n 20
```

**✅ REAL DATA logs:**

```
Starting real GloFAS forecast ingestion...
Requesting GloFAS forecast: {'system_version': 'operational', ...}
Ingested 360 GloFAS forecasts across 5 stations (model run 2025-11-12T00:00:00+00:00)
```

**❌ FAKE DATA logs:**

```
Starting fake forecast ingestion...
Ingested 60 fake forecasts for 5 stations
```

---

## Method 3: Check via API

### Use curl to check forecast metadata:

```bash
# Get a recent forecast
curl -s http://localhost:8080/v1/forecasts?limit=1 | jq '.[0].source'

# Expected output for REAL data:
"GloFAS"

# Expected output for FAKE data:
"GloFAS-fake"
```

### Check all sources:

```bash
curl -s http://localhost:8080/v1/forecasts | jq '[.[].source] | unique'

# REAL data: ["GloFAS"]
# FAKE data: ["GloFAS-fake"]
```

---

## Method 4: Check Configuration

### Verify CDS API credentials are set:

```bash
cd /home/lenovo/scrimba/floodsight/backend

# Check docker-compose.yml for CDS_API_KEY
grep CDS_API_KEY docker-compose.yml
```

**Should see:**

```yaml
- CDS_API_KEY=ff5874bb-e24c-495f-878c-e206f74e0c36
```

**If it shows an empty value, you're using fake data!**

### Check ingestion mode:

```bash
grep GLOFAS_INGEST_MODE docker-compose.yml
```

**Options:**

- `auto` = Try real, fallback to fake if fails
- `real` = Only real (fail if unavailable)
- `fake` = Always synthetic

---

## Method 5: Analyze Data Patterns

Real GloFAS data has different characteristics than synthetic data:

### Run the Python analysis script:

```bash
cd /home/lenovo/scrimba/floodsight/backend
docker compose exec api python /app/verify_data_source.py
```

**This checks:**

1. **Source field** in database
2. **Model run timestamp** (real data is recent)
3. **Discharge patterns** (real = smooth, fake = random/jumpy)
4. **Data coverage** (real data may have gaps, fake is perfect)

### Key differences:

| Characteristic       | Real GloFAS Data         | Fake Synthetic Data             |
| -------------------- | ------------------------ | ------------------------------- |
| **Source field**     | `GloFAS`                 | `GloFAS-fake`                   |
| **Model run**        | Recent (< 24h old)       | May be outdated                 |
| **Discharge values** | Realistic (50-2000 m³/s) | Wide range (100-2500 m³/s)      |
| **Temporal pattern** | Smooth progression       | Random jumps                    |
| **Lead times**       | Various (6h-240h)        | Fixed intervals (6,12,18...72h) |
| **Data gaps**        | Possible                 | No gaps (perfect)               |
| **Value precision**  | NetCDF precision         | Rounded to 2 decimals           |

---

## 🔍 Deep Dive: Check a Specific Forecast

```bash
cd /home/lenovo/scrimba/floodsight/backend

# Get full details of most recent forecast
docker compose exec db psql -U floodsight -d floodsight -c \
  "SELECT
     f.id,
     f.source,
     f.model_run,
     f.ts as forecast_time,
     f.lead_hours,
     f.discharge_m3s,
     s.code as station,
     f.created_at
   FROM forecasts f
   JOIN stations s ON f.station_id = s.id
   ORDER BY f.created_at DESC
   LIMIT 10;" -x
```

**Look for:**

✅ **Real data indicators:**

- `source` = `GloFAS` (no "-fake" suffix)
- `model_run` timestamp within last 24 hours
- `discharge_m3s` values are realistic for the river
- Multiple lead times (not just 6-hour intervals)

❌ **Fake data indicators:**

- `source` = `GloFAS-fake`
- `model_run` timestamp may be old
- `discharge_m3s` values seem too variable
- Perfect 6-hour intervals only

---

## 🐛 Troubleshooting: If You're Getting Fake Data

### 1. Check CDS API Key is Valid

```bash
# Test your CDS API key directly
curl -s "https://ewds.climate.copernicus.eu/api/resources/cems-glofas-forecast" \
  -H "PRIVATE-TOKEN: ff5874bb-e24c-495f-878c-e206f74e0c36"
```

If this returns HTML or an error, your API key may be invalid.

### 2. Check Backend Logs for Errors

```bash
docker compose logs api | grep -i "error\|failed\|credentials"
```

**Common issues:**

- `GloFAS credentials missing` = API key not configured
- `GloFAS ingestion failed` = CDS service unavailable
- `Unable to locate discharge variable` = Wrong dataset parameters

### 3. Force Real Data Ingestion

```bash
# Manually trigger ingestion (should try real first)
curl -X POST http://localhost:8080/v1/forecasts/ingest

# Check logs immediately after
docker compose logs api | tail -n 30
```

### 4. Check Environment Variables

```bash
# See what the API container actually has
docker compose exec api env | grep -E "CDS|GLOFAS"
```

Should show:

```
GLOFAS_INGEST_MODE=auto
CDS_API_URL=https://ewds.climate.copernicus.eu/api
CDS_API_KEY=ff5874bb-e24c-495f-878c-e206f74e0c36
```

---

## ✅ Verification Checklist

Use this checklist to confirm you have real data:

- [ ] Database shows `source = GloFAS` (not `GloFAS-fake`)
- [ ] Backend logs show "Starting real GloFAS forecast ingestion"
- [ ] CDS_API_KEY is configured in docker-compose.yml
- [ ] Model run timestamp is recent (< 24 hours old)
- [ ] API returns `"source": "GloFAS"` in forecasts
- [ ] Discharge values show smooth temporal progression
- [ ] No error messages in logs about missing credentials

**If all checked ✅ = You have REAL DATA! 🎉**

---

## 📊 Compare Real vs Fake Data Side-by-Side

### Real GloFAS Data Example:

```json
{
  "id": 1234,
  "station_id": 1,
  "source": "GloFAS",
  "model_run": "2025-11-12T00:00:00+00:00",
  "ts": "2025-11-12T18:00:00+00:00",
  "lead_hours": 18,
  "discharge_m3s": 847.32,
  "created_at": "2025-11-12T02:15:33+00:00"
}
```

### Fake Synthetic Data Example:

```json
{
  "id": 42,
  "station_id": 1,
  "source": "GloFAS-fake",
  "model_run": "2025-11-12T00:00:00+00:00",
  "ts": "2025-11-12T18:00:00+00:00",
  "lead_hours": 18,
  "discharge_m3s": 1247.83,
  "created_at": "2025-11-12T02:05:12+00:00"
}
```

**Key difference: the `source` field!**

---

## 🎯 Quick Answer

**Want to know RIGHT NOW?**

```bash
curl -s http://localhost:8080/v1/forecasts?limit=1 | jq '.[0].source'
```

- Output `"GloFAS"` = ✅ **REAL DATA**
- Output `"GloFAS-fake"` = ❌ **FAKE DATA**

That's it! 🎉

---

## 📚 Related Documentation

- `backend/README.md` - Backend setup and GloFAS configuration
- `PRODUCTION_STATUS.md` - Current deployment status
- `backend/app/services/glefas.py` - Ingestion logic source code

---

**Questions?** Check the logs:

```bash
docker compose logs api | grep -i glofas | tail -n 50
```
