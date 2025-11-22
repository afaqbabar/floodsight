# How to Set Alert Levels in FloodSight

## 📊 **Current Alert Thresholds**

Your system uses these global thresholds for all rivers:

| Level | Threshold | Color | Description |
|-------|-----------|-------|-------------|
| **Info** | 800 m³/s | 🔵 Blue | Elevated water levels, monitor situation |
| **Warning** | 1200 m³/s | 🟡 Yellow | High water levels, prepare for potential flooding |
| **Severe** | 1600 m³/s | 🟠 Orange | Very high levels, flooding likely |
| **Extreme** | 2000 m³/s | 🔴 Red | Critical flooding, take immediate action |

## ⚠️ **Problem: One-Size-Fits-All Thresholds**

**Current issue:**
- Same thresholds for ALL rivers (800, 1200, 1600, 2000 m³/s)
- Doesn't make sense! Rivers have vastly different sizes:
  - Rhine (Cologne): Normal flow ~2000 m³/s
  - Spree (Berlin): Normal flow ~20 m³/s

**Example of the problem:**
- Rhine at 1800 m³/s = **NORMAL** (no alert needed)
- Spree at 1800 m³/s = **IMPOSSIBLE** (river would be destroyed!)
- Main at 800 m³/s = **EXTREME FLOOD** (should be red alert!)

---

## ✅ **Solution 1: Quick Fix - Adjust Global Thresholds**

### **Option A: Conservative (Suitable for smaller rivers)**

For systems monitoring primarily smaller/medium rivers:

```yaml
ALERT_THRESHOLD_INFO: "300"     # 300 m³/s
ALERT_THRESHOLD_WARNING: "600"  # 600 m³/s
ALERT_THRESHOLD_SEVERE: "900"   # 900 m³/s
ALERT_THRESHOLD_EXTREME: "1200" # 1200 m³/s
```

**Result:**
- ✅ Better for Main, Elbe, Spree
- ❌ Rhine/Danube will show constant alerts

### **Option B: Aggressive (Suitable for major rivers)**

For systems monitoring primarily large rivers:

```yaml
ALERT_THRESHOLD_INFO: "2500"    # 2500 m³/s
ALERT_THRESHOLD_WARNING: "4000" # 4000 m³/s
ALERT_THRESHOLD_SEVERE: "6000"  # 6000 m³/s
ALERT_THRESHOLD_EXTREME: "8000" # 8000 m³/s
```

**Result:**
- ✅ Better for Rhine/Danube
- ❌ Smaller rivers will never trigger alerts

---

## ✅ **Solution 2: River-Specific Thresholds (RECOMMENDED)**

### **Realistic Thresholds by River:**

Based on historical data and flood levels:

#### **1. Spree (Berlin) - Small Urban River**
```yaml
Station: Berlin Spree
Normal: 15-25 m³/s
Alert Thresholds:
  Info:     40 m³/s   # 2x normal
  Warning:  60 m³/s   # 3x normal
  Severe:   80 m³/s   # 4x normal
  Extreme:  100 m³/s  # 5x normal
```

#### **2. Main (Frankfurt) - Small River**
```yaml
Station: Frankfurt Main
Normal: 150-250 m³/s
Alert Thresholds:
  Info:     400 m³/s   # High water starting
  Warning:  600 m³/s   # Significant flooding
  Severe:   800 m³/s   # Major flooding
  Extreme:  1000 m³/s  # Extreme flooding
```

#### **3. Elbe (Dresden) - Medium River**
```yaml
Station: Dresden Elbe
Normal: 300-500 m³/s
Alert Thresholds:
  Info:     800 m³/s   # High water
  Warning:  1500 m³/s  # Flood stage 1
  Severe:   2500 m³/s  # Flood stage 2
  Extreme:  4000 m³/s  # Flood stage 3
```

#### **4. Rhine (Cologne) - Major River**
```yaml
Station: Cologne Rhine
Normal: 2000-2500 m³/s
Alert Thresholds:
  Info:     3500 m³/s  # High water mark
  Warning:  5000 m³/s  # Flood stage 1
  Severe:   7000 m³/s  # Flood stage 2
  Extreme:  9000 m³/s  # Flood stage 3 (catastrophic)
```

#### **5. Danube (Vienna) - Major River**
```yaml
Station: Vienna Danube
Normal: 1900-2100 m³/s
Alert Thresholds:
  Info:     3000 m³/s  # High water mark
  Warning:  4500 m³/s  # Flood stage 1
  Severe:   6500 m³/s  # Flood stage 2
  Extreme:  8500 m³/s  # Flood stage 3
```

---

## 🔧 **How to Apply Changes**

### **Method 1: Update Global Thresholds (Quick)**

**Step 1: Edit ConfigMap**
```bash
nano /home/lenovo/scrimba/floodsight/deploy/k8s/base/backend-configmap.yaml
```

**Step 2: Find and modify these lines:**
```yaml
# Alert thresholds (m³/s)
ALERT_THRESHOLD_INFO: "800"
ALERT_THRESHOLD_WARNING: "1200"
ALERT_THRESHOLD_SEVERE: "1600"
ALERT_THRESHOLD_EXTREME: "2000"
```

**Step 3: Change to your desired values** (example for medium rivers):
```yaml
# Alert thresholds (m³/s) - Adjusted for medium rivers
ALERT_THRESHOLD_INFO: "500"
ALERT_THRESHOLD_WARNING: "1000"
ALERT_THRESHOLD_SEVERE: "1500"
ALERT_THRESHOLD_EXTREME: "2000"
```

**Step 4: Apply changes:**
```bash
kubectl apply -f /home/lenovo/scrimba/floodsight/deploy/k8s/base/backend-configmap.yaml
kubectl rollout restart deployment floodsight-backend -n floodsight
kubectl rollout restart deployment floodsight-scheduler -n floodsight
```

**Step 5: Recompute alerts:**
```bash
curl -X POST http://192.168.178.50:30636/v1/alerts/compute
```

**Step 6: Refresh dashboard**
- Hard refresh: Ctrl + Shift + R

---

### **Method 2: Implement Station-Specific Thresholds (Advanced)**

This requires code changes to support per-station thresholds.

**Step 1: Create station-specific thresholds file**

Create `/home/lenovo/scrimba/floodsight/backend/app/config/alert_thresholds.json`:

```json
{
  "stations": {
    "BERLIN-SPREE": {
      "info": 40,
      "warning": 60,
      "severe": 80,
      "extreme": 100
    },
    "MAIN-FRANKFURT": {
      "info": 400,
      "warning": 600,
      "severe": 800,
      "extreme": 1000
    },
    "ELBE-DRESDEN": {
      "info": 800,
      "warning": 1500,
      "severe": 2500,
      "extreme": 4000
    },
    "RHINE-COLOGNE": {
      "info": 3500,
      "warning": 5000,
      "severe": 7000,
      "extreme": 9000
    },
    "DANUBE-VIENNA": {
      "info": 3000,
      "warning": 4500,
      "severe": 6500,
      "extreme": 8500
    }
  },
  "default": {
    "info": 800,
    "warning": 1200,
    "severe": 1600,
    "extreme": 2000
  }
}
```

**Step 2: Update alert service to load station-specific thresholds**

This would require modifying `/home/lenovo/scrimba/floodsight/backend/app/services/alerts.py` to read from the JSON file instead of using global thresholds.

---

## 📋 **Quick Command Reference**

### **Check Current Thresholds:**
```bash
kubectl get configmap floodsight-backend-config -n floodsight -o yaml | grep "ALERT_THRESHOLD"
```

### **Update Thresholds (Example):**
```bash
kubectl patch configmap floodsight-backend-config -n floodsight --type merge -p '
{
  "data": {
    "ALERT_THRESHOLD_INFO": "500",
    "ALERT_THRESHOLD_WARNING": "1000",
    "ALERT_THRESHOLD_SEVERE": "1500",
    "ALERT_THRESHOLD_EXTREME": "2000"
  }
}'

# Restart services
kubectl rollout restart deployment floodsight-backend -n floodsight
kubectl rollout restart deployment floodsight-scheduler -n floodsight

# Wait for restart
sleep 15

# Recompute alerts
curl -X POST http://192.168.178.50:30636/v1/alerts/compute
```

### **View Current Alerts:**
```bash
curl http://192.168.178.50:30636/v1/alerts | jq
```

### **Check Alert Computation in Logs:**
```bash
kubectl logs -l component=scheduler -n floodsight --tail=50 | grep alert
```

---

## 🎯 **Recommended Settings for Your Current Setup**

Given your 5 rivers (Spree, Main, Elbe, Rhine, Danube), I recommend:

### **Option 1: Medium River Compromise**
Best for balanced alerts across all rivers:

```yaml
ALERT_THRESHOLD_INFO: "600"     # Catches Main, Elbe starting high water
ALERT_THRESHOLD_WARNING: "1500" # Rhine/Danube starting high, Main/Elbe flooding
ALERT_THRESHOLD_SEVERE: "3000"  # Rhine/Danube flooding, Main/Elbe major flood
ALERT_THRESHOLD_EXTREME: "5000" # Rhine/Danube major flood
```

**Result:**
- Rhine/Danube: Will show alerts when actually high
- Main/Elbe: Will show appropriate warnings
- Spree: May never trigger (too small)

### **Option 2: Focus on Smaller Rivers**
If Main and Elbe are your primary concern:

```yaml
ALERT_THRESHOLD_INFO: "300"
ALERT_THRESHOLD_WARNING: "600"
ALERT_THRESHOLD_SEVERE: "1000"
ALERT_THRESHOLD_EXTREME: "1500"
```

**Result:**
- Main/Elbe: Perfect sensitivity
- Rhine/Danube: Will show CONSTANT alerts (too sensitive)

---

## 🧪 **Testing Your Thresholds**

After changing thresholds:

**1. Check which stations would trigger alerts:**
```bash
curl -s http://192.168.178.50:30636/v1/forecasts | jq '.[] | select(.discharge_m3s > 600) | {station: .station_id, discharge: .discharge_m3s}'
```

**2. Manually compute alerts:**
```bash
curl -X POST http://192.168.178.50:30636/v1/alerts/compute
```

**3. View new alerts:**
```bash
curl http://192.168.178.50:30636/v1/alerts | jq '.[] | {station: .station_id, level: .level, message: .message}'
```

**4. Check dashboard:**
- Refresh browser (Ctrl + Shift + R)
- Look at "Active Alerts" section
- Check alert levels on map markers

---

## 💡 **Understanding Alert Logic**

### **How Alerts Are Computed:**

1. **Scheduler runs hourly** (or manually triggered)
2. **Gets latest forecasts** for each station
3. **Compares discharge** to thresholds:
   ```
   if discharge >= EXTREME_THRESHOLD → Create EXTREME alert
   else if discharge >= SEVERE_THRESHOLD → Create SEVERE alert
   else if discharge >= WARNING_THRESHOLD → Create WARNING alert
   else if discharge >= INFO_THRESHOLD → Create INFO alert
   else → No alert
   ```
4. **Creates alert** in database
5. **Sends notifications** (if configured)
6. **Dashboard displays** active alerts

### **Alert Expiration:**

Alerts remain active until:
- New forecast shows discharge below threshold
- Manual deletion via API
- Scheduled cleanup (if configured)

---

## 📚 **Additional Resources**

### **Official Flood Stage Information:**

- **Rhine (Cologne)**: https://www.hochwasser-zentrum.de/
- **Danube (Vienna)**: https://www.hydro.bmlrt.gv.at/
- **Elbe (Dresden)**: https://www.umwelt.sachsen.de/
- **Pegelonline (Germany)**: https://www.pegelonline.wsv.de/

### **GloFAS Documentation:**

- **GloFAS Portal**: https://global-flood.emergency.copernicus.eu/
- **Alert Methodology**: https://www.globalfloods.eu/

---

## 🎯 **Quick Start: Set Alerts for Your Rivers**

**For immediate improvement, use these settings:**

```bash
# Edit config
nano /home/lenovo/scrimba/floodsight/deploy/k8s/base/backend-configmap.yaml

# Change to:
ALERT_THRESHOLD_INFO: "600"
ALERT_THRESHOLD_WARNING: "1500"
ALERT_THRESHOLD_SEVERE: "3000"
ALERT_THRESHOLD_EXTREME: "5000"

# Apply
kubectl apply -f /home/lenovo/scrimba/floodsight/deploy/k8s/base/backend-configmap.yaml
kubectl rollout restart deployment floodsight-backend floodsight-scheduler -n floodsight
sleep 15
curl -X POST http://192.168.178.50:30636/v1/alerts/compute
```

**Then refresh your dashboard!**

---

## 🆘 **Troubleshooting**

### **Alerts Not Updating:**
1. Check if backend restarted: `kubectl get pods -n floodsight`
2. Check scheduler logs: `kubectl logs -l component=scheduler -n floodsight --tail=50`
3. Manually trigger: `curl -X POST http://192.168.178.50:30636/v1/alerts/compute`
4. Hard refresh dashboard: Ctrl + Shift + R

### **Too Many Alerts:**
- Increase thresholds (make them higher)
- Focus on "Severe" and "Extreme" only
- Disable "Info" and "Warning" in dashboard filters

### **Not Enough Alerts:**
- Decrease thresholds (make them lower)
- Check if forecasts are available
- Verify data is real (not fake)

---

**Your alert system is now ready to customize!** 🚨✅

