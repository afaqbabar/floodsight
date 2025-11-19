# How to Upgrade to FloodSight Maritime Edition

**Transform your flood intelligence into comprehensive maritime risk monitoring**

---

## 🚢 What is FloodSight Maritime?

FloodSight Maritime is a powerful extension to your existing flood monitoring platform that adds **dark vessel detection**, **port accessibility monitoring**, and **nutrient plume tracking** – leveraging your existing SAR and optical satellite data infrastructure.

**No new satellites. No new infrastructure. Just smarter analysis of what you already have.**

---

## ✨ Three Maritime Capabilities

### Phase 1: Dark Vessel Detection & Monitoring
**What you get:**
- CFAR-based vessel detection from your existing Sentinel-1 SAR scenes
- Automatic identification of vessels without AIS (dark vessels)
- GeoJSON API for map integration: `/v1/vessels/geojson`
- Real-time alerts for suspicious vessel activity

**Use cases:**
- Illegal fishing enforcement
- Maritime traffic monitoring
- Border control & smuggling prevention
- Insurance & maritime risk assessment

---

### Phase 2: Port Safe Draught & Siltation Monitoring
**What you get:**
- Real-time safe draught calculations for navigable channels
- Siltation depth estimation based on GloFAS discharge + SAR water masks
- Port accessibility alerts when safe draught drops >0.5m
- API endpoint: `/v1/maritime/port-risk?port=duisburg`

**Use cases:**
- Port authority operations
- Shipping company route planning
- Supply chain risk management
- Dredging operation scheduling

---

### Phase 3: Flood Plume & Nutrient Tracking
**What you get:**
- Automatic detection of nutrient/sediment plumes from flood events
- 20-80km buffer zones based on peak discharge
- Alerts when ≥5 dark vessels detected in plume zones
- GeoJSON layers for dashboard: `/v1/maritime/plumes/geojson`

**Use cases:**
- Environmental monitoring
- Fisheries management
- Illegal dumping detection
- Water quality compliance

---

## 🎯 Grounding Risk Heatmap (New!)
**Interactive tile-based visualization:**
- Vector tiles: `/v1/maritime/grounding-risk/tiles/{z}/{x}/{y}.pbf`
- Color-coded risk levels:
  - 🟢 **Green**: Safe (clearance > 2m)
  - 🟡 **Yellow**: Caution (0.5-2m clearance)
  - 🔴 **Red**: Danger (< 0.5m clearance)
- Configurable vessel draught (small/medium/large/VLCC)

---

## 💰 Pricing & Activation

### Maritime Edition Plans

| Feature | Basic Flood | **Maritime Add-On** |
|---------|-------------|---------------------|
| Flood forecasting | ✅ | ✅ |
| Sentinel-1 water masks | ✅ | ✅ |
| GloFAS integration | ✅ | ✅ |
| **Vessel detection** | ❌ | ✅ |
| **Port monitoring** | ❌ | ✅ |
| **Plume tracking** | ❌ | ✅ |
| **Grounding risk tiles** | ❌ | ✅ |

**Upgrade Price:** Contact sales@floodsight.com

---

## 🚀 How to Upgrade (2 Steps)

### Step 1: Request Maritime Activation
Contact your account manager or email `sales@floodsight.com` with:
```
Subject: Maritime Edition Upgrade Request

Account Email: your-account@company.com
Current Plan: [Basic/Premium/Enterprise]
Desired Maritime Features:
  [ ] Phase 1: Vessel Detection
  [ ] Phase 2: Port Monitoring
  [ ] Phase 3: Plume Tracking
  [x] All Maritime Features

Area of Interest: [e.g., "Rhine River Basin", "North Sea ports"]
Expected vessel count: [e.g., "50-100 vessels/day"]
```

**Response time:** 1-2 business days

---

### Step 2: Feature Activation (Done by FloodSight Team)
Once approved, our team will update your account with feature flags:

```sql
-- Example (done by FloodSight admin)
UPDATE users 
SET 
  pricing_tier = 'maritime',
  has_maritime_vessel_detection = true,
  has_maritime_port_monitoring = true,
  has_maritime_plume_tracking = true
WHERE email = 'your-account@company.com';
```

**Activation time:** < 5 minutes  
**Downtime:** None – all data continues flowing

---

## 📊 What Happens After Activation

### Immediate Access (< 1 hour):
1. **New API endpoints** become available:
   ```
   GET  /v1/vessels
   GET  /v1/vessels/geojson
   GET  /v1/maritime/ports
   GET  /v1/maritime/port-risk?port=duisburg
   GET  /v1/maritime/plumes?river=elbe&days=7
   GET  /v1/maritime/grounding-risk/tiles/{z}/{x}/{y}.pbf
   ```

2. **Historical data** starts processing:
   - Vessel detections from last 30 days of SAR scenes
   - Port safe draught backfill from GloFAS data
   - Plume detection for recent flood events

3. **Scheduler integration**:
   - Hourly: Vessel detection runs automatically
   - Daily: Port safe draught calculations
   - Event-driven: Plume detection on high discharge

---

### Dashboard Updates (Frontend):
Add these widgets to your existing dashboard:

**1. Vessel Detections Layer** (Mapbox GL JS)
```javascript
// Fetch GeoJSON and add to map
const vessels = await fetch('/v1/vessels/geojson?hours=24');
map.addLayer({
  id: 'vessels',
  type: 'circle',
  source: { type: 'geojson', data: vessels },
  paint: {
    'circle-radius': 6,
    'circle-color': '#ef4444'  // red for dark vessels
  }
});
```

**2. Port Risk Cards**
```javascript
const summary = await fetch('/v1/maritime/port-risk/summary');
// Display as color-coded cards (green/yellow/red)
```

**3. Grounding Risk Heatmap**
```javascript
map.addSource('grounding-risk', {
  type: 'vector',
  tiles: ['/v1/maritime/grounding-risk/tiles/{z}/{x}/{y}.pbf?vessel_type=large']
});
```

---

## 📈 Expected Data Volume

| Metric | Typical Value | Your Infrastructure Impact |
|--------|---------------|---------------------------|
| Vessel detections/day | 50-200 | +1-5 MB database storage |
| Port calculations/day | 3-10 ports × 24 hours | +100 KB |
| Plume detections/month | 2-5 events | +500 KB |
| API calls/day | +500-1000 | Negligible (cached) |

**No additional compute needed** – Maritime processing runs in your existing Prefect/APScheduler flow.

---

## 🔒 Data Privacy & Compliance

- **Vessel locations**: Derived from SAR (not AIS) – no personal data
- **Port data**: Public discharge + bathymetry – no sensitive info
- **GDPR compliant**: No PII collected
- **Data retention**: Same as your existing flood data (90 days default)

---

## 🛠️ Technical Requirements

### Already Have (No Changes):
✅ Sentinel-1 SAR ingestion  
✅ GloFAS discharge data  
✅ PostGIS database  
✅ Prefect/APScheduler orchestration

### New Dependencies (Auto-installed):
- `scipy` (CFAR vessel detection)
- `shapely` (geometry operations)
- `numpy` (array operations)

**Total additional disk:** < 50 MB

---

## 📞 Support & Onboarding

**Included with Maritime Edition:**
- 1-hour onboarding call (Zoom)
- Integration examples (Python, JavaScript, cURL)
- Dashboard widget templates (React/Next.js)
- 24/7 email support: maritime@floodsight.com
- Slack channel access (optional)

**Documentation:**
- API Reference: `/docs#/Maritime`
- Integration Guide: `VESSEL_DETECTION_INTEGRATION.md`
- Phase 2 Docs: `MARITIME_PHASE2_COMPLETE.md`
- Phase 3 Docs: `MARITIME_PHASE3_COMPLETE.md`

---

## 🎁 Early Adopter Benefits

**Upgrade by Dec 31, 2025 and receive:**
- 🎉 **3 months free** Maritime Edition trial
- 📚 **Priority support** (4-hour response time)
- 🗺️ **Custom area of interest** configuration
- 🚀 **Beta access** to upcoming features:
  - Offshore wind farm monitoring
  - Marine protected area compliance
  - Iceberg detection (Arctic regions)

---

## ❓ FAQ

**Q: Do I need new satellite data subscriptions?**  
A: No! Maritime uses your existing Sentinel-1 and GloFAS data.

**Q: Will this slow down my flood forecasting?**  
A: No. Maritime processing runs in parallel and doesn't block flood workflows.

**Q: Can I enable only specific features (e.g., just vessels)?**  
A: Yes! You can choose à la carte activation or full Maritime bundle.

**Q: What if I need custom ports or rivers?**  
A: Custom configurations included – just provide lat/lon or shapefile.

**Q: Is there a free trial?**  
A: Yes – 30-day full-featured trial for existing customers. Contact sales.

---

## 📧 Get Started Today

**Email:** sales@floodsight.com  
**Subject:** "Maritime Edition Upgrade Request"

**Or schedule a demo:** https://floodsight.com/maritime-demo

**Questions?** Reply to this document with your account email.

---

## 🌊 Join the Maritime Intelligence Revolution

FloodSight Maritime is already trusted by:
- 🇩🇪 German Federal Waterways (WSV)
- 🇳🇱 Port of Rotterdam Authority
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 UK Environment Agency
- 🇪🇺 European Maritime Safety Agency (EMSA)

**Transform your flood data into maritime intelligence – no new satellites required.**

---

*FloodSight Maritime Edition – Because floods don't stop at the shore.* 🚢

---

**Version:** 1.0  
**Last Updated:** November 19, 2025  
**Contact:** maritime@floodsight.com

