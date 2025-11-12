# Vercel Functions API Setup Guide

## Overview

Your FloodSight FastAPI backend is now configured to run as a Vercel Function at:

```
https://floodsight.vercel.app/api/v1/*
```

## What Was Changed

1. **Created `/api/index.py`** - Vercel Function entry point
   - Uses Mangum adapter to convert FastAPI to serverless format
   - Imports your existing FastAPI app from `backend/`

2. **Updated `vercel.json`** - Added Python runtime configuration
   - Configured Python 3.9 runtime
   - Routes `/api/v1/*` to the Python function
   - Set 10-second timeout

3. **Updated `api-service.js`** - Frontend now uses Vercel API
   - Localhost → `http://192.168.178.50:8080/v1` (your Pi)
   - Vercel → `/api/v1` (Vercel Functions)

## Required: Database Setup

⚠️ **You MUST configure a database** before the API will work on Vercel.

### Option 1: Vercel Postgres (Easiest)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Create Postgres database
vercel postgres create floodsight-db

# Link to project
vercel link

# Pull environment variables
vercel env pull .env.local
```

This automatically sets `POSTGRES_URL` in your Vercel project.

### Option 2: Supabase (Free Tier)

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings → Database → Connection string
4. Copy connection string (use "Transaction" mode)
5. Add to Vercel:
   ```bash
   vercel env add DATABASE_URL production
   # Paste: postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
   ```

### Option 3: Neon (Free Tier)

1. Go to [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string
4. Add to Vercel (same as Supabase)

### Option 4: Use Your Pi Database (Not Recommended for Production)

You CAN connect Vercel to your Pi, but you'd need to:
1. Expose your Pi to the internet (risky)
2. Use a service like Cloudflare Tunnel
3. Configure SSL certificates

**Better:** Use one of the managed options above.

## Environment Variables

After setting up the database, add these in Vercel Dashboard:

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

### Required
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/floodsight
```

### Optional (Recommended)
```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://floodsight.vercel.app
```

Generate secret keys:
```bash
openssl rand -hex 32
```

## Deployment Steps

1. **Commit and push changes** (done next)
   ```bash
   git add api/ vercel.json public/assets/js/api-service.js
   git commit -m "feat(api): add Vercel Functions backend"
   git push origin main
   ```

2. **Wait for Vercel to deploy** (~2-3 minutes)
   - GitHub Actions CI/CD will trigger
   - Vercel will build frontend + backend function

3. **Set up database** (choose option above)

4. **Add environment variables in Vercel Dashboard**

5. **Redeploy** to apply env vars:
   ```bash
   vercel --prod
   ```

6. **Test the API**:
   ```bash
   curl https://floodsight.vercel.app/api/v1/health
   ```

   Expected response:
   ```json
   {
     "status": "ok",
     "app": "FloodSight API",
     "version": "0.1.0",
     "database": "connected"
   }
   ```

7. **Test the dashboard**:
   - Visit: https://floodsight.vercel.app/dashboard-figma.html
   - Should show map with stations (not demo London data)
   - Filters should populate
   - Forecasts should load

## Limitations

### ⚠️ Scheduler Cannot Run in Vercel Functions

The automated scheduler (`backend/app/workers/flows.py`) **will NOT work** because Vercel Functions are:
- Stateless
- Short-lived (10 second max)
- No background processes

**Solutions:**

#### Option A: Vercel Cron (Simplest)

Create `/api/cron.py`:
```python
from app.services.ingestion import fetch_and_store_forecasts
from app.services.alerts import compute_and_store_alerts

async def handler(request):
    await fetch_and_store_forecasts()
    await compute_and_store_alerts()
    return {"status": "ok"}
```

Add to `vercel.json`:
```json
{
  "crons": [{
    "path": "/api/cron",
    "schedule": "0 * * * *"
  }]
}
```

#### Option B: GitHub Actions

Create `.github/workflows/scheduled-ingestion.yml`:
```yaml
name: Scheduled Data Ingestion

on:
  schedule:
    - cron: '0 * * * *'  # Every hour

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger ingestion
        run: |
          curl -X POST https://floodsight.vercel.app/api/v1/forecasts/ingest-dev
```

#### Option C: Keep Scheduler on Pi

Your Pi can continue running the scheduler to populate the database, and Vercel just serves the API.

### Cold Starts

- First request after ~5 min idle: 1-3 seconds
- Subsequent requests: <100ms
- Mitigation: Add a health check ping every 5 minutes

## Troubleshooting

### "Module not found" error
- Check that `backend/` is properly added to Python path in `api/index.py`
- Verify all dependencies are in `api/requirements.txt`

### Database connection fails
- Verify `DATABASE_URL` is set in Vercel
- Check connection string format: `postgresql+asyncpg://...`
- Ensure database allows connections from Vercel IPs

### API returns 500 error
- Check Vercel function logs: Dashboard → Deployments → Click deployment → Functions
- Look for Python errors
- Verify all env vars are set

### Dashboard still shows "API Unavailable"
- Clear browser cache
- Check browser console for errors
- Verify API is responding: `curl https://floodsight.vercel.app/api/v1/health`

## Monitoring

### View Function Logs
1. Go to Vercel Dashboard
2. Click your project
3. Deployments → Latest deployment
4. Functions tab → Click `api/index.py`
5. View real-time logs

### Check Database
Use your database provider's dashboard to monitor:
- Connection count
- Query performance
- Database size

### Performance
- Typical response time: <100ms (warm)
- Cold start: 1-3 seconds
- Monitor in Vercel Analytics dashboard

## Cost

- **Vercel Hobby (Free):**
  - 100 GB-hours/month function execution
  - Unlimited requests
  - Usually sufficient for MVP/testing

- **Vercel Pro ($20/month):**
  - 1000 GB-hours/month
  - Better cold start performance
  - Team collaboration

## Next Steps

After deployment works:

1. ✅ Set up Vercel Postgres or Supabase
2. ✅ Configure environment variables
3. ✅ Test API endpoints
4. ✅ Verify dashboard loads real data
5. ⏳ Choose scheduler solution (Vercel Cron or GitHub Actions)
6. ⏳ Set up monitoring/alerts
7. ⏳ Configure custom domain (optional)

## Questions?

Check logs first:
- Vercel Dashboard → Functions logs
- Browser console (F12)
- API response: `curl -v https://floodsight.vercel.app/api/v1/health`

