# 🌍 GloFAS Real Data Integration Guide

This guide explains how to integrate real ECMWF GloFAS (Global Flood Awareness System) forecast data into FloodSight.

---

## 📋 What is GloFAS?

**GloFAS (Global Flood Awareness System)** provides:

- Global river discharge forecasts
- Up to 30-day lead time
- 0.1° resolution (~11km at equator)
- Updated daily (00:00 UTC)
- Ensemble forecasts (51 members)
- Historical data since 1984

**Data Source:** ECMWF Copernicus Climate Data Store (CDS)

---

## 🔑 Step 1: Register for CDS API Access

### 1.1 Create CDS Account

1. Go to https://cds.climate.copernicus.eu/
2. Click "Register" (top right)
3. Fill in your details
4. Verify your email address
5. Accept the Terms & Conditions

### 1.2 Get API Credentials

1. Log in to CDS
2. Go to your profile: https://cds.climate.copernicus.eu/user
3. Scroll down to "API key" section
4. Copy your UID and API key

**Format:**

```
UID: 12345
API Key: abcd1234-ef56-7890-ghij-klmnopqrstuv
```

### 1.3 Accept GloFAS License

**IMPORTANT:** You must accept the data license before you can download GloFAS data.

1. Go to: https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-glofas-forecast
2. Scroll down to "Terms of use"
3. Click "Accept terms"
4. You should see "You have accepted the licence to use this dataset"

---

## ⚙️ Step 2: Configure FloodSight Backend

### 2.1 Local Development (Docker Compose)

Edit `backend/docker-compose.yml`:

```yaml
services:
  api:
    environment:
      # ... existing vars ...

      # GloFAS Configuration
      - GLOFAS_INGEST_MODE=auto # or 'real' to require real data
      - CDS_API_URL=https://cds.climate.copernicus.eu/api/v2
      - CDS_API_KEY=12345:abcd1234-ef56-7890-ghij-klmnopqrstuv

      # GloFAS Data Selection
      - GLOFAS_SYSTEM_VERSION=version_4_0
      - GLOFAS_HYDROLOGICAL_MODEL=lisflood
      - GLOFAS_VARIABLE=river_discharge_in_the_last_24_hours
```

**CDS_API_KEY Format:** `{UID}:{API_KEY}`

### 2.2 Kubernetes Deployment

Update `deploy/k8s/base/backend-secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: floodsight-backend-secrets
  namespace: floodsight
type: Opaque
stringData:
  # ... other secrets ...

  # ECMWF CDS API credentials
  cds-api-key: '12345:abcd1234-ef56-7890-ghij-klmnopqrstuv'
  cds-api-url: 'https://cds.climate.copernicus.eu/api/v2'
```

Apply the secrets:

```bash
kubectl apply -f deploy/k8s/base/backend-secrets.yaml
```

Restart the backend:

```bash
kubectl rollout restart deployment/floodsight-backend -n floodsight
kubectl rollout restart deployment/floodsight-scheduler -n floodsight
```

---

## 🧪 Step 3: Test Real Data Ingestion

### 3.1 Manual Trigger (API Endpoint)

```bash
# Trigger real data ingestion
curl -X POST http://localhost:8080/v1/forecasts/ingest

# Or for production
curl -X POST https://api.floodsight.com/v1/forecasts/ingest
```

**Expected Response:**

```json
{
  "status": "success",
  "message": "Ingested 120 forecasts (real)",
  "forecasts_created": 120,
  "mode": "real"
}
```

**Modes:**

- `real` - Successfully downloaded from ECMWF CDS
- `fake` - Fell back to synthetic data (if `GLOFAS_INGEST_MODE=auto`)

### 3.2 Manual Trigger (Command Line)

```bash
# Docker Compose
docker compose exec api python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.services.glefas import ingest_forecasts

async def main():
    async with AsyncSessionLocal() as db:
        count, mode = await ingest_forecasts(db)
        print(f'Ingested {count} forecasts (mode: {mode})')

asyncio.run(main())
"

# Kubernetes
kubectl exec -it deployment/floodsight-backend -n floodsight -- python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.services.glefas import ingest_forecasts

async def main():
    async with AsyncSessionLocal() as db:
        count, mode = await ingest_forecasts(db)
        print(f'Ingested {count} forecasts (mode: {mode})')

asyncio.run(main())
"
```

### 3.3 Check Logs

```bash
# Docker Compose
docker compose logs -f api

# Kubernetes
kubectl logs -f -l component=backend -n floodsight
```

**Look for:**

```
INFO: 🌍 Attempting real GloFAS ingestion via ECMWF CDS...
INFO: ✅ CDS API credentials configured
INFO: 📡 Fetching GloFAS data for 10 stations...
INFO: ⬇️  Downloading GRIB data from CDS...
INFO: 📊 Processing forecast data...
INFO: ✅ Successfully ingested 120 forecasts from real GloFAS data
```

---

## 🔍 Step 4: Verify Real Data

### 4.1 Check Forecast Data

```bash
# Get recent forecasts
curl http://localhost:8080/v1/forecasts?limit=10

# Check data source
curl http://localhost:8080/v1/forecasts | jq '.[] | {station_id, source, discharge_m3s}'
```

**Real data should have:**

- `source: "GloFAS"`
- `model_run: "2025-11-13T00:00:00Z"` (recent timestamp)
- Realistic discharge values based on actual river conditions

### 4.2 Compare with Fake Data

**Fake data characteristics:**

- Random values between 500-2500 m³/s
- Uniform distribution
- No correlation with actual weather/hydrology

**Real data characteristics:**

- Based on numerical weather prediction (NWP)
- Reflects actual hydrological conditions
- May show trends (rising/falling discharge)
- Varies by station and river basin

### 4.3 Check Data Coverage

```bash
# Get stations with recent forecasts
curl http://localhost:8080/v1/stations | jq '.[] | select(.forecasts | length > 0)'

# Count forecasts per station
curl http://localhost:8080/v1/forecasts | jq 'group_by(.station_id) | map({station: .[0].station_id, count: length})'
```

---

## 🤖 Step 5: Automated Ingestion

### 5.1 Scheduler Configuration

The scheduler automatically runs ingestion every hour (configurable).

**Check scheduler status:**

```bash
# Docker Compose
docker compose logs -f scheduler

# Kubernetes
kubectl logs -f -l component=scheduler -n floodsight
```

**Expected logs:**

```
🌊 FloodSight Scheduler Starting
📅 Schedule: 0 * * * * (hourly at :00)
⚙️  Environment: production
🗄️  Database: configured
Press Ctrl+C to stop the scheduler
▶️  Running initial ingestion job...
🌍 Attempting real GloFAS ingestion via ECMWF CDS...
✅ Ingested 120 forecasts (mode=real)
```

### 5.2 Customize Schedule

Edit `backend/app/workers/flows.py`:

```python
# Default: Every hour at the top of the hour
schedule = "0 * * * *"

# Examples:
# Every 3 hours: "0 */3 * * *"
# Every 6 hours: "0 */6 * * *"
# Daily at 00:00 UTC: "0 0 * * *"
# Twice daily (00:00 and 12:00): "0 0,12 * * *"
```

Or use environment variable:

```yaml
- SCHEDULER_CRON=0 */3 * * * # Every 3 hours
```

---

## ⚠️ Troubleshooting

### Issue 1: "CDS API credentials not configured"

**Error:**

```
ERROR: CDS API credentials not configured
```

**Solution:**

- Verify `CDS_API_KEY` environment variable is set
- Format: `{UID}:{API_KEY}` (no spaces)
- Check if secret is properly mounted in K8s

### Issue 2: "CDS API request failed"

**Error:**

```
ERROR: CDS API request failed: {'error': {'code': 401, 'message': 'Invalid API key'}}
```

**Solutions:**

1. **Invalid credentials**
   - Verify UID and API key are correct
   - Check for extra spaces or quotes
   - Regenerate API key if needed

2. **License not accepted**
   - Go to: https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-glofas-forecast
   - Click "Accept terms" (scroll down)

3. **CDS service down**
   - Check status: https://cds.climate.copernicus.eu/live/status
   - Wait and retry later

### Issue 3: "Timeout downloading GRIB data"

**Error:**

```
ERROR: Timeout waiting for CDS data retrieval
```

**Solutions:**

- CDS requests can take 5-15 minutes for large queries
- The queue may be long during peak hours
- Reduce the number of stations or time range
- Try again during off-peak hours (night time in Europe)

### Issue 4: "No stations configured"

**Error:**

```
WARNING: No stations found for GloFAS ingestion
```

**Solution:**

```bash
# Seed sample stations
docker compose exec api python -m app.services.seed

# Or in K8s
kubectl exec deployment/floodsight-backend -n floodsight -- python -m app.services.seed
```

### Issue 5: Falling back to fake data

**Log:**

```
WARNING: Real GloFAS ingestion failed, falling back to fake data
```

**When this happens:**

- `GLOFAS_INGEST_MODE=auto` (default) allows fallback
- Check logs for the actual error
- Set `GLOFAS_INGEST_MODE=real` to require real data (will error instead of falling back)

---

## 📊 GloFAS Data Parameters

### Available Variables

```python
GLOFAS_VARIABLE options:
- "river_discharge_in_the_last_24_hours"  # Default, best for forecasting
- "river_discharge"                        # Instantaneous discharge
- "river_volume"                           # River volume
```

### System Versions

```python
GLOFAS_SYSTEM_VERSION options:
- "version_4_0"  # Current version (recommended)
- "version_3_1"  # Legacy version
```

### Hydrological Models

```python
GLOFAS_HYDROLOGICAL_MODEL options:
- "lisflood"  # Default, used by GloFAS operational system
- "htessel"   # Alternative model
```

### Forecast Lead Times

GloFAS provides forecasts for:

- Lead times: 0 to 720 hours (0-30 days)
- Temporal resolution: 24 hours
- Ensemble members: 51 (1 control + 50 perturbed)

FloodSight currently uses:

- Lead times: 24, 48, 72 hours (configurable in code)
- Ensemble: Control run (ensemble member 0)

---

## 🎯 Advanced Configuration

### Configure Stations for GloFAS

Edit `backend/app/services/seed.py` to add your stations:

```python
stations = [
    {
        "code": "ELBE-DRESDEN",
        "name": "Dresden (Elbe)",
        "lat": 51.0504,
        "lon": 13.7373,
        "river_basin": "Elbe",
    },
    # Add your stations here
]
```

**Important:** Use coordinates that match river locations in GloFAS grid (0.1° resolution).

### Customize Ingestion Frequency

Modify `backend/app/workers/flows.py`:

```python
# Run every 6 hours (matches GloFAS update frequency)
schedule = "0 */6 * * *"

# Or run at specific times (e.g., 00:00, 06:00, 12:00, 18:00 UTC)
scheduler.add_job(
    floodsight_ingest_flow,
    trigger=CronTrigger(hour='0,6,12,18', minute='0'),
    # ... other settings ...
)
```

### Adjust Forecast Lead Times

Edit `backend/app/services/glefas.py`:

```python
# Default: 24h, 48h, 72h
FORECAST_LEAD_TIMES = [24, 48, 72]

# Extended: Include longer lead times
FORECAST_LEAD_TIMES = [24, 48, 72, 96, 120, 144, 168]  # Up to 7 days
```

---

## 📈 Monitoring Real Data Ingestion

### Key Metrics to Monitor

1. **Ingestion Success Rate**

   ```bash
   # Check recent ingestions
   kubectl logs -l component=scheduler -n floodsight | grep "Ingested"
   ```

2. **Data Freshness**

   ```bash
   # Check latest forecast timestamp
   curl http://localhost:8080/v1/forecasts?limit=1 | jq '.[0].model_run'
   ```

3. **CDS API Performance**
   - Monitor request times in logs
   - Track timeout rates
   - Watch for quota limits

4. **Data Quality**
   - Compare discharge values with historical data
   - Check for missing stations
   - Verify forecast lead time coverage

### Grafana Dashboard (if configured)

Add panels for:

- Real vs fake data ratio
- CDS API response times
- Ingestion error rate
- Data coverage by station
- Forecast freshness

---

## 🔐 Security Best Practices

1. **Protect API Credentials**
   - Never commit API keys to git
   - Use K8s secrets or environment variables
   - Rotate keys periodically

2. **Rate Limiting**
   - CDS has request limits per user
   - Don't query too frequently (hourly is sufficient)
   - Respect the CDS fair use policy

3. **Data Licensing**
   - GloFAS data is free for non-commercial use
   - Commercial use requires separate agreement
   - Always cite ECMWF as data source

---

## 📚 Additional Resources

- **GloFAS Dataset:** https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-glofas-forecast
- **CDS API Documentation:** https://cds.climate.copernicus.eu/api-how-to
- **GloFAS Technical Documentation:** https://www.globalfloods.eu/
- **ECMWF Support:** https://confluence.ecmwf.int/

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs** for detailed error messages
2. **Verify credentials** are correct
3. **Check CDS status** page
4. **Review GloFAS documentation**
5. **Open GitHub issue** with error details

---

## ✅ Integration Checklist

- [ ] CDS account created
- [ ] API credentials obtained
- [ ] GloFAS license accepted
- [ ] Backend configured with CDS_API_KEY
- [ ] Test ingestion successful
- [ ] Real data verified
- [ ] Scheduler running
- [ ] Monitoring configured
- [ ] Error alerting set up

---

**🌍 You're now ingesting real global flood forecast data! 🎉**
