# Vercel Frontend Integration Guide

**Goal**: Connect your Vercel frontend to the FloodSight backend API running on Raspberry Pi

---

## 🚀 Option 1: ngrok Tunnel (Quick Testing) ⭐ Recommended

**Best for**: Development, testing, demos  
**Pros**: Fast setup, HTTPS included, no DNS needed  
**Cons**: URL changes on restart (unless paid plan)

### Step 1: Get ngrok Auth Token

1. **Visit**: https://dashboard.ngrok.com/signup
2. **Sign up** or **log in**
3. **Copy your authtoken** from: https://dashboard.ngrok.com/get-started/your-authtoken

### Step 2: Configure ngrok

```bash
# On your Raspberry Pi
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Step 3: Start ngrok Tunnel

```bash
# Expose your backend API
ngrok http 192.168.178.50:30636
```

You'll see output like:

```
Session Status                online
Forwarding                    https://abc123.ngrok-free.app -> http://192.168.178.50:30636
```

**Copy that HTTPS URL!** (e.g., `https://abc123.ngrok-free.app`)

### Step 4: Update Vercel Environment Variables

1. **Visit**: https://vercel.com/your-project/settings/environment-variables

2. **Add/Update**:

   ```
   Variable Name: VITE_API_URL
   Value: https://abc123.ngrok-free.app
   Environment: Production
   ```

   Or if your frontend uses `NEXT_PUBLIC_`:

   ```
   Variable Name: NEXT_PUBLIC_API_URL
   Value: https://abc123.ngrok-free.app
   Environment: Production
   ```

3. **Redeploy** your frontend:
   - Go to "Deployments" tab
   - Click "Redeploy" on the latest deployment

### Step 5: Test the Connection

Visit your Vercel app and check the browser console:

```javascript
// In browser console
fetch('https://your-vercel-app.vercel.app/api/v1/health')
  .then((r) => r.json())
  .then(console.log);
```

Expected response:

```json
{
  "status": "ok",
  "app": "FloodSight Backend API",
  "version": "0.1.0",
  "database": "connected"
}
```

---

## 🌐 Option 2: Cloudflare Tunnel (Stable Free Solution)

**Best for**: Long-term development, stable URL  
**Pros**: Free, stable URL, HTTPS included, no port forwarding  
**Cons**: Slightly more setup

### Step 1: Install Cloudflare Tunnel

```bash
# On your Raspberry Pi
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
```

### Step 2: Authenticate

```bash
cloudflared tunnel login
```

This opens a browser - select your domain.

### Step 3: Create Tunnel

```bash
cloudflared tunnel create floodsight-api
```

Copy the tunnel ID shown.

### Step 4: Configure Tunnel

```bash
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/lenovo/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: api.yourdomain.com
    service: http://192.168.178.50:30636
  - service: http_status:404
EOF
```

### Step 5: Create DNS Record

```bash
cloudflared tunnel route dns floodsight-api api.yourdomain.com
```

### Step 6: Run Tunnel

```bash
cloudflared tunnel run floodsight-api
```

Or as a service:

```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### Step 7: Update Vercel

Add environment variable:

```
VITE_API_URL=https://api.yourdomain.com
```

---

## 🏠 Option 3: Port Forwarding + Dynamic DNS (Production)

**Best for**: Production deployment  
**Pros**: Full control, own domain  
**Cons**: Requires router configuration

### Step 1: Configure Port Forwarding

On your router:

- External Port: 443
- Internal IP: 192.168.178.50
- Internal Port: 30636
- Protocol: TCP

### Step 2: Setup Dynamic DNS

Use a service like:

- **DuckDNS**: https://www.duckdns.org/ (Free)
- **No-IP**: https://www.noip.com/ (Free tier)
- **Dynu**: https://www.dynu.com/ (Free)

Create a hostname like: `floodsight.duckdns.org`

### Step 3: SSL Certificate

Install Cert-Manager on K3s:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

Or use Cloudflare SSL (easier).

### Step 4: Update Vercel

```
VITE_API_URL=https://floodsight.duckdns.org
```

---

## 🔧 Frontend Code Updates

### React/Vite Example

**1. Create API Client** (`src/lib/api.ts`):

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export const api = {
  async getStations() {
    const response = await fetch(`${API_BASE_URL}/v1/stations`);
    if (!response.ok) throw new Error('Failed to fetch stations');
    return response.json();
  },

  async getForecasts(params?: { station_id?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.station_id) query.append('station_id', params.station_id.toString());
    if (params?.limit) query.append('limit', params.limit.toString());

    const response = await fetch(`${API_BASE_URL}/v1/forecasts?${query}`);
    if (!response.ok) throw new Error('Failed to fetch forecasts');
    return response.json();
  },

  async getAlerts() {
    const response = await fetch(`${API_BASE_URL}/v1/alerts`);
    if (!response.ok) throw new Error('Failed to fetch alerts');
    return response.json();
  },

  async triggerIngestion() {
    const response = await fetch(`${API_BASE_URL}/v1/forecasts/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    if (!response.ok) throw new Error('Failed to trigger ingestion');
    return response.json();
  },
};
```

**2. Usage in Component**:

```typescript
import { useEffect, useState } from 'react';
import { api } from './lib/api';

function Dashboard() {
  const [stations, setStations] = useState([]);
  const [forecasts, setForecasts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [stationsData, forecastsData] = await Promise.all([
          api.getStations(),
          api.getForecasts({ limit: 50 }),
        ]);
        setStations(stationsData);
        setForecasts(forecastsData);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>FloodSight Dashboard</h1>
      <div>
        <h2>Stations ({stations.length})</h2>
        <ul>
          {stations.map(station => (
            <li key={station.id}>
              {station.name} - {station.lat}°N, {station.lon}°E
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h2>Recent Forecasts ({forecasts.length})</h2>
        <ul>
          {forecasts.slice(0, 10).map((forecast, i) => (
            <li key={i}>
              Discharge: {forecast.discharge_m3s} m³/s
              (Lead: {forecast.lead_hours}h)
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Dashboard;
```

### Next.js Example

**API Route** (`pages/api/stations.ts`):

```typescript
import type { NextApiRequest, NextApiResponse } from 'next';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const response = await fetch(`${API_BASE_URL}/v1/stations`);
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch stations' });
  }
}
```

---

## 🧪 Testing Checklist

### 1. Test Backend Connectivity

```bash
# From your local machine
curl https://your-ngrok-url.ngrok-free.app/v1/health

# Expected response:
{
  "status": "ok",
  "app": "FloodSight Backend API",
  "version": "0.1.0",
  "environment": "production",
  "database": "connected"
}
```

### 2. Test CORS

```javascript
// In browser console on your Vercel app
fetch('https://your-ngrok-url.ngrok-free.app/v1/stations')
  .then((r) => r.json())
  .then(console.log)
  .catch(console.error);
```

If you see CORS errors, the backend CORS is already configured for:

- `https://floodsight.vercel.app`
- `https://floodsight.com`
- `http://localhost:3000`
- `http://localhost:5173`

Add your actual Vercel URL if different:

```bash
kubectl edit configmap floodsight-backend-config -n floodsight

# Add your URL to BACKEND_CORS_ORIGINS:
BACKEND_CORS_ORIGINS: '["https://your-app.vercel.app","https://floodsight.vercel.app"]'

# Restart backend
kubectl rollout restart deployment/floodsight-backend -n floodsight
```

### 3. Test API Endpoints

```javascript
// Stations
fetch('https://your-url/v1/stations')
  .then((r) => r.json())
  .then(console.log);

// Forecasts
fetch('https://your-url/v1/forecasts?limit=10')
  .then((r) => r.json())
  .then(console.log);

// Alerts
fetch('https://your-url/v1/alerts')
  .then((r) => r.json())
  .then(console.log);

// Health
fetch('https://your-url/v1/health')
  .then((r) => r.json())
  .then(console.log);
```

### 4. Test Real-Time Updates

```javascript
// Trigger ingestion
fetch('https://your-url/v1/forecasts/ingest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({})
}).then(r => r.json()).then(console.log)

// Should return:
{
  "status": "success",
  "message": "Ingested X forecasts (real)",
  "forecasts_created": X,
  "mode": "real"
}
```

---

## 🔐 Security Considerations

### For Development (ngrok)

✅ **Already Secure**: HTTPS included, temporary URL  
⚠️ **Warning**: URL changes on restart  
💡 **Tip**: Use paid ngrok plan for stable subdomain

### For Production

1. **Enable Rate Limiting**: Already configured in backend
2. **Use HTTPS**: Required (ngrok/Cloudflare provide this)
3. **API Authentication**:
   ```bash
   # Enable Supabase JWT in ConfigMap
   kubectl edit secret floodsight-backend-secrets -n floodsight
   # Add: supabase-jwt-secret: your-secret-here
   ```
4. **Monitoring**:
   ```bash
   # Watch API usage
   kubectl logs -f -l component=backend -n floodsight
   ```

---

## 📊 Monitoring & Debugging

### Check Backend Logs

```bash
# Real-time logs
kubectl logs -f -l component=backend -n floodsight

# Recent errors
kubectl logs -l component=backend -n floodsight --tail=100 | grep ERROR
```

### Check ngrok Status

```bash
# Visit ngrok dashboard
http://127.0.0.1:4040

# Or check ngrok logs
ngrok http 192.168.178.50:30636 --log stdout
```

### Test from Vercel Build Logs

In your frontend build:

```javascript
// Add to your build script
console.log('API URL:', process.env.VITE_API_URL);
fetch(process.env.VITE_API_URL + '/v1/health')
  .then((r) => r.json())
  .then((data) => console.log('Backend health:', data))
  .catch((err) => console.error('Backend connection failed:', err));
```

---

## 🚨 Troubleshooting

### Issue: "Failed to fetch" or CORS error

**Solution 1**: Add your Vercel URL to CORS whitelist

```bash
kubectl edit configmap floodsight-backend-config -n floodsight
# Add your Vercel URL to BACKEND_CORS_ORIGINS
kubectl rollout restart deployment/floodsight-backend -n floodsight
```

**Solution 2**: Check ngrok is running

```bash
# Make sure ngrok tunnel is active
curl https://your-ngrok-url.ngrok-free.app/v1/health
```

### Issue: "ngrok URL changes every time"

**Solution**: Use ngrok paid plan for static subdomain, or switch to Cloudflare Tunnel (free static URL)

### Issue: "Connection refused"

**Solution**: Check backend is running

```bash
kubectl get pods -n floodsight
curl http://192.168.178.50:30636/v1/health
```

### Issue: "404 Not Found"

**Solution**: Check API path

```bash
# Correct paths:
/v1/health ✅
/v1/stations ✅
/v1/forecasts ✅

# Wrong paths:
/api/v1/health ❌ (unless using vercel.json proxy)
/health ❌
```

---

## 📱 Quick Start Script

Save this as `start-ngrok.sh`:

```bash
#!/bin/bash

echo "🚀 Starting ngrok tunnel for FloodSight API..."
echo ""
echo "Make sure your backend is running:"
echo "  kubectl get pods -n floodsight"
echo ""
echo "Starting ngrok..."
echo ""

ngrok http 192.168.178.50:30636 \
  --domain=YOUR_STATIC_DOMAIN.ngrok-free.app \
  --log=stdout

# Without static domain (free):
# ngrok http 192.168.178.50:30636
```

Run it:

```bash
chmod +x start-ngrok.sh
./start-ngrok.sh
```

---

## ✅ Final Checklist

Before going to production:

- [ ] Backend running and healthy (`/v1/health` returns 200)
- [ ] Real GloFAS data ingesting (`mode: "real"`)
- [ ] ngrok/Cloudflare tunnel running
- [ ] Vercel environment variables set
- [ ] Frontend redeployed
- [ ] CORS configured for your Vercel domain
- [ ] API endpoints tested from browser
- [ ] Error handling implemented in frontend
- [ ] Loading states implemented
- [ ] API retry logic (for intermittent failures)

---

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ Your Vercel app loads without errors
2. ✅ Browser console shows successful API calls
3. ✅ Station data appears on your map/list
4. ✅ Forecast data displays correctly
5. ✅ Real-time updates work
6. ✅ No CORS errors in console

---

**Your FloodSight backend is ready for frontend integration!** 🌊🚀

For support, check:

- Backend logs: `kubectl logs -f -l component=backend -n floodsight`
- ngrok dashboard: http://127.0.0.1:4040
- API documentation: http://192.168.178.50:30636/docs
