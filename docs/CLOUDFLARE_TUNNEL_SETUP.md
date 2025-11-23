# Cloudflare Tunnel Setup for FloodSight

This document explains how the Cloudflare Tunnel is configured to expose the FloodSight backend API publicly.

## Overview

The FloodSight backend runs on a Raspberry Pi in a home network and is not directly accessible from the internet. We use **Cloudflare Tunnel** to provide secure public access to the backend API.

## Current Setup

### Systemd Service

The tunnel runs as a systemd service that starts automatically on boot:

- **Service file**: `/etc/systemd/system/cloudflared-tunnel.service`
- **Log file**: `/var/log/cloudflared-tunnel.log`
- **Backend URL**: `http://localhost:30636` (K3s NodePort)

### Service Management

```bash
# Check status
sudo systemctl status cloudflared-tunnel

# View logs
sudo tail -f /var/log/cloudflared-tunnel.log

# Restart service
sudo systemctl restart cloudflared-tunnel

# Stop service
sudo systemctl stop cloudflared-tunnel

# Start service
sudo systemctl start cloudflared-tunnel
```

## Tunnel URL Changes

⚠️ **Important**: The current setup uses a "quick tunnel" which generates a **random URL each time the service restarts**. This means:

- The URL changes after every Pi reboot
- The URL changes if the tunnel service crashes and restarts
- You must update the CI/CD workflows after each URL change

### Current Tunnel URL

Check the logs to find the current URL:

```bash
sudo grep -Eo "https://[a-z0-9-]+\.trycloudflare\.com" /var/log/cloudflared-tunnel.log | tail -1
```

### Updating After URL Change

Run the helper script to update all configurations:

```bash
cd /home/lenovo/scrimba/floodsight
./scripts/update-tunnel-url.sh
```

Then commit and push the changes:

```bash
git add .github/workflows/ deploy/k8s/base/backend-configmap.yaml
git commit -m "chore: update cloudflare tunnel url"
git push origin main

# Apply backend CORS changes
kubectl apply -f deploy/k8s/base/backend-configmap.yaml
kubectl rollout restart deployment floodsight-backend -n floodsight
```

## Upgrading to Permanent Tunnel (Recommended)

To avoid URL changes, set up a **named tunnel** with a permanent domain:

### Step 1: Authenticate with Cloudflare

```bash
cloudflared tunnel login
```

This opens a browser to log in to your Cloudflare account.

### Step 2: Create a Named Tunnel

```bash
cloudflared tunnel create floodsight-backend
```

This creates a permanent tunnel and saves credentials to `~/.cloudflared/`.

### Step 3: Configure DNS

Add a CNAME record in your Cloudflare DNS:

```bash
cloudflared tunnel route dns floodsight-backend api.floodsight.com
```

### Step 4: Update Service Configuration

Create `/home/lenovo/.cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /home/lenovo/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: api.floodsight.com
    service: http://localhost:30636
  - service: http_status:404
```

### Step 5: Update Systemd Service

Edit `/etc/systemd/system/cloudflared-tunnel.service`:

```ini
[Service]
ExecStart=/usr/local/bin/cloudflared tunnel --config /home/lenovo/.cloudflared/config.yml run floodsight-backend
```

Then restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart cloudflared-tunnel
```

### Step 6: Update CI/CD Workflows

Update all workflows to use `https://api.floodsight.com/v1` instead of the trycloudflare.com URL.

## Troubleshooting

### Tunnel Not Working

1. Check if service is running:
   ```bash
   sudo systemctl status cloudflared-tunnel
   ```

2. Check logs for errors:
   ```bash
   sudo tail -100 /var/log/cloudflared-tunnel.log
   ```

3. Test backend locally:
   ```bash
   curl http://localhost:30636/v1/health
   ```

4. Test tunnel publicly:
   ```bash
   TUNNEL_URL=$(sudo grep -Eo "https://[a-z0-9-]+\.trycloudflare\.com" /var/log/cloudflared-tunnel.log | tail -1)
   curl $TUNNEL_URL/v1/health
   ```

### Backend Not Accessible

1. Check K3s is running:
   ```bash
   sudo systemctl status k3s
   ```

2. Check backend pods:
   ```bash
   kubectl get pods -n floodsight | grep backend
   ```

3. Check backend service:
   ```bash
   kubectl get svc -n floodsight floodsight-backend-external
   ```

### CORS Errors

Make sure the tunnel URL is in the backend CORS configuration:

```bash
kubectl get configmap floodsight-backend-config -n floodsight -o yaml | grep CORS
```

Update if needed:

```bash
kubectl apply -f deploy/k8s/base/backend-configmap.yaml
kubectl rollout restart deployment floodsight-backend -n floodsight
```

## Security Considerations

- The quick tunnel has **no uptime guarantee** and is subject to Cloudflare's terms
- For production use, always use a **named tunnel** with authentication
- Consider implementing rate limiting and API authentication
- Monitor tunnel logs for suspicious activity

## References

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Quick Tunnels](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/do-more-with-tunnels/trycloudflare/)
- [Named Tunnels](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide/)

