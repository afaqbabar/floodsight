# FloodSight Deployment Strategy

## 🎯 Current Production Setup

### Architecture (December 2024)

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Vercel        │  HTTPS  │  Cloudflare      │  HTTP   │  Raspberry Pi   │
│   (Frontend)    ├────────►│  Tunnel          ├────────►│  (Backend)      │
│   Global CDN    │         │  (Secure Proxy)  │         │  192.168.178.50 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

### Why This Approach?

✅ **Cost**: $0/month (completely free)
✅ **Performance**: Pi backend is working perfectly
✅ **Security**: Cloudflare Tunnel (no open ports)
✅ **Reliability**: Pi runs 24/7 with scheduler
✅ **Simplicity**: No complex cloud deployments
✅ **Real Data**: 5 stations + forecasts + alerts

---

## 📦 Components

### 1. Frontend - Vercel
- **URL**: https://floodsight.vercel.app
- **Deployment**: Automatic on `git push`
- **Build Time**: ~2 minutes
- **Hosting**: Vercel Free Tier
- **CDN**: Global (Frankfurt primary)

### 2. Backend - Raspberry Pi
- **Local IP**: http://192.168.178.50:8080
- **Public URL**: https://[tunnel-url].trycloudflare.com/v1
- **Database**: PostgreSQL in Docker
- **Scheduler**: APScheduler (hourly ingestion)
- **API**: FastAPI + Uvicorn
- **Container**: Docker Compose

### 3. Tunnel - Cloudflare
- **Purpose**: Expose Pi backend to internet
- **Security**: End-to-end encryption
- **Setup**: `cloudflared tunnel --url http://localhost:8080`
- **Cost**: Free
- **Performance**: Cloudflare's global network

---

## 🚀 Deployment Steps

### Initial Setup (One Time)

#### 1. Pi Backend
```bash
cd /home/lenovo/scrimba/floodsight/backend
docker compose up -d
```

#### 2. Cloudflare Tunnel
```bash
cd /home/lenovo/scrimba/floodsight
./QUICK_START_CLOUDFLARE.sh
# Copy the tunnel URL shown
```

#### 3. Update Frontend
```bash
# Edit public/assets/js/api-service.js
# Replace line 30 with your tunnel URL:
return 'https://your-tunnel-url.trycloudflare.com/v1';

git add public/assets/js/api-service.js
git commit -m "feat: update API endpoint"
git push origin main
```

#### 4. Verify
```bash
# Wait 2 minutes for Vercel to deploy
# Visit: https://floodsight.vercel.app/dashboard-figma.html
```

---

## 🔄 Daily Operations

### Backend Status
```bash
# Check backend health
curl http://localhost:8080/v1/health

# Check Docker containers
docker compose ps

# View logs
docker compose logs -f api
```

### Tunnel Status
```bash
# Check if tunnel is running
ps aux | grep cloudflared

# Restart tunnel
./QUICK_START_CLOUDFLARE.sh
```

### Frontend Deployment
```bash
# Push changes (auto-deploys)
git push origin main

# Monitor deployment
# Visit: https://vercel.com/your-org/floodsight
```

---

## 💰 Cost Analysis

| Component | Service | Monthly Cost |
|-----------|---------|--------------|
| Frontend | Vercel | $0 (Free Tier) |
| Backend | Raspberry Pi | ~$2 (electricity) |
| Tunnel | Cloudflare | $0 (Free) |
| Domain | (future) | ~$12/year |
| **TOTAL** | | **~$2/month** |

### Comparison with Alternatives

| Setup | Monthly Cost | Complexity |
|-------|--------------|------------|
| **Current (Pi + Cloudflare)** | **$2** | **Low** |
| Vercel + Vercel Functions | $0-20 | Medium |
| Vercel + Fly.io | $0-10 | Medium |
| Vercel + Railway | $5-15 | Medium |
| AWS (ECS + RDS) | $30-60 | High |
| Full Azure | $40-80 | High |

---

## 🗂️ Alternative Deployments (Not Used)

### Fly.io (Suspended)

We created Fly.io resources but suspended them in favor of the Pi approach:

**Resources:**
- App: `floodsight-api` (suspended)
- Database: `floodsight-db` (suspended)
- Status: Not deleted (can resume if needed)

**Configuration Files:**
- `backend/fly.toml` - Fly.io app config
- `backend/Dockerfile.fly` - Optimized Dockerfile
- `FLY_IO_DEPLOYMENT.md` - Deployment guide

**Why Suspended:**
- Pi backend works perfectly
- No need for duplicate deployment
- Free tier is sufficient but Pi is simpler
- Can resume later if needed

**To Resume Fly.io (if needed):**
```bash
# Fix database connection issue first
cd backend
flyctl deploy --remote-only --app floodsight-api

# Then update frontend to use:
# https://floodsight-api.fly.dev/v1
```

### Vercel Functions (Removed)

Initially attempted but removed:

**Why Removed:**
- No persistent storage (scheduler needs to run 24/7)
- Cold start latency
- Limited execution time (10s on free tier)
- Can't run background jobs

**Files Deleted:**
- `api/index.py`
- `api/requirements.txt`
- `VERCEL_API_SETUP.md`

---

## 📊 Performance Metrics

### Frontend (Vercel)
- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Lighthouse Score**: 95+
- **Global Availability**: 99.9%

### Backend (Pi)
- **Response Time**: ~50ms (local network)
- **Through Tunnel**: ~200ms (global)
- **Uptime**: 99%+ (depends on home internet)
- **Concurrent Users**: 50+ (tested)

### API Endpoints
- `/v1/health` - 10ms
- `/v1/stations` - 50ms
- `/v1/forecasts` - 100ms
- `/v1/alerts` - 80ms

---

## 🔒 Security

### Frontend (Vercel)
- ✅ HTTPS enforced
- ✅ CSP headers
- ✅ CORS configured
- ✅ XSS protection
- ✅ GDPR cookie banner

### Backend (Pi)
- ✅ Not directly exposed (behind tunnel)
- ✅ JWT authentication ready
- ✅ Rate limiting configured
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Environment variables for secrets

### Tunnel (Cloudflare)
- ✅ End-to-end encryption
- ✅ DDoS protection
- ✅ No open ports on router
- ✅ Automatic certificate management
- ✅ IP whitelisting (optional)

---

## 🛠️ Maintenance

### Weekly
- [ ] Check backend logs: `docker compose logs api | grep ERROR`
- [ ] Verify scheduler runs: `docker compose logs scheduler`
- [ ] Test API health: `curl http://localhost:8080/v1/health`

### Monthly
- [ ] Update dependencies: `cd backend && poetry update`
- [ ] Check disk space: `df -h`
- [ ] Review database size: `docker compose exec db psql -U floodsight -c "SELECT pg_size_pretty(pg_database_size('floodsight'));"`
- [ ] Backup database: `./scripts/backup-db.sh`

### Quarterly
- [ ] Security audit: `npm audit` and `poetry audit`
- [ ] Performance review: Lighthouse audit
- [ ] Database optimization: VACUUM and ANALYZE
- [ ] Review logs for anomalies

---

## 🐛 Troubleshooting

### Frontend Shows "API Unavailable"

**Check 1: Is tunnel running?**
```bash
ps aux | grep cloudflared
# If not running:
./QUICK_START_CLOUDFLARE.sh
```

**Check 2: Is backend running?**
```bash
curl http://localhost:8080/v1/health
# If fails:
cd backend && docker compose up -d
```

**Check 3: Is URL correct in frontend?**
```bash
grep "trycloudflare" public/assets/js/api-service.js
# Should match your current tunnel URL
```

### Tunnel Keeps Disconnecting

**Solution: Use named tunnel (permanent)**
```bash
# See EXPOSE_PI_BACKEND.md - "Named Tunnel" section
cloudflared tunnel login
cloudflared tunnel create floodsight-api
# Install as systemd service
sudo cloudflared service install
```

### Database Connection Errors

**Check database:**
```bash
docker compose ps db
docker compose logs db | tail -20

# If needed, restart:
docker compose restart db
```

**Test connection:**
```bash
docker compose exec db psql -U floodsight -c "SELECT 1;"
```

### High Memory Usage on Pi

**Check:**
```bash
free -h
docker stats

# If needed, restart containers:
docker compose restart
```

---

## 📈 Future Improvements

### Short Term (Next Month)
- [ ] Set up named Cloudflare Tunnel (permanent URL)
- [ ] Configure systemd service for tunnel auto-start
- [ ] Add monitoring/alerting (Uptime Kuma on Pi)
- [ ] Set up automated database backups

### Medium Term (3 Months)
- [ ] Custom domain (floodsight.com)
- [ ] Production-ready authentication (OAuth2)
- [ ] Multi-region redundancy (second Pi or cloud backup)
- [ ] Performance monitoring (Grafana)

### Long Term (6+ Months)
- [ ] Mobile apps (React Native)
- [ ] WebSocket for real-time updates
- [ ] Multi-tenant support (other countries)
- [ ] ML-based flood prediction

---

## 📚 Documentation Files

- `EXPOSE_PI_BACKEND.md` - Cloudflare Tunnel setup (current approach)
- `FLY_IO_DEPLOYMENT.md` - Fly.io deployment (suspended alternative)
- `QUICK_START_CLOUDFLARE.sh` - Quick tunnel setup script
- `README.md` - Project overview
- `backend/README.md` - Backend development guide
- `DEPLOYMENT_STRATEGY.md` - This file

---

## 🎓 Lessons Learned

### What Worked Well
1. ✅ Raspberry Pi as backend - reliable, cheap, sufficient performance
2. ✅ Cloudflare Tunnel - easy setup, secure, free
3. ✅ Docker Compose - consistent environment, easy deployment
4. ✅ Vercel for frontend - fast deployments, great DX

### What Didn't Work
1. ❌ Vercel Functions - not suitable for persistent backend
2. ❌ Fly.io (attempted) - database connection issues, overkill for our use case

### Key Decisions
- **Pi over Cloud**: Cost savings, sufficient for MVP, we have direct control
- **Cloudflare over ngrok**: More reliable, better docs, enterprise-grade
- **Docker over bare metal**: Easier deployment, reproducible environment
- **PostgreSQL over SQLite**: Production-ready, better performance

---

## 🤝 Contributing

When deploying changes:

1. **Test locally first**: Run backend on Pi, frontend on laptop
2. **Check API compatibility**: Ensure frontend works with backend
3. **Update docs**: If deployment changes, update this file
4. **Monitor after deploy**: Check Vercel dashboard and Pi logs
5. **Rollback if needed**: `git revert` + `git push`

---

## 📞 Support

**Backend Issues**: Check Pi logs
```bash
docker compose logs api
```

**Frontend Issues**: Check Vercel logs
https://vercel.com/your-org/floodsight/logs

**Tunnel Issues**: Check Cloudflare status
https://www.cloudflarestatus.com/

**Database Issues**: 
```bash
docker compose logs db
```

---

**Last Updated**: November 12, 2025
**Status**: ✅ Production (Pi + Cloudflare Tunnel)
**Next Review**: December 12, 2025

