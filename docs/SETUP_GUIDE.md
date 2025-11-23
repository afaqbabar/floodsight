# FloodSight Setup Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Docker (optional)
- Kubernetes cluster (for production)

## 📦 Frontend Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your values
nano .env
```

Required environment variables:
```bash
# API Configuration
VITE_API_BASE_URL=https://your-api-domain.com/v1

# Map Configuration
VITE_MAP_PROVIDER=openstreetmap
VITE_MAP_DEFAULT_LAT=51.5074
VITE_MAP_DEFAULT_LNG=-0.1278
VITE_MAP_DEFAULT_ZOOM=11

# Feature Flags
VITE_ENABLE_ALERTS=true
VITE_ENABLE_FORECASTING=true
VITE_ENABLE_HISTORICAL_DATA=true
```

### 3. Run Development Server
```bash
npm run dev
```

### 4. Build for Production
```bash
npm run build
```

## 🐍 Backend Setup

### 1. Create Virtual Environment
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your values
nano .env
```

Required environment variables:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/floodsight

# Security (IMPORTANT: Change these!)
SECRET_KEY=your-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
BACKEND_CORS_ORIGINS=["http://localhost:5173","https://your-frontend-domain.com"]

# ECMWF/GloFAS (Optional - for real flood data)
CDS_API_KEY=your-ecmwf-api-key
CDS_API_EMAIL=your-email@example.com
```

### 4. Setup Database
```bash
# Create database
createdb floodsight

# Run migrations (if using Alembic)
alembic upgrade head

# Or initialize with sample data
python -m app.db.init_db
```

### 5. Run Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## 🔐 Security Setup

### Generate Secure Secrets

#### For SECRET_KEY (Python)
```python
import secrets
print(secrets.token_urlsafe(32))
```

#### For SESSION_SECRET (Node.js)
```javascript
require('crypto').randomBytes(32).toString('hex')
```

### Important Security Notes

1. **Never commit `.env` files** to git
2. **Always use strong, random secrets** in production
3. **Rotate secrets regularly** (every 90 days recommended)
4. **Use environment-specific secrets** (different for dev/staging/prod)
5. **Enable HTTPS** in production (required for secure cookies)

## 🐳 Docker Setup

### Build Images
```bash
# Frontend
docker build -f docker/Dockerfile.nginx -t floodsight-frontend .

# Backend
docker build -f backend/Dockerfile -t floodsight-backend ./backend
```

### Run with Docker Compose
```bash
cd backend
docker-compose up -d
```

## ☸️ Kubernetes Setup

### 1. Create Namespace
```bash
kubectl create namespace floodsight
```

### 2. Create Secrets
```bash
# Backend secrets
kubectl create secret generic floodsight-backend-secrets \
  --from-literal=DATABASE_URL='postgresql+asyncpg://user:pass@db:5432/floodsight' \
  --from-literal=SECRET_KEY='your-secret-key-here' \
  --from-literal=CDS_API_KEY='your-ecmwf-api-key' \
  --from-literal=CDS_API_EMAIL='your-email@example.com' \
  -n floodsight

# Docker registry credentials (for private images)
kubectl create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=your-github-username \
  --docker-password=your-github-token \
  -n floodsight
```

### 3. Deploy Application
```bash
# Using Kustomize
kubectl apply -k deploy/k8s/base

# Or using kubectl
kubectl apply -f deploy/k8s/base/
```

### 4. Verify Deployment
```bash
# Check pods
kubectl get pods -n floodsight

# Check services
kubectl get svc -n floodsight

# Check logs
kubectl logs -f deployment/floodsight-backend -n floodsight
```

## 🌐 Cloudflare Tunnel Setup (Optional)

For exposing your local backend to the internet:

### 1. Install cloudflared
```bash
# Download from https://github.com/cloudflare/cloudflared/releases
# Or use package manager:
sudo apt install cloudflared  # Debian/Ubuntu
brew install cloudflared       # macOS
```

### 2. Create Named Tunnel
```bash
# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create floodsight

# Get tunnel ID
cloudflared tunnel list
```

### 3. Configure Tunnel
```bash
# Create config file
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml <<EOF
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/user/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: api.your-domain.com
    service: http://localhost:8080
  - service: http_status:404
EOF
```

### 4. Run Tunnel as Service
```bash
# Install as systemd service
sudo cloudflared service install

# Start service
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Check status
sudo systemctl status cloudflared
```

See [docs/CLOUDFLARE_TUNNEL_SETUP.md](./CLOUDFLARE_TUNNEL_SETUP.md) for detailed instructions.

## 🔧 Vercel Deployment

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Configure Project
```bash
# Link to existing project
vercel link

# Or create new project
vercel
```

### 4. Set Environment Variables
```bash
vercel env add VITE_API_BASE_URL production
# Enter your API URL when prompted
```

### 5. Deploy
```bash
# Build and deploy
npm run build
vercel --prod
```

## 📊 Monitoring & Observability

### Prometheus Metrics
Backend exposes Prometheus metrics at `/metrics`:
```bash
curl http://localhost:8080/metrics
```

### Health Checks
```bash
# Backend health
curl http://localhost:8080/v1/health

# Frontend health
curl http://localhost:5173/health.html
```

### Logs
```bash
# Backend logs (Docker)
docker logs floodsight-backend -f

# Backend logs (Kubernetes)
kubectl logs -f deployment/floodsight-backend -n floodsight

# Frontend logs (Vercel)
vercel logs
```

## 🧪 Testing

### Run Tests
```bash
# Frontend tests
npm test

# Backend tests
cd backend
pytest

# E2E tests
npm run test:e2e
```

### Run Linting
```bash
# Frontend
npm run lint

# Backend
cd backend
ruff check .
black --check .
```

## 🆘 Troubleshooting

### Common Issues

#### "API endpoint not configured"
- Check `VITE_API_BASE_URL` is set correctly
- Rebuild frontend after changing environment variables
- Verify API is accessible from frontend

#### "Database connection failed"
- Check `DATABASE_URL` format
- Verify PostgreSQL is running
- Check network connectivity

#### "CORS error"
- Add frontend URL to `BACKEND_CORS_ORIGINS`
- Restart backend after changing CORS settings
- Check browser console for exact error

#### "Cloudflare tunnel not working"
- Check tunnel is running: `sudo systemctl status cloudflared`
- Verify tunnel config: `cat ~/.cloudflared/config.yml`
- Check tunnel logs: `sudo journalctl -u cloudflared -f`

### Get Help
- [GitHub Issues](https://github.com/afaqbabar/floodsight/issues)
- [Documentation](./README.md)
- [Security Policy](../SECURITY.md)

## 📚 Additional Resources

- [Architecture Overview](./REPOSITORY_STRUCTURE.md)
- [API Documentation](../backend/README.md)
- [Deployment Strategy](./deployment/DEPLOYMENT_STRATEGY.md)
- [Security Best Practices](./.github/SECURITY_CHECKLIST.md)

