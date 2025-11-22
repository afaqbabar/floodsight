# FloodSight Setup on Raspberry Pi

## Quick Setup Guide

### 1. Install Node.js (if not installed)

```bash
# Check if Node.js is installed
node --version

# If not installed, install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### 2. Install Dependencies

```bash
cd /home/lenovo/scrimba/floodsight
npm install
```

### 3. Start Development Server

```bash
# Start dev server (accessible on network)
npm run dev

# The server will be available at:
# - Local: http://localhost:5173
# - Network: http://192.168.178.50:5173
```

### 4. Access from Other Devices

From any device on your network, visit:

```
http://192.168.178.50:5173
```

### 5. Build for Production

```bash
# Build the site
npm run build

# Preview production build
npm run preview
```

### 6. Serve with Simple HTTP Server (Alternative)

If you just want to serve the built site without dev server:

```bash
# Build first
npm run build

# Serve with Python (usually pre-installed on Pi)
cd dist
python3 -m http.server 8080 --bind 0.0.0.0

# Or use a simple HTTP server npm package
npm install -g http-server
http-server dist -p 8080 -a 0.0.0.0
```

Then access at: `http://192.168.178.50:8080`

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 5173
sudo lsof -ti:5173 | xargs sudo kill -9

# Or use a different port
npm run dev -- --port 3000
```

### Permission Issues

```bash
# Fix npm permissions
sudo chown -R $USER:$USER /home/lenovo/scrimba/floodsight/node_modules
```

### Memory Issues (for older Pis)

```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=512"
npm run build
```

### Firewall Issues

```bash
# Check if port is accessible
sudo ufw status

# Allow port 5173 if needed
sudo ufw allow 5173/tcp
```

## Performance Tips for Raspberry Pi

1. **Use production build** instead of dev server for better performance
2. **Close unused applications** to free up RAM
3. **Use swap space** if building is slow
4. **Consider using nginx** for serving static files

## Nginx Setup (Optional - for Production)

```bash
# Install nginx
sudo apt-get update
sudo apt-get install nginx

# Build the site
cd /home/lenovo/scrimba/floodsight
npm run build

# Copy to nginx directory
sudo cp -r dist/* /var/www/html/

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Access at http://192.168.178.50
```

## Auto-start on Boot (Optional)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/floodsight.service
```

Add:

```ini
[Unit]
Description=FloodSight Development Server
After=network.target

[Service]
Type=simple
User=lenovo
WorkingDirectory=/home/lenovo/scrimba/floodsight
ExecStart=/usr/bin/npm run dev
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable floodsight
sudo systemctl start floodsight
```

Check status:

```bash
sudo systemctl status floodsight
```
