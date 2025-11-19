# FloodSight Dashboard - CORRECTED Access URLs

## ✅ **PROBLEM SOLVED: Port Conflict Fixed**

### What Was Wrong

- Port **8080** had a conflict with the backend API
- The external IP (192.168.178.50:8080) was routing to the backend (uvicorn), not the frontend (Vite)

### What Was Fixed

- Moved frontend to port **5173** (Vite's default)
- Updated Cloudflare tunnel
- Now both services work without conflicts

---

## 🌊 **OPEN YOUR DASHBOARD NOW**

### ⭐ **USE THIS URL:**

```
http://192.168.178.50:5173/dashboard-figma.html
```

**Or use the public URL from anywhere:**

```
https://shoppers-applications-prairie-reserves.trycloudflare.com/dashboard-figma.html
```

---

## 📋 **ALL AVAILABLE DASHBOARDS**

### Main Dashboards (With Real ECMWF Data)

- **Full Dashboard**: http://192.168.178.50:5173/dashboard-figma.html
- **API Dashboard**: http://192.168.178.50:5173/dashboard-api.html
- **Admin Dashboard**: http://192.168.178.50:5173/admin-dashboard.html
- **Analytics**: http://192.168.178.50:5173/analytics-dashboard.html

### Info Pages

- **Landing Page**: http://192.168.178.50:5173/
- **Health Check**: http://192.168.178.50:5173/health.html
- **API Test**: http://192.168.178.50:5173/api-test-simple.html

---

## 🌐 **PUBLIC ACCESS (Cloudflare Tunnels)**

### Frontend Dashboard

```
https://shoppers-applications-prairie-reserves.trycloudflare.com/dashboard-figma.html
```

### Backend API

```
https://shoe-mere-livestock-mild.trycloudflare.com/v1
```

**API Docs:**

```
https://shoe-mere-livestock-mild.trycloudflare.com/docs
```

---

## 🎯 **PORT SUMMARY**

| Service              | Port  | Protocol | Purpose                        |
| -------------------- | ----- | -------- | ------------------------------ |
| **Frontend (Vite)**  | 5173  | HTTP     | Dashboard UI                   |
| **Backend API**      | 30636 | HTTP     | REST API (Kubernetes NodePort) |
| **Backend Internal** | 8080  | HTTP     | Inside K8s cluster             |
| **Database**         | 5432  | TCP      | PostgreSQL (internal only)     |

---

## 🧪 **QUICK TEST**

Open your browser and go to:

```
http://192.168.178.50:5173/dashboard-figma.html
```

**You should see:**

- ✅ Interactive map with 5 European stations
- ✅ "API Connected" indicator (green dot)
- ✅ Real-time river discharge forecasts
- ✅ Active flood alerts (5 currently active)
- ✅ Station cards with data

**In the browser console (F12), you should see NO errors.**

---

## 🔧 **SERVICE STATUS**

### Frontend (Vite Dev Server)

- **Status**: ✅ Running
- **Port**: 5173
- **Process**: `node .../vite --host 0.0.0.0`
- **Logs**: `/tmp/frontend-dev.log`

### Backend API (Kubernetes)

- **Status**: ✅ Running
- **Port**: 30636 (NodePort)
- **Pods**: 2 backend + 1 scheduler
- **Data**: Real ECMWF GloFAS (updates hourly)

### Cloudflare Tunnels

- **Frontend**: shoppers-applications-prairie-reserves.trycloudflare.com
- **Backend**: shoe-mere-livestock-mild.trycloudflare.com
- **Status**: ✅ Running

---

## 📊 **CURRENT DATA**

✅ **5 Stations**

- Berlin Spree (Germany)
- Dresden Elbe (Germany)
- Cologne Rhine (Germany)
- Frankfurt Main (Germany)
- Vienna Danube (Austria)

✅ **50+ Forecasts**

- Source: ECMWF EWDS (Early Warning Data Store)
- Dataset: GloFAS (Global Flood Awareness System)
- Updated: Every hour
- Range: 10 days ahead

✅ **5 Active Alerts**

- Computed from forecast thresholds
- Severity levels: Info, Warning, Alert, Critical

---

## 🔍 **TROUBLESHOOTING**

### Still Seeing 404?

1. **Make sure you're using port 5173 (not 8080!)**
   - Correct: http://192.168.178.50:**5173**/dashboard-figma.html
   - Wrong: http://192.168.178.50:8080/dashboard-figma.html

2. **Clear your browser cache**
   - Hard refresh: Ctrl + Shift + R
   - Or open in incognito/private window

3. **Check if Vite is running**
   ```bash
   ps aux | grep vite
   ```

### Dashboard Loads But No Data?

1. **Check API connection in browser console (F12)**

   ```javascript
   fetch('http://192.168.178.50:30636/v1/health')
     .then((r) => r.json())
     .then(console.log);
   ```

2. **Look for "API Connected" indicator**
   - Should show green dot in top right
   - If red, check backend is running

3. **Verify backend is accessible**
   ```bash
   curl http://192.168.178.50:30636/v1/health
   ```

### Need to Restart Services?

**Restart Frontend:**

```bash
pkill -f vite
cd /home/lenovo/scrimba/floodsight
nohup npm run dev -- --host 0.0.0.0 > /tmp/frontend-dev.log 2>&1 &
```

**Restart Backend:**

```bash
kubectl rollout restart deployment floodsight-backend -n floodsight
```

**Restart Cloudflare Tunnels:**

```bash
# Stop all tunnels
pkill cloudflared

# Restart frontend tunnel
nohup cloudflared tunnel --url http://localhost:5173 > /tmp/cloudflare-frontend.log 2>&1 &

# Restart backend tunnel
nohup cloudflared tunnel --url http://192.168.178.50:30636 > /tmp/cloudflare-tunnel.log 2>&1 &

# Check tunnel URLs
sleep 10
cat /tmp/cloudflare-frontend.log | grep "Your quick Tunnel"
cat /tmp/cloudflare-tunnel.log | grep "Your quick Tunnel"
```

---

## 💡 **PRO TIPS**

1. **Bookmark the correct URL**: http://192.168.178.50:5173/dashboard-figma.html
2. **Use port 5173 for frontend**, not 8080
3. **Port 8080 is for backend API** (inside Kubernetes)
4. **Port 30636 is the backend NodePort** (accessible from host)
5. **Check browser console (F12)** if you see issues

---

## 📚 **RELATED DOCUMENTATION**

- **ACCESS_GUIDE.md** - Complete system access guide
- **DASHBOARD_ACCESS.md** - Original dashboard guide (outdated)
- **K8S_SUCCESS.md** - Kubernetes deployment details
- **REAL_GLOFAS_SUCCESS.md** - Real data integration status

---

## 🎉 **SUMMARY**

Your FloodSight system is fully operational!

**✅ Frontend Dashboard:**

- Local: http://192.168.178.50:5173/dashboard-figma.html
- Public: https://shoppers-applications-prairie-reserves.trycloudflare.com/dashboard-figma.html

**✅ Backend API:**

- Local: http://192.168.178.50:30636/v1
- Public: https://shoe-mere-livestock-mild.trycloudflare.com/v1

**✅ Real-Time Data:**

- ECMWF GloFAS forecasts
- 5 European monitoring stations
- Hourly automatic updates
- Active flood alerts

**Open your dashboard now and enjoy! 🌊🎯**
