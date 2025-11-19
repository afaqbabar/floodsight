# 🚀 FloodSight - Deployment Quick Start

Quick reference for deploying FloodSight frontend and backend.

---

## 📦 What You Have

### Frontend (Already Deployed ✅)

- **Platform:** Vercel
- **URL:** https://floodsight.vercel.app
- **Status:** ✅ Live
- **Tech:** Next.js + Vite + Leaflet maps

### Backend (Ready to Deploy 🎯)

- **Platform:** K8s/K3s (Raspberry Pi)
- **URL:** https://api.floodsight.com (to be configured)
- **Status:** 🟡 Ready for deployment
- **Tech:** FastAPI + PostgreSQL + APScheduler

---

## 🏃 Quick Deploy Commands

### Option 1: Local Development (Docker)

```bash
# Start backend locally
cd backend
docker compose up -d

# Run migrations
docker compose exec api alembic upgrade head

# Seed sample data
docker compose exec api python -m app.services.seed

# Test API
curl http://localhost:8080/v1/health
open http://localhost:8080/docs

# Trigger ingestion (generates fake data)
curl -X POST http://localhost:8080/v1/forecasts/ingest-dev

# View alerts
curl http://localhost:8080/v1/alerts
```

### Option 2: K8s/K3s Deployment

```bash
# 1. Configure secrets
cp deploy/k8s/base/backend-secrets.yaml.example deploy/k8s/base/backend-secrets.yaml
nano deploy/k8s/base/backend-secrets.yaml
# Fill in DATABASE_URL and other secrets

# 2. Apply secrets
kubectl apply -f deploy/k8s/base/backend-secrets.yaml

# 3. Deploy backend
kubectl apply -k deploy/k8s/base/

# 4. Wait for pods
kubectl wait --for=condition=ready pod -l component=backend --timeout=300s

# 5. Run migrations
kubectl exec -it deployment/floodsight-backend -- alembic upgrade head

# 6. Seed data
kubectl exec -it deployment/floodsight-backend -- python -m app.services.seed

# 7. Test
kubectl port-forward svc/floodsight-backend 8080:8080
curl http://localhost:8080/v1/health
```

### Option 3: Production (with DNS)

```bash
# 1. Deploy to K8s (see Option 2)

# 2. Get LoadBalancer IP
kubectl get svc floodsight-backend-external

# 3. Configure DNS
# Add A record: api.floodsight.com -> <LOADBALANCER_IP>

# 4. Wait for TLS certificate (cert-manager)
kubectl get certificate -n floodsight

# 5. Test production API
curl https://api.floodsight.com/v1/health
open https://api.floodsight.com/docs
```

---

## 🔧 Configuration Checklist

### Required Configuration

- [ ] **Database URL** - PostgreSQL connection string

  ```
  postgresql+asyncpg://user:pass@host:5432/floodsight
  ```

- [ ] **CORS Origins** - Frontend URLs

  ```json
  ["https://floodsight.vercel.app", "https://floodsight.com"]
  ```

- [ ] **DNS Records**
  ```
  api.floodsight.com -> <K8s-Ingress-IP>
  ```

### Optional Configuration

- [ ] **ECMWF CDS API Key** - For real GloFAS data
  - Register: https://cds.climate.copernicus.eu/
  - Add to secrets: `cds-api-key`

- [ ] **Supabase JWT** - For authentication
  - Get from: https://app.supabase.com
  - Add to secrets: `supabase-jwks-url`

- [ ] **Email Notifications** - SMTP credentials
  - Add to secrets: `smtp-host`, `smtp-user`, `smtp-password`

- [ ] **SMS Notifications** - Twilio credentials
  - Add to secrets: `twilio-account-sid`, `twilio-auth-token`

---

## 🧪 Testing the Full Stack

### 1. Test Backend Health

```bash
curl https://api.floodsight.com/v1/health
# Should return: {"status": "ok", "database": "connected"}
```

### 2. Test Frontend

```bash
open https://floodsight.vercel.app
# Should show map with stations
```

### 3. Test Integration

```bash
# Ingest fake data
curl -X POST https://api.floodsight.com/v1/forecasts/ingest-dev

# Compute alerts
curl -X POST https://api.floodsight.com/v1/alerts/compute

# Check alerts in API
curl https://api.floodsight.com/v1/alerts

# Check alerts in frontend
open https://floodsight.vercel.app/dashboard
```

### 4. Test Real Data (if CDS API configured)

```bash
# Trigger real GloFAS ingestion
curl -X POST https://api.floodsight.com/v1/forecasts/ingest

# Check logs
kubectl logs -l component=backend --tail=100
```

---

## 📊 Monitoring

### Check System Status

```bash
# Backend pods
kubectl get pods -l component=backend

# Backend logs
kubectl logs -l component=backend -f

# Scheduler logs
kubectl logs -l component=scheduler -f

# Metrics
curl https://api.floodsight.com/metrics

# Resource usage
kubectl top pods
```

### View in Grafana (if configured)

1. **API Metrics:** Request rate, latency, errors
2. **Database:** Connection pool, query times
3. **Ingestion:** Success rate, data volume
4. **Alerts:** Alert counts by level

---

## 🔐 Security Checklist

- [ ] Use HTTPS everywhere (TLS certificates)
- [ ] Store secrets in K8s Secrets (never in git)
- [ ] Enable CORS only for trusted origins
- [ ] Configure rate limiting (100 RPS default)
- [ ] Use non-root containers
- [ ] Enable network policies
- [ ] Scan images with Trivy (automated in CI)
- [ ] Keep dependencies updated (Dependabot)
- [ ] Monitor security advisories

---

## 🆘 Troubleshooting

### Backend won't start

```bash
kubectl describe pod -l component=backend
kubectl logs -l component=backend
# Common issues: database connection, missing secrets
```

### Database connection failed

```bash
# Test from pod
kubectl exec -it deployment/floodsight-backend -- \
  python -c "import asyncio; from app.db.session import init_db; asyncio.run(init_db())"
```

### Ingestion not working

```bash
# Check scheduler logs
kubectl logs -l component=scheduler -f

# Manually trigger
curl -X POST https://api.floodsight.com/v1/forecasts/ingest-dev
```

### Frontend can't reach API

- Check CORS configuration in `backend-configmap.yaml`
- Verify `vercel.json` has API rewrites
- Check DNS: `api.floodsight.com` resolves correctly
- Test directly: `curl https://api.floodsight.com/v1/health`

---

## 📚 Documentation

- **Backend README:** `backend/README.md`
- **K8s Deployment Guide:** `deploy/k8s/README_BACKEND.md`
- **Phase C Summary:** `docs/PHASE_C_COMPLETE.md`
- **API Docs:** https://api.floodsight.com/docs
- **Development Prompt:** `docs/DEVELOPMENT_PROMPT.md`

---

## 🎯 Next Steps

1. **Deploy backend to K3s** (follow Option 3 above)
2. **Configure DNS** for api.floodsight.com
3. **Add ECMWF CDS API key** for real data
4. **Set up monitoring** (Prometheus + Grafana)
5. **Configure notifications** (email, SMS, webhooks)
6. **Test end-to-end** data flow
7. **Monitor and iterate** 🚀

---

**🌊 Happy Deploying! May your servers stay dry and your alerts be timely! 🔔**
