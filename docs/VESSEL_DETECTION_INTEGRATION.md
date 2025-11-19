# Vessel Detection - Drop-In Integration Guide

## 🎯 Exact Integration Point

Insert this code **immediately after your speckle-filtering step** in your existing Sentinel-1 processing pipeline.

---

## 📍 Where to Insert (15-25 Lines)

```python
# YOUR EXISTING SENTINEL-1 FLOW
# ================================

# Step 1: Download Sentinel-1 scene from Copernicus
sentinel1_data = download_sentinel1_scene(scene_id)

# Step 2: Radiometric calibration
sigma0_vv = calibrate_to_sigma0(sentinel1_data)

# Step 3: Speckle filtering (your existing step)
sigma0_vv_filtered = apply_speckle_filter(sigma0_vv)  # Lee filter, etc.

# Step 4: Flood-water classification (your existing CNN)
water_mask = your_flood_cnn.predict(sigma0_vv_filtered)

# ========================================
# INSERT VESSEL DETECTION HERE (15 LINES)
# ========================================

from app.services.sentinel1 import process_sentinel1_scene
from app.db.session import AsyncSessionLocal

# Add vessel detection (reuses the same filtered data)
async with AsyncSessionLocal() as db:
    vessel_count = await process_sentinel1_scene(
        db=db,
        scene_id=scene_id,
        sigma0_vv_filtered=sigma0_vv_filtered,  # Your existing output
        geotransform=geotransform,              # Your GDAL geotransform
        scene_timestamp=scene_timestamp,        # Scene acquisition time
        detector_type="cfar",
        threshold_db=12.0  # Coastal: 12 dB, River: 10 dB, Port: 15 dB
    )
    logger.info(f"Detected {vessel_count} vessels in {scene_id}")

# ========================================
# END VESSEL DETECTION
# ========================================

# Step 5: Store flood mask (your existing step)
store_flood_mask(water_mask, scene_id)
```

---

## 🔧 What You Need to Provide

| Parameter            | Your Variable            | Notes                                               |
| -------------------- | ------------------------ | --------------------------------------------------- |
| `scene_id`           | Your scene identifier    | e.g., `"S1A_IW_GRDH_1SDV_20251119T..."`             |
| `sigma0_vv_filtered` | Output of speckle filter | 2D numpy array in dB                                |
| `geotransform`       | GDAL geotransform tuple  | `(originX, pixelWidth, 0, originY, 0, pixelHeight)` |
| `scene_timestamp`    | Scene acquisition time   | `datetime` object with timezone                     |

---

## 🧪 Example with GDAL

If you're using GDAL to read Sentinel-1 GeoTIFFs:

```python
from osgeo import gdal
import numpy as np

# Open Sentinel-1 GeoTIFF
dataset = gdal.Open("S1A_IW_GRDH_VV_20251119.tif")
band = dataset.GetRasterBand(1)

# Read data
sigma0_vv_db = band.ReadAsArray()

# Get geotransform
geotransform = dataset.GetGeoTransform()
# Returns: (originX, pixelWidth, 0, originY, 0, pixelHeight)

# Parse timestamp from filename
from datetime import datetime, timezone
scene_timestamp = datetime(2025, 11, 19, 12, 0, 0, tzinfo=timezone.utc)

# Apply speckle filter (your code)
sigma0_vv_filtered = your_speckle_filter(sigma0_vv_db)

# Add vessel detection
vessel_count = await process_sentinel1_scene(
    db=db,
    scene_id="S1A_IW_GRDH_VV_20251119",
    sigma0_vv_filtered=sigma0_vv_filtered,
    geotransform=geotransform,
    scene_timestamp=scene_timestamp,
)
```

---

## 🎛️ Detector Tuning

### Threshold Selection

```python
# Coastal / open water (default)
threshold_db=12.0

# Calm rivers (more sensitive)
threshold_db=10.0

# High-traffic ports (reduce false alarms)
threshold_db=15.0

# Rough seas / high wind
threshold_db=14.0
```

### Window Size (Advanced)

Modify in `app/services/sentinel1.py`:

```python
vessel_mask = detect_vessels_cfar(
    sigma0_vv_filtered,
    threshold_db=12.0,
    window_size=40,   # Default: 40 pixels
    guard_size=10,    # Default: 10 pixels
)
```

- **Smaller window (20-30)**: Better for small vessels, more false alarms
- **Larger window (50-60)**: Better for large ships, may miss small boats

---

## 🔍 Verification

### 1. Check Database

```sql
-- Count detections by scene
SELECT scene_id, COUNT(*) as vessel_count
FROM vessel_detections
GROUP BY scene_id
ORDER BY vessel_count DESC;

-- Recent detections
SELECT id, scene_id, detection_time, confidence,
       ST_X(geom) as lon, ST_Y(geom) as lat
FROM vessel_detections
ORDER BY detection_time DESC
LIMIT 10;
```

### 2. Query via API

```bash
# List all vessels
curl http://localhost:8080/v1/vessels | jq

# Filter by scene
curl "http://localhost:8080/v1/vessels?scene_id=S1A_IW_GRDH_..." | jq

# High-confidence only
curl "http://localhost:8080/v1/vessels?min_confidence=0.8" | jq

# GeoJSON for map
curl http://localhost:8080/v1/vessels/geojson | jq
```

### 3. Visualize on Map

```python
import folium

# Fetch vessels as GeoJSON
response = requests.get("http://localhost:8080/v1/vessels/geojson")
vessels_geojson = response.json()

# Create map
m = folium.Map(location=[50.0, 8.0], zoom_start=8)
folium.GeoJson(vessels_geojson).add_to(m)
m.save("vessels_map.html")
```

---

## ⚙️ Automatic Scheduling

Vessel detection runs automatically every hour via the scheduler:

```python
# backend/app/workers/flows.py
async def run_complete_flow():
    forecast_count = await fetch_and_store_forecasts()  # GloFAS
    alerts_count = await compute_and_store_alerts()     # Flood alerts
    vessel_count = await process_sentinel1_vessels()    # Vessels (NEW)
    return forecast_count, alerts_count, vessel_count
```

To enable:

```bash
docker compose up scheduler
```

---

## 🐛 Troubleshooting

### No vessels detected

**Possible causes:**

1. **Threshold too high**: Lower `threshold_db` from 12 to 10
2. **Land masking**: CFAR works on water; ensure scene covers water
3. **Data range**: Verify `sigma0_vv_filtered` is in dB (not linear)

**Check:**

```python
print(f"VV range: {sigma0_vv_filtered.min():.1f} to {sigma0_vv_filtered.max():.1f} dB")
# Expected: -25 dB (water) to +5 dB (bright targets)
```

### Too many false alarms

**Solutions:**

1. Increase `threshold_db` from 12 to 15
2. Increase `window_size` from 40 to 50
3. Add land mask to exclude detections over land

### Performance issues

**Optimization:**

- CFAR is already fast (~50ms per 1000×1000 scene)
- For huge scenes, downsample before detection:
  ```python
  from scipy.ndimage import zoom
  sigma0_downsampled = zoom(sigma0_vv_filtered, 0.5)  # 2x faster
  ```

---

## 🚀 Production Checklist

- [ ] Apply database migration: `alembic upgrade head`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test with synthetic data: `POST /v1/vessels/ingest`
- [ ] Integrate into real Sentinel-1 pipeline
- [ ] Tune `threshold_db` for your region
- [ ] Verify detections in database
- [ ] Enable automatic scheduling
- [ ] Monitor logs for errors

---

## 📞 Support

**Common integration patterns:**

1. **Using Copernicus Data Space API:**
   - Download Sentinel-1 GRD (VV polarization)
   - Extract sigma0 from product metadata
   - Apply your speckle filter → insert vessel detection

2. **Using ESA SNAP:**
   - Export calibrated, filtered VV band as GeoTIFF
   - Read with GDAL → insert vessel detection

3. **Using xarray/rioxarray:**
   ```python
   import rioxarray
   data = rioxarray.open_rasterio("S1_VV.tif")
   sigma0_vv_db = data.values[0]  # First band
   geotransform = data.rio.transform().to_gdal()
   ```

**Need help?** Check logs:

```bash
docker compose logs -f scheduler | grep vessel
```
