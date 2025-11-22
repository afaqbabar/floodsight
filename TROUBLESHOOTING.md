# 🔧 Troubleshooting Guide

## Issue: Docker Compose Building Wrong Service

### Symptom
When running `backend/test-local.sh`, you see:
```
npm error The `npm ci` command can only install with an existing package-lock.json
```

### Root Cause
The script was running from the wrong directory and picking up the root `docker-compose.yaml` (frontend) instead of `backend/docker-compose.yml`.

### ✅ Solution (FIXED)
The script has been updated to automatically change to the backend directory. Now you can run it from anywhere:

```bash
# From anywhere in the project:
./backend/test-local.sh

# Or from root:
cd /home/lenovo/scrimba/floodsight
./backend/test-local.sh
```

### Alternative: Run from Backend Directory
```bash
cd /home/lenovo/scrimba/floodsight/backend
./test-local.sh
```

---

## Issue: Permission Denied

### Symptom
```
bash: ./test-local.sh: Permission denied
```

### Solution
```bash
chmod +x backend/test-local.sh
chmod +x backend/test-glofas-integration.sh
chmod +x backend/test-api-comprehensive.sh
chmod +x backend/monitor-health.sh
chmod +x deploy/k8s/deploy-backend.sh
```

---

## Issue: Docker Not Running

### Symptom
```
Cannot connect to the Docker daemon
```

### Solution
```bash
# Start Docker
sudo systemctl start docker

# Or on macOS/Windows
# Start Docker Desktop application

# Verify Docker is running
docker info
```

---

## Issue: Port Already in Use

### Symptom
```
Error: Bind for 0.0.0.0:8080 failed: port is already allocated
```

### Solution
```bash
# Find what's using port 8080
sudo lsof -i :8080

# Kill the process (replace PID)
sudo kill -9 <PID>

# Or change the port in docker-compose.yml
# Change "8080:8080" to "8081:8080"
```

---

## Issue: Database Connection Failed

### Symptom
```
FATAL: password authentication failed
```

### Solution
```bash
# Reset the database
cd backend
docker compose down -v
docker compose up -d

# Wait for database to be ready
sleep 10

# Run migrations
docker compose exec api alembic upgrade head
```

---

## Issue: Migrations Fail

### Symptom
```
sqlalchemy.exc.ProgrammingError: relation does not exist
```

### Solution
```bash
cd backend

# Reset database and start fresh
docker compose down -v
docker compose up -d

# Wait for DB to be ready
sleep 10

# Run migrations
docker compose exec api alembic upgrade head

# Seed data
docker compose exec api python -m app.services.seed
```

---

## Issue: Backend Container Keeps Restarting

### Symptom
```
STATUS: Restarting (1) 2 seconds ago
```

### Solution
```bash
# Check logs
docker compose logs api

# Common causes:
# 1. Database not ready - wait 30 seconds
# 2. Missing dependencies - rebuild
docker compose up -d --build

# 3. Configuration error - check .env
```

---

## Issue: GloFAS Integration Fails

### Symptom
```
ERROR: CDS API credentials not configured
```

### Solution
```bash
# Option 1: Use fake data (default)
# Just run without CDS credentials, it will use fake data

# Option 2: Configure real data
# 1. Register at https://cds.climate.copernicus.eu/
# 2. Accept GloFAS license
# 3. Get API key (UID:KEY format)
# 4. Add to docker-compose.yml:
nano docker-compose.yml
# Add under api -> environment:
#   - CDS_API_KEY=12345:abcdef-1234-5678-90ab-cdefghijklmn

# 5. Restart
docker compose restart api scheduler
```

---

## Issue: Kubernetes Deployment Fails

### Symptom
```
Error: secrets not found
```

### Solution
```bash
cd deploy/k8s

# Create secrets from template
cp base/backend-secrets.yaml.example base/backend-secrets.yaml

# Edit with your values
nano base/backend-secrets.yaml

# Apply secrets
kubectl apply -f base/backend-secrets.yaml -n floodsight

# Try deployment again
./deploy-backend.sh
```

---

## Issue: Cannot Access API Docs

### Symptom
```
curl: (7) Failed to connect to localhost port 8080
```

### Solution
```bash
# Check if backend is running
docker compose ps

# If not running, start it
cd backend
docker compose up -d

# Wait for startup
sleep 30

# Check health
curl http://localhost:8080/v1/health

# If still not working, check logs
docker compose logs api
```

---

## Issue: Frontend Cannot Connect to Backend

### Symptom
Frontend shows "Connection error" or CORS errors

### Solution

**For Local Development:**
```bash
# 1. Ensure backend is running
curl http://localhost:8080/v1/health

# 2. Check CORS settings in backend/docker-compose.yml
# Should include: http://localhost:3000, http://localhost:5173

# 3. Restart backend if changed
docker compose restart api
```

**For Production:**
```bash
# 1. Check vercel.json has API proxy
cat vercel.json | grep api

# 2. Verify DNS
nslookup api.floodsight.com

# 3. Check ingress
kubectl get ingress -n floodsight

# 4. Check backend service
kubectl get svc -n floodsight
```

---

## Quick Reset (Nuclear Option)

If everything is broken and you want to start fresh:

```bash
cd /home/lenovo/scrimba/floodsight/backend

# Stop and remove everything
docker compose down -v

# Remove all containers, images, volumes
docker system prune -a --volumes -f

# Start fresh
docker compose up -d --build

# Wait for services
sleep 30

# Run migrations
docker compose exec api alembic upgrade head

# Seed data
docker compose exec api python -m app.services.seed

# Test
curl http://localhost:8080/v1/health
```

---

## Verify Installation

Run these commands to verify everything is set up correctly:

```bash
# 1. Check Docker
docker --version
docker compose version

# 2. Check scripts are executable
ls -lh backend/*.sh

# 3. Check backend files exist
ls backend/docker-compose.yml
ls backend/pyproject.toml
ls backend/app/main.py

# 4. Check K8s (if using)
kubectl version --client
kubectl cluster-info

# 5. Test backend locally
cd backend
./test-local.sh
```

---

## Still Having Issues?

1. **Check logs:**
   ```bash
   # Docker Compose
   docker compose logs -f api
   
   # Kubernetes
   kubectl logs -l component=backend -n floodsight
   ```

2. **Verify prerequisites:**
   - Docker installed and running
   - Python 3.11+ (if running locally without Docker)
   - kubectl configured (if using K8s)
   - Sufficient disk space (5GB+)

3. **Review documentation:**
   - `backend/README.md`
   - `deploy/k8s/README_BACKEND.md`
   - `backend/GLOFAS_INTEGRATION_GUIDE.md`

4. **Create a GitHub issue:**
   - Include error logs
   - Include system info (OS, Docker version)
   - Include steps to reproduce

---

## Common Environment Issues

### macOS
```bash
# If Docker Desktop is slow
# Increase resources: Docker Desktop → Settings → Resources
# Recommended: 4 CPUs, 8GB RAM

# If port binding fails
sudo lsof -i :8080
sudo kill -9 <PID>
```

### Linux
```bash
# If Docker permission denied
sudo usermod -aG docker $USER
newgrp docker

# If systemd issues
sudo systemctl enable docker
sudo systemctl start docker
```

### Windows (WSL2)
```bash
# Ensure WSL2 is enabled
wsl --status

# Ensure Docker Desktop is using WSL2 backend
# Docker Desktop → Settings → General → Use WSL2 based engine
```

### Raspberry Pi
```bash
# If out of memory
# Increase swap size in /etc/dphys-swapfile
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048

sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# If ARM compatibility issues
# Ensure using correct image tags (linux/arm64)
```

---

## Success Indicators

You'll know everything is working when:

1. ✅ `docker compose ps` shows all services as "Up"
2. ✅ `curl http://localhost:8080/v1/health` returns `{"status":"ok"}`
3. ✅ `docker compose logs api` shows no errors
4. ✅ `curl http://localhost:8080/v1/stations` returns JSON array
5. ✅ `open http://localhost:8080/docs` shows API documentation

---

**Last Updated:** 2025-11-13  
**Status:** Living Document (updated as issues are discovered)

