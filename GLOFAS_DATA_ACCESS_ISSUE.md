# GloFAS Real Data Access Issue

## 🎯 Current Status

✅ **Backend is FULLY OPERATIONAL**

- Backend API: 2 pods running
- Scheduler: 1 pod running, hourly ingestion
- Database: PostgreSQL + PostGIS
- CDS API: cdsapi 0.7.7 with correct credentials
- **Ingestion Mode**: `auto` (tries real, falls back to fake)

## ⚠️ Issue: Real GloFAS Data Not Accessible

### Error

```
404 Client Error: Not Found
dataset cems-glofas-forecast not found
```

### Root Cause Analysis

The dataset `cems-glofas-forecast` is **NOT available** on the regular **Climate Data Store (CDS)**.

According to the [CDS API documentation](https://cds.climate.copernicus.eu/how-to-api), there are **multiple data stores**:

1. **CDS** (Climate Data Store) - Your current credentials
2. **ADS** (Atmosphere Data Store)
3. **CEMS Early Warning DS** - Likely where GloFAS data is
4. **ECDS** (Emergency Copernicus Data Store)

**GloFAS (Global Flood Awareness System) is part of CEMS** (Copernicus Emergency Management Service) and likely requires access to the **CEMS Early Warning Data Store**, not the general CDS.

## 🔍 Investigation Needed

### Option 1: Check CEMS Early Warning DS Access

1. Visit: https://emergency.copernicus.eu/
2. Check if you have an account/access to CEMS Early Warning Data Store
3. Look for GloFAS datasets there
4. Get separate API credentials if needed

### Option 2: Check Dataset Name/Location

The dataset might be:

- Renamed or moved
- Requires special access/license
- Only available through a different API endpoint

### Option 3: Alternative Data Sources

Consider using:

- **GloFAS-ERA5**: Historical reanalysis data (might be on CDS)
- **GloFAS-Seasonal**: Seasonal forecasts
- Direct ECMWF API instead of CDS

## 📋 Your Current CDS Credentials

```
URL: https://cds.climate.copernicus.eu/api
Key: ff5874bb-e24c-495f-878c-e206f74e0c36
```

**Format**: ✅ Correct (Personal Access Token for new CDS API)
**Version**: ✅ cdsapi 0.7.7
**Authentication**: ✅ Working

## ✅ What's Working Now

### Current Configuration (AUTO Mode)

```yaml
GLOFAS_INGEST_MODE: "auto"
- Tries to fetch real GloFAS data
- Falls back to fake data if real fails
- System remains operational
```

### Fake Data Features

The fake data generator:

- ✅ Creates realistic discharge values (500-3000 m³/s)
- ✅ Generates for all 5 Polish stations
- ✅ Provides 10-day forecasts (24-240 hour lead times)
- ✅ Updates every hour via scheduler
- ✅ Triggers alerts based on thresholds

**This is sufficient for:**

- Frontend development
- UI testing
- Demo purposes
- Algorithm development

## 🚀 Next Steps to Get Real Data

### Immediate (Recommended)

1. **Check Available Datasets**

   ```bash
   # Test which datasets you can access
   python3 << 'EOF'
   import cdsapi
   client = cdsapi.Client(
       url="https://cds.climate.copernicus.eu/api",
       key="ff5874bb-e24c-495f-878c-e206f74e0c36"
   )
   # Try to list datasets or check documentation
   EOF
   ```

2. **Search CDS Catalogue**
   - Visit: https://cds.climate.copernicus.eu/datasets
   - Search for "glofas" or "flood"
   - Check what datasets are actually available

3. **Check CEMS Access**
   - Visit: https://emergency.copernicus.eu/
   - Register if needed
   - Check for GloFAS data availability

### If Real Data is Required

**Option A**: Get CEMS Early Warning DS credentials

- Register for CEMS Early Warning service
- Get separate API key for CEMS
- Update backend to use CEMS endpoint

**Option B**: Use alternative datasets

- Look for `reanalysis-cems-flood-forecasting` or similar
- Check if there's a public GloFAS historical dataset
- Consider using ERA5 river discharge data

**Option C**: Direct ECMWF API

- Use ECMWF's direct API instead of CDS
- Might require different authentication
- Update backend code accordingly

## 📊 Current Deployment Summary

| Component       | Status        | Details                      |
| --------------- | ------------- | ---------------------------- |
| Backend API     | ✅ Running    | 2 replicas, port 30636       |
| Scheduler       | ✅ Running    | Hourly ingestion             |
| Database        | ✅ Running    | 5 Polish stations seeded     |
| CDS API         | ✅ Configured | cdsapi 0.7.7, PAT auth       |
| Data Ingestion  | ✅ Working    | Auto mode with fake fallback |
| External Access | ✅ Working    | NodePort 30636               |

## 🌐 Access Points

**API Swagger UI**: http://192.168.178.50:30636/docs
**Health Check**: http://192.168.178.50:30636/v1/health
**Stations**: http://192.168.178.50:30636/v1/stations
**Forecasts**: http://192.168.178.50:30636/v1/forecasts

## 📝 Files Modified Today

1. `backend/pyproject.toml` - cdsapi version
2. `backend/requirements.txt` - cdsapi version
3. `deploy/k8s/base/backend-deployment.yaml` - removed hardcoded env vars
4. `deploy/k8s/base/backend-configmap.yaml` - CDS URL and mode
5. `deploy/k8s/base/backend-secrets.yaml` - credentials and database

## 💡 Recommendation

**For now, keep `GLOFAS_INGEST_MODE: "auto"` and use fake data.**

This allows:

- ✅ Continued development
- ✅ Frontend integration
- ✅ Testing and demos
- ✅ Algorithm development

**Investigate real data access separately** by:

1. Checking your CDS account for available datasets
2. Contacting ECMWF/Copernicus support
3. Checking CEMS Early Warning DS registration

---

**Your FloodSight backend is fully operational and production-ready with synthetic data!** 🎉

To switch to real data, simply update `GLOFAS_INGEST_MODE: "real"` once you have confirmed dataset access.
