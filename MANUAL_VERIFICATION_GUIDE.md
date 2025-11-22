# Manual Forecast Verification Guide

Quick reference for checking your forecast accuracy without automated tools.

---

## 🚀 Quick Start

Run the verification script:
```bash
cd /home/lenovo/scrimba/floodsight/backend
./verify_simple.sh
```

---

## 📊 Your Current Data

From the verification script, you have:
- **150 real GloFAS forecasts**
- **5 stations** (Berlin, Vienna, Dresden, Frankfurt, Cologne)
- **Lead times**: 6h to 240h (10 days)
- **Discharge range**: 15-2000 m³/s

---

## ✅ Method 1: Convergence Analysis (Easiest)

### Concept
Compare multiple forecasts for the same future time. As you get closer to the event, forecasts should converge (become more similar).

### How To Do It

**Step 1: Find overlapping forecasts**
```bash
cd /home/lenovo/scrimba/floodsight/backend

# Find times with multiple forecasts
docker compose exec db psql -U postgres -d floodsight -c \
  "SELECT ts, COUNT(*) FROM forecasts 
   WHERE source = 'GloFAS' 
   GROUP BY ts HAVING COUNT(*) > 1 
   ORDER BY ts LIMIT 5;"
```

**Step 2: Compare forecasts for same target**
```bash
# Example: Get all forecasts for Nov 13, 2025
docker compose exec db psql -U postgres -d floodsight -c \
  "SELECT 
     s.code as station,
     f.lead_hours,
     ROUND(f.discharge_m3s::numeric, 2) as discharge,
     f.model_run
   FROM forecasts f
   JOIN stations s ON f.station_id = s.id
   WHERE f.ts = '2025-11-13 00:00:00+00' 
   AND f.source = 'GloFAS'
   ORDER BY s.code, f.lead_hours;"
```

**Step 3: Calculate error**
```
Berlin Spree, Target: 2025-11-13 00:00
├─ 72h lead: 1200 m³/s (forecast made on Nov 10)
├─ 48h lead: 1180 m³/s (forecast made on Nov 11)
└─ 24h lead: 1150 m³/s (forecast made on Nov 12)

Error (72h vs 24h): |1200 - 1150| = 50 m³/s
Percentage error: 50/1150 × 100 = 4.3%
```

**Interpretation:**
- ✅ **Good**: Error < 10% → Forecasts are stable
- ⚠️ **Fair**: Error 10-20% → Some uncertainty
- ❌ **Poor**: Error > 20% → High uncertainty

---

## 🔬 Method 2: GloFAS Reanalysis Comparison (Most Accurate)

### Concept
Compare your forecast with GloFAS Reanalysis (hindcast) for the same time/location. This is the "ground truth" from the same model.

### How To Do It

**Step 1: Export your forecast**
```bash
# Pick a forecast that's now in the past
docker compose exec db psql -U postgres -d floodsight -c \
  "SELECT 
     s.code,
     s.lat,
     s.lon,
     f.ts as target_time,
     f.discharge_m3s as forecast_value,
     f.model_run
   FROM forecasts f
   JOIN stations s ON f.station_id = s.id
   WHERE f.ts < NOW() 
   AND f.source = 'GloFAS'
   ORDER BY f.ts DESC
   LIMIT 10;" > my_forecasts.txt
```

**Step 2: Download GloFAS Reanalysis**

1. Go to: https://cds.climate.copernicus.eu
2. Sign in with your account
3. Search for: **"CEMS GloFAS historical"**
4. Select:
   - **Product type**: Consolidated
   - **Variable**: River discharge in the last 24 hours
   - **Date**: Same as your forecast target
   - **Area**: Copy coordinates from your stations
   - **Format**: NetCDF

**Step 3: Extract reanalysis values**

Once downloaded, open the NetCDF file and extract discharge at your station coordinates.

**Step 4: Compare**
```
Berlin Spree (52.52°N, 13.40°E)
Target: 2025-11-11 00:00

Forecast (made 24h ahead): 1200 m³/s
Reanalysis (hindcast):     1150 m³/s

Error: |1200 - 1150| = 50 m³/s
Accuracy: 100 - (50/1150 × 100) = 95.7% ✅
```

---

## 👀 Method 3: Visual Inspection (Quick Check)

### How To Do It

**Step 1: Get forecast time series**
```bash
# Via API
curl -s http://localhost:8080/v1/forecasts?station_id=1 | jq '.[] | {lead: .lead_hours, discharge: .discharge_m3s}' | less

# Via Database
docker compose exec db psql -U postgres -d floodsight -c \
  "SELECT 
     lead_hours,
     discharge_m3s,
     ts
   FROM forecasts 
   WHERE station_id = 1 
   AND source = 'GloFAS'
   ORDER BY ts, lead_hours;"
```

**Step 2: Look for red flags**
- ❌ **Negative values**: Impossible for discharge
- ❌ **Sudden jumps**: e.g., 500 → 2000 → 400 m³/s
- ❌ **Out of range**: Rivers have typical ranges (e.g., Rhine: 500-3000 m³/s)
- ❌ **Flat lines**: Same value repeated (data issue)

**Step 3: Check reasonableness**
```
Typical discharge ranges (m³/s):
- Small rivers: 10-100
- Medium rivers: 100-1000
- Large rivers: 1000-5000+
```

---

## 📈 Accuracy Metrics

### Common Metrics

**Mean Absolute Error (MAE)**
```
MAE = (|forecast1 - actual1| + |forecast2 - actual2| + ...) / n
Lower is better
```

**Bias**
```
Bias = (forecast - actual)
Positive = Over-prediction
Negative = Under-prediction
Close to 0 is best
```

**Root Mean Square Error (RMSE)**
```
RMSE = sqrt((error1² + error2² + ...) / n)
Penalizes large errors more
```

**Accuracy Percentage**
```
Accuracy = 100 - (|error| / actual × 100)
95%+ is excellent
90-95% is good
<90% needs improvement
```

---

## 🎯 What Good Accuracy Looks Like

### By Lead Time (Typical GloFAS Performance)

| Lead Time | Expected MAE | Expected Accuracy |
|-----------|--------------|-------------------|
| 6-24 hours | <50 m³/s | >95% |
| 24-48 hours | <100 m³/s | >90% |
| 48-72 hours | <150 m³/s | >85% |
| 3-5 days | <200 m³/s | >80% |
| 5-10 days | <300 m³/s | >70% |

### Red Flags
- ⚠️ Accuracy < 70% at any lead time
- ⚠️ Bias > 20% (consistent over/under prediction)
- ⚠️ No convergence (72h forecast same as 6h)
- ⚠️ Wild swings between forecast runs

---

## 🔄 Workflow for Regular Verification

### Daily Routine
```bash
# 1. Run verification script
cd /home/lenovo/scrimba/floodsight/backend
./verify_simple.sh > verification_$(date +%Y%m%d).txt

# 2. Check for new overlapping forecasts
# 3. Look at convergence trends
# 4. Note any accuracy issues
```

### Weekly Routine
```bash
# 1. Download reanalysis for past week
# 2. Compare with your forecasts
# 3. Calculate accuracy metrics
# 4. Document findings
```

---

## 📊 Sample Verification Report

```
FloodSight Forecast Verification
=================================
Date: 2025-11-12
Period: Last 7 days
Method: Convergence Analysis

Station: Berlin Spree
---------------------
Forecasts analyzed: 30
Target times: 10
Convergence quality: GOOD ✅

Lead Time | Avg Error | Accuracy
----------|-----------|----------
24h       | 45 m³/s   | 94%
48h       | 72 m³/s   | 91%
72h       | 108 m³/s  | 87%

Findings:
- Forecasts converge well (low variance)
- No systematic bias detected
- Performance within expected range

Station: Rhine Cologne
----------------------
Forecasts analyzed: 30
Target times: 10
Convergence quality: FAIR ⚠️

Lead Time | Avg Error | Accuracy
----------|-----------|----------
24h       | 95 m³/s   | 88%
48h       | 156 m³/s  | 82%
72h       | 235 m³/s  | 75%

Findings:
- Higher than expected errors at 24h
- Possible model bias (+12% over-prediction)
- Recommend comparison with reanalysis

Overall Assessment: GOOD
Recommendation: Continue monitoring
```

---

## 💡 Tips

1. **Start Simple**: Use convergence analysis first (easiest)
2. **Be Patient**: Need 2-3 days of forecasts for good comparison
3. **Check Multiple Stations**: One station might have issues
4. **Look for Patterns**: Systematic errors are more concerning than random ones
5. **Document**: Keep notes of what you find

---

## 🚀 Next Steps

### To Get Better Verification:

**Option 1: Wait and Accumulate**
- Run forecast ingestion hourly
- Wait 1-2 weeks
- More data = better verification

**Option 2: Implement Automation**
- Auto-download reanalysis
- Auto-calculate metrics
- Generate reports automatically

**Option 3: Add Real Gauges**
- Compare with actual measurements
- Best possible verification
- Only available in some regions

---

## 📞 Quick Commands Reference

```bash
# Run verification
./verify_simple.sh

# Check forecast count
docker compose exec db psql -U postgres -d floodsight -c \
  "SELECT COUNT(*) FROM forecasts WHERE source = 'GloFAS';"

# Export forecasts to CSV
docker compose exec db psql -U postgres -d floodsight -c \
  "COPY (SELECT * FROM forecasts WHERE source = 'GloFAS') 
   TO STDOUT WITH CSV HEADER;" > forecasts.csv

# Get API data
curl http://localhost:8080/v1/forecasts | jq . > forecasts.json
```

---

**Questions?** Check the logs:
```bash
docker compose logs api | grep -i forecast
```




