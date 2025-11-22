# Expose Pi Backend to Vercel Frontend

This guide shows how to make your Pi backend accessible to the Vercel frontend so it can display real data.

## Current Setup

✅ **Pi Backend**: http://192.168.178.50:8080 (5 stations with real data)
✅ **Vercel Frontend**: https://floodsight.vercel.app
❌ **Problem**: Vercel can't reach your local Pi

## Solution: Cloudflare Tunnel (Recommended)

### Why Cloudflare Tunnel?
- ✅ **Free** (no cost)
- ✅ **Secure** (no open ports, encrypted)
- ✅ **Easy** (one command)
- ✅ **Reliable** (enterprise-grade)
- ✅ **No router config** needed

### Option A: Quick Tunnel (Temporary - for testing)

**On your Pi:**

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared-linux-arm64.deb

# Start tunnel (gives you a random URL)
cloudflared tunnel --url http://localhost:8080
```

**Output:**
```
Your quick tunnel has been created! Visit it at:
https://abc-xyz-random-123.trycloudflare.com
```

**Copy that URL!**

### Update Frontend

1. Copy the URL from cloudflared (e.g., `https://abc-xyz-random-123.trycloudflare.com`)

2. Update `public/assets/js/api-service.js`:

```javascript
// Line 30 - Replace with your tunnel URL
return 'https://abc-xyz-random-123.trycloudflare.com/v1';
```

3. Commit and push:

```bash
git add public/assets/js/api-service.js
git commit -m "feat: connect Vercel to Pi backend via Cloudflare Tunnel"
git push origin main
```

4. Wait 2 minutes for Vercel to deploy

5. Test:
```bash
curl https://floodsight.vercel.app/api/healthz
# Visit: https://floodsight.vercel.app/dashboard-figma.html
```

### Test It Works

```bash
# From any computer, test the tunnel
curl https://abc-xyz-random-123.trycloudflare.com/v1/health

# Should return:
# {"status":"ok","app":"FloodSight API","database":"connected"}
```

### ⚠️ Quick Tunnel Limitations

- URL changes every time you restart
- Not suitable for production
- Good for testing only

---

## Option B: Named Tunnel (Permanent - Recommended)

For a permanent setup that survives restarts:

### 1. Create Named Tunnel

```bash
# Login to Cloudflare (opens browser)
cloudflared tunnel login

# Create named tunnel
cloudflared tunnel create floodsight-api

# This creates:
# - Tunnel ID and credentials
# - ~/.cloudflared/[tunnel-id].json
```

### 2. Configure Tunnel

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: floodsight-api
credentials-file: /home/lenovo/.cloudflared/[your-tunnel-id].json

ingress:
  - hostname: floodsight-api.yourdomain.com
    service: http://localhost:8080
  - service: http_status:404
```

### 3. Route DNS

```bash
# Add DNS record (replace with your domain)
cloudflared tunnel route dns floodsight-api floodsight-api.yourdomain.com
```

### 4. Run Tunnel

```bash
# Run tunnel
cloudflared tunnel run floodsight-api

# Or install as service (runs on boot)
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### 5. Update Frontend

Use your custom domain:

```javascript
// public/assets/js/api-service.js
return 'https://floodsight-api.yourdomain.com/v1';
```

---

## Alternative: ngrok (Quick Alternative)

If Cloudflare doesn't work:

```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz
tar xvzf ngrok-v3-stable-linux-arm64.tgz
sudo mv ngrok /usr/local/bin/

# Sign up at https://ngrok.com (free)
# Get auth token from dashboard

# Authenticate
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Start tunnel
ngrok http 8080
```

You'll get a URL like: `https://abc123.ngrok.io`

Update frontend:
```javascript
return 'https://abc123.ngrok.io/v1';
```

---

## Comparison

| Method | Cost | Permanence | Setup Time | Security |
|--------|------|------------|------------|----------|
| **Cloudflare Quick** | Free | Temporary | 1 min | High |
| **Cloudflare Named** | Free | Permanent | 5 min | High |
| **ngrok Free** | Free | Temporary | 2 min | Medium |
| **ngrok Paid** | $8/mo | Permanent | 2 min | Medium |
| **Port Forward** | Free | Permanent | 10 min | **Low** ⚠️ |

---

## Test Your Setup

Once tunnel is running:

### 1. Test Tunnel Directly

```bash
# Should return API health
curl https://your-tunnel-url/v1/health

# Should return stations
curl https://your-tunnel-url/v1/stations
```

### 2. Test Vercel Dashboard

Visit: https://floodsight.vercel.app/dashboard-figma.html

You should see:
- ✅ Map with 5 stations (not London demo)
- ✅ Filters populated with real countries
- ✅ Forecast data loading
- ✅ Alerts displayed

### 3. Check Browser Console

Press F12 → Console tab

Look for:
```
🌐 Connecting to API: https://your-tunnel-url/v1
✅ API connected successfully
```

---

## Troubleshooting

### Tunnel Won't Start

```bash
# Check if port 8080 is in use
sudo lsof -i :8080

# Restart backend
cd /home/lenovo/scrimba/floodsight/backend
docker compose restart api
```

### CORS Errors in Browser

The backend already allows CORS from Vercel. If you see errors:

```bash
# Check backend logs
docker compose logs api | grep CORS
```

### Vercel Still Shows Demo Data

1. **Clear browser cache** (Ctrl+Shift+R)
2. **Check API URL** in browser console
3. **Verify tunnel** is running: `curl https://your-tunnel-url/v1/health`

### Tunnel Disconnects

For permanent tunnel:
```bash
# Install as systemd service
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared

# Check status
sudo systemctl status cloudflared
```

---

## Keep Tunnel Running

### Quick Tunnel (for testing)

Run in `screen` or `tmux` so it persists:

```bash
# Install screen
sudo apt-get install screen

# Start screen session
screen -S tunnel

# Run tunnel
cloudflared tunnel --url http://localhost:8080

# Detach: Press Ctrl+A then D

# Reattach later
screen -r tunnel
```

### Named Tunnel (for production)

Install as system service (auto-starts on boot):

```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

---

## Cost Comparison

| Setup | Monthly Cost |
|-------|--------------|
| **Your current setup** (Pi + Vercel + Cloudflare) | **$0** |
| Fly.io (working backend + DB) | $0 (free tier) |
| Vercel + Railway | ~$5/month |
| Full AWS setup | ~$30+/month |

**Recommendation**: Use Pi + Cloudflare Tunnel. It's free and works perfectly!

---

## Summary

**Fastest way to get real data on Vercel:**

```bash
# 1. On Pi - start tunnel
cloudflared tunnel --url http://localhost:8080

# 2. Copy the URL shown

# 3. Update api-service.js with that URL

# 4. Push to GitHub
git add public/assets/js/api-service.js
git commit -m "feat: use Pi backend via Cloudflare Tunnel"
git push origin main

# 5. Wait 2 min, visit:
# https://floodsight.vercel.app/dashboard-figma.html

# Done! Real data on production! 🎉
```

Your Pi backend has:
- ✅ 5 stations
- ✅ Forecasts
- ✅ Alerts
- ✅ Scheduler running
- ✅ Database with real data

No need to fix Fly.io - your local setup works perfectly!

