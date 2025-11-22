# FloodSight Access Guide

## 🌐 Public URLs (Accessible from Anywhere)

### Frontend Dashboard (Your Main App)
```
https://lab-grounds-super-behavioral.trycloudflare.com
```
**What you'll see:**
- Interactive map with 5 European flood monitoring stations
- Real-time river discharge forecasts
- Active flood alerts
- Station details and charts

### Backend API (For Development/Integration)
```
https://shoe-mere-livestock-mild.trycloudflare.com
```

**API Documentation:**
```
https://shoe-mere-livestock-mild.trycloudflare.com/docs
```

**Example Endpoints:**
- Health: `/v1/health`
- Stations: `/v1/stations`
- Forecasts: `/v1/forecasts`
- Alerts: `/v1/alerts`

---

## 🏠 Local Access (Within Your Network)

### Frontend Dashboard
```
http://192.168.178.50:8080
```

### Backend API
```
http://192.168.178.50:30636
```

---

## 📱 Quick Access Links

### For End Users (Dashboard)
Share this with anyone who wants to see flood forecasts:
```
https://lab-grounds-super-behavioral.trycloudflare.com
```

### For Developers (API)
Use this in your frontend code or Vercel:
```
https://shoe-mere-livestock-mild.trycloudflare.com
```

---

## 🔧 Service Management

### Check What's Running
```bash
# Frontend dev server
ps aux | grep "vite"

# Backend (Kubernetes)
kubectl get pods -n floodsight

# Cloudflare tunnels
ps aux | grep cloudflared
```

### View Logs
```bash
# Frontend logs
tail -f /tmp/frontend-dev.log

# Backend logs
kubectl logs -f -l component=backend -n floodsight

# Scheduler logs (data ingestion)
kubectl logs -f -l component=scheduler -n floodsight

# Cloudflare tunnel logs
tail -f /tmp/cloudflare-tunnel.log
tail -f /tmp/cloudflare-frontend.log
```

### Restart Services

#### Restart Frontend
```bash
# Stop frontend
pkill -f "vite"

# Start frontend
cd /home/lenovo/scrimba/floodsight
nohup npm run dev -- --host 0.0.0.0 --port 8080 > /tmp/frontend-dev.log 2>&1 &
```

#### Restart Backend
```bash
# Restart backend pods
kubectl rollout restart deployment floodsight-backend -n floodsight
kubectl rollout restart deployment floodsight-scheduler -n floodsight
```

#### Restart Cloudflare Tunnels
```bash
# Stop all tunnels
pkill cloudflared

# Restart frontend tunnel
nohup cloudflared tunnel --url http://localhost:8080 > /tmp/cloudflare-frontend.log 2>&1 &

# Restart backend tunnel
nohup cloudflared tunnel --url http://192.168.178.50:30636 > /tmp/cloudflare-tunnel.log 2>&1 &

# Wait 10 seconds, then check logs
sleep 10
cat /tmp/cloudflare-frontend.log | grep "Your quick Tunnel"
cat /tmp/cloudflare-tunnel.log | grep "Your quick Tunnel"
```

#### Quick Restart Script
```bash
./restart-cloudflare-tunnel.sh
```

---

## 🧪 Testing

### Test Frontend
```bash
# From command line
curl -I http://localhost:8080

# In browser console (F12)
console.log('Frontend loaded!');
```

### Test Backend
```bash
# Health check
curl https://shoe-mere-livestock-mild.trycloudflare.com/v1/health

# Get stations
curl https://shoe-mere-livestock-mild.trycloudflare.com/v1/stations | jq

# Get forecasts
curl https://shoe-mere-livestock-mild.trycloudflare.com/v1/forecasts | jq

# Get alerts
curl https://shoe-mere-livestock-mild.trycloudflare.com/v1/alerts | jq
```

### Test Data Updates
```bash
# Trigger manual data ingestion
kubectl exec -n floodsight deploy/floodsight-scheduler -- \
  python -m app.workers.flows run

# Check latest forecast timestamp
curl -s https://shoe-mere-livestock-mild.trycloudflare.com/v1/forecasts | \
  jq -r '.[0].forecast_timestamp'
```

---

## 🚀 Vercel Integration

### Environment Variable Setup
1. Go to: https://vercel.com/YOUR_PROJECT/settings/environment-variables
2. Add variable:
   ```
   Name:  VITE_API_URL
   Value: https://shoe-mere-livestock-mild.trycloudflare.com
   Environment: ✓ Production
   ```
3. Go to: Deployments
4. Click "..." → "Redeploy"
5. Wait for "Ready" status

### Frontend Code
```javascript
// In your frontend code (e.g., src/config.js or similar)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Use it
async function fetchStations() {
  const response = await fetch(`${API_URL}/v1/stations`);
  return response.json();
}
```

---

## 🔒 Security Notes

### Cloudflare Tunnel URLs
- These URLs are **temporary** and will change if you restart the tunnel
- For production, consider:
  - Cloudflare Argo Tunnel with custom domain
  - ngrok with reserved subdomain
  - Proper SSL/TLS certificates with Let's Encrypt

### API Access
- Currently no authentication (suitable for public dashboard)
- Backend has CORS enabled for specific origins
- For production with user accounts, enable Supabase JWT auth

### Database
- Currently using default `postgres:postgres` credentials
- For production, change these in `deploy/k8s/base/backend-secrets.yaml`

---

## 📊 What's Running on Your Pi

### Port Mapping
| Service | Internal Port | External Port | Cloudflare Tunnel |
|---------|--------------|---------------|-------------------|
| Frontend | 8080 | - | lab-grounds-super-behavioral.trycloudflare.com |
| Backend | 8080 (container) | 30636 (NodePort) | shoe-mere-livestock-mild.trycloudflare.com |
| Database | 5432 | - | (internal only) |
| Prometheus | 9090 | - | (internal only) |

### Kubernetes Namespaces
```bash
# View all resources
kubectl get all -n floodsight

# Backend deployment (2 replicas)
kubectl get pods -n floodsight -l component=backend

# Scheduler (data ingestion, 1 replica)
kubectl get pods -n floodsight -l component=scheduler

# Database
kubectl get pods -n floodsight -l app=postgres
```

---

## 💡 Common Tasks

### Check If Forecasts Are Updating
```bash
# Get latest forecast timestamp
curl -s https://shoe-mere-livestock-mild.trycloudflare.com/v1/forecasts | \
  jq -r '.[0] | "Station: \(.station_name), Latest: \(.forecast_timestamp)"'

# Check scheduler logs
kubectl logs -f -l component=scheduler -n floodsight --tail=50
```

### Check Active Alerts
```bash
# In browser
https://lab-grounds-super-behavioral.trycloudflare.com

# Via API
curl https://shoe-mere-livestock-mild.trycloudflare.com/v1/alerts | jq
```

### Monitor Backend Health
```bash
# Quick health check
curl https://shoe-mere-livestock-mild.trycloudflare.com/v1/health | jq

# Metrics (Prometheus format)
curl http://192.168.178.50:30636/metrics
```

---

## 🆘 Troubleshooting

### Frontend Not Loading
1. Check if dev server is running:
   ```bash
   ps aux | grep vite
   ```
2. Check logs:
   ```bash
   tail -f /tmp/frontend-dev.log
   ```
3. Restart:
   ```bash
   pkill -f vite
   cd /home/lenovo/scrimba/floodsight
   npm run dev -- --host 0.0.0.0 --port 8080
   ```

### Backend Not Responding
1. Check pods:
   ```bash
   kubectl get pods -n floodsight
   ```
2. Check logs:
   ```bash
   kubectl logs -l component=backend -n floodsight --tail=50
   ```
3. Restart:
   ```bash
   kubectl rollout restart deployment floodsight-backend -n floodsight
   ```

### Cloudflare Tunnel Not Working
1. Check if running:
   ```bash
   ps aux | grep cloudflared
   ```
2. View tunnel logs:
   ```bash
   cat /tmp/cloudflare-frontend.log
   cat /tmp/cloudflare-tunnel.log
   ```
3. Restart:
   ```bash
   pkill cloudflared
   # Then run the restart commands from "Restart Services" section above
   ```

### No Data / Empty Forecasts
1. Check if scheduler is running:
   ```bash
   kubectl get pods -n floodsight -l component=scheduler
   ```
2. Check scheduler logs:
   ```bash
   kubectl logs -l component=scheduler -n floodsight --tail=100
   ```
3. Manually trigger ingestion:
   ```bash
   kubectl exec -n floodsight deploy/floodsight-scheduler -- \
     python -m app.workers.flows run
   ```

---

## 📚 Additional Documentation

- **VERCEL_TROUBLESHOOTING.md** - Vercel-specific issues
- **REAL_GLOFAS_SUCCESS.md** - Real data ingestion details
- **K8S_SUCCESS.md** - Kubernetes deployment details
- **TROUBLESHOOTING.md** - General troubleshooting guide

---

## 🎯 Summary

**Your FloodSight system is fully operational!**

✅ **Frontend Dashboard:**
   - Public: https://lab-grounds-super-behavioral.trycloudflare.com
   - Local: http://192.168.178.50:8080

✅ **Backend API:**
   - Public: https://shoe-mere-livestock-mild.trycloudflare.com
   - Local: http://192.168.178.50:30636

✅ **Data Source:**
   - Real ECMWF GloFAS forecasts
   - Updated every hour
   - 5 European monitoring stations
   - Up to 10 days ahead

✅ **Infrastructure:**
   - Running on Raspberry Pi 5
   - Kubernetes (K3s) cluster
   - PostgreSQL + PostGIS database
   - Cloudflare tunnels for public access

**Everything is running and accessible! 🌊🎉**

