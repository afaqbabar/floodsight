# FloodSight Dashboard - Quick Access Guide

## 🎯 **OPEN YOUR DASHBOARD NOW**

### Main Dashboard (Full Features with Real Data)
```
http://192.168.178.50:8080/dashboard-figma.html
```

### API-Connected Dashboard (Real-Time Updates)
```
http://192.168.178.50:8080/dashboard-api.html
```

---

## ✅ **PROBLEM SOLVED**

### What Was Wrong
Your dashboard was trying to connect to the **frontend port** (8080) instead of the **backend API port** (30636).

### What Was Fixed
Updated `/public/assets/js/api-service.js`:
- **Old**: `http://192.168.178.50:8080/v1` (frontend)
- **New**: `http://192.168.178.50:30636/v1` (backend API)

---

## 📊 **What You'll See**

When you open the dashboard, you should see:

✅ **Interactive Map**
   - 5 European monitoring stations
   - Color-coded by alert level
   - Clickable markers

✅ **Real-Time Forecasts**
   - ECMWF GloFAS data
   - Updated hourly
   - 10-day outlook

✅ **Active Alerts**
   - Currently: 5 active alerts
   - Severity indicators
   - Station details

✅ **API Status Indicator**
   - Green dot = "API Connected"
   - Shows connection status

---

## 🌐 **All Available Dashboards**

### Main Dashboards (With Real Data)
- **Full Dashboard**: http://192.168.178.50:8080/dashboard-figma.html
- **API Dashboard**: http://192.168.178.50:8080/dashboard-api.html
- **Admin Dashboard**: http://192.168.178.50:8080/admin-dashboard.html
- **Analytics**: http://192.168.178.50:8080/analytics-dashboard.html

### Landing & Info Pages
- **Home Page**: http://192.168.178.50:8080/
- **Health Check**: http://192.168.178.50:8080/health.html

### Test Pages
- **API Test**: http://192.168.178.50:8080/api-test-simple.html
- **Full Test**: http://192.168.178.50:8080/test-api.html

---

## 🔧 **Backend API Endpoints**

Your backend API is accessible at:
```
http://192.168.178.50:30636/v1
```

### Key Endpoints
- **Health**: `/v1/health`
- **Stations**: `/v1/stations`
- **Forecasts**: `/v1/forecasts`
- **Alerts**: `/v1/alerts`
- **API Docs**: http://192.168.178.50:30636/docs

---

## 📋 **Current Data Status**

✅ **5 Stations** (Berlin, Dresden, Cologne, Frankfurt, Vienna)
✅ **50+ Forecasts** (Real ECMWF GloFAS data)
✅ **5 Active Alerts** (Computed from forecasts)
✅ **Hourly Updates** (Automatic data ingestion)

---

## 🌐 **Public Access (via Cloudflare Tunnel)**

### Frontend Dashboard (For Everyone)
```
https://lab-grounds-super-behavioral.trycloudflare.com/dashboard-figma.html
```

### Backend API (For Developers)
```
https://shoe-mere-livestock-mild.trycloudflare.com/v1
```

---

## 🔍 **Testing in Browser**

Open the dashboard, then press **F12** (Developer Tools) and run:

```javascript
// Check API configuration
console.log('API URL:', await import('/assets/js/api-service.js').then(m => m.getAPIConfig()));

// Test API connection
fetch('http://192.168.178.50:30636/v1/health')
  .then(r => r.json())
  .then(data => console.log('✅ Backend:', data));

// Test stations
fetch('http://192.168.178.50:30636/v1/stations')
  .then(r => r.json())
  .then(stations => console.log('✅ Stations:', stations.length));
```

**Expected Output:**
```
API URL: { baseUrl: "http://192.168.178.50:30636/v1", timeout: 10000 }
✅ Backend: {status: "ok", app: "FloodSight Backend API", ...}
✅ Stations: 5
```

---

## 🚀 **What's Running**

### On Raspberry Pi (192.168.178.50)

1. **Frontend (Vite Dev Server)**
   - Port: 8080
   - Status: ✅ Running
   - Serves: Dashboard HTML/JS/CSS

2. **Backend API (Kubernetes)**
   - Port: 30636 (NodePort)
   - Status: ✅ Running
   - Pods: 2 replicas + 1 scheduler
   - Data: Real ECMWF GloFAS

3. **Database (PostgreSQL + PostGIS)**
   - Port: 5432 (internal)
   - Status: ✅ Running
   - Contains: Stations, forecasts, alerts

4. **Cloudflare Tunnels**
   - Frontend: lab-grounds-super-behavioral.trycloudflare.com
   - Backend: shoe-mere-livestock-mild.trycloudflare.com
   - Status: ✅ Running

---

## 🔄 **Data Updates**

- **Frequency**: Every hour
- **Source**: ECMWF EWDS (Early Warning Data Store)
- **Dataset**: GloFAS (Global Flood Awareness System)
- **Format**: NetCDF
- **Coverage**: 5 European river monitoring stations
- **Forecast Range**: 10 days ahead
- **Lead Times**: 24h, 48h, 72h, 96h, 120h, 144h, 168h, 192h, 216h, 240h

### Check Last Update
```bash
# Via API
curl http://192.168.178.50:30636/v1/forecasts | jq -r '.[0].forecast_timestamp'

# Via logs
kubectl logs -l component=scheduler -n floodsight --tail=50
```

---

## 🆘 **Troubleshooting**

### Dashboard Shows "API Offline"
1. Check backend is running:
   ```bash
   curl http://192.168.178.50:30636/v1/health
   ```
2. Check Kubernetes pods:
   ```bash
   kubectl get pods -n floodsight
   ```
3. Restart backend if needed:
   ```bash
   kubectl rollout restart deployment floodsight-backend -n floodsight
   ```

### No Data Loading
1. Check browser console (F12) for errors
2. Verify API URL in browser:
   ```javascript
   import('/assets/js/api-service.js').then(m => console.log(m.getAPIConfig()))
   ```
3. Clear browser cache (Ctrl+Shift+R)

### Map Not Showing
1. Check Leaflet is loading (view Network tab in F12)
2. Check for JavaScript errors in Console
3. Try different dashboard: `/dashboard-api.html`

---

## 💡 **Pro Tips**

1. **Use dashboard-figma.html** for the best experience (has most features)
2. **Open in Chrome/Firefox** for best compatibility
3. **Check browser console** (F12) if something doesn't work
4. **Use local IP** (192.168.178.50:8080) for fastest access
5. **Bookmark** your favorite dashboard URL

---

## 📚 **More Documentation**

- **ACCESS_GUIDE.md** - Complete system access guide
- **K8S_SUCCESS.md** - Kubernetes deployment details
- **REAL_GLOFAS_SUCCESS.md** - Real data integration status
- **VERCEL_TROUBLESHOOTING.md** - Vercel deployment guide

---

## 🎉 **You're All Set!**

Your FloodSight dashboard is now fully operational with:

✅ Real-time ECMWF GloFAS flood forecasts
✅ 5 European monitoring stations
✅ Active flood alerts
✅ Hourly automatic updates
✅ Beautiful interactive interface
✅ Running on your Raspberry Pi 5

**Open your dashboard now:**
```
http://192.168.178.50:8080/dashboard-figma.html
```

Enjoy your flood monitoring system! 🌊🎯

