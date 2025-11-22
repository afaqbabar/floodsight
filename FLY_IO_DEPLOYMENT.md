# Fly.io Deployment Guide for FloodSight Backend

## Why Fly.io?

Perfect for FloodSight because:

- ✅ **Persistent containers** - Scheduler works!
- ✅ **No cold starts** - Always-on instance
- ✅ **Free PostgreSQL** - Included in free tier
- ✅ **Global edge network** - Fast from anywhere
- ✅ **Simple deployment** - One command to deploy

Unlike Vercel Functions:

- ✅ Can run background workers (scheduler)
- ✅ No 10-second timeout limits
- ✅ Full control over the runtime

---

## Prerequisites

1. **Fly.io account** (free): https://fly.io/app/sign-up
2. **Flyctl CLI** installed

```bash
# Install flyctl (macOS/Linux)
curl -L https://fly.io/install.sh | sh

# Or via Homebrew (macOS)
brew install flyctl

# Verify installation
flyctl version
```

3. **Login to Fly.io**

```bash
flyctl auth login
```

---

## Step 1: Create Fly.io App

Navigate to backend directory:

```bash
cd backend
```

Create the app (you'll be prompted for a name):

```bash
flyctl launch

# Answer the prompts:
# - App name: floodsight-api (or your choice)
# - Region: Select Frankfurt (fra) for EU
# - Add PostgreSQL? YES (select Development - free tier)
# - Add Redis? NO (not needed yet)
# - Deploy now? NO (we'll configure first)
```

This creates:

- ✅ Fly.io app
- ✅ PostgreSQL database (free tier)
- ✅ Database connection credentials (auto-set as secrets)

---

## Step 2: Set Environment Variables

```bash
# Generate secret keys
openssl rand -hex 32

# Set environment variables
flyctl secrets set \
  SECRET_KEY="your-generated-key-here" \
  JWT_SECRET_KEY="another-generated-key-here" \
  ENVIRONMENT="production" \
  DEBUG="false"

# Database URL is automatically set by Fly.io
# No need to manually configure DATABASE_URL
```

---

## Step 3: Deploy

```bash
# Deploy the app
flyctl deploy

# Wait for build and deployment (~2-3 minutes)
```

This will:

1. Build Docker image using `Dockerfile.fly`
2. Push to Fly.io registry
3. Deploy to Frankfurt region
4. Run database migrations automatically
5. Start the API server

---

## Step 4: Verify Deployment

```bash
# Check app status
flyctl status

# View logs
flyctl logs

# Check health endpoint
curl https://floodsight-api.fly.dev/v1/health

# Expected response:
# {
#   "status": "ok",
#   "app": "FloodSight API",
#   "version": "0.1.0",
#   "database": "connected"
# }
```

---

## Step 5: Test API Endpoints

```bash
# Get stations
curl https://floodsight-api.fly.dev/v1/stations

# Trigger data ingestion (development endpoint)
curl -X POST https://floodsight-api.fly.dev/v1/forecasts/ingest-dev

# Get forecasts
curl https://floodsight-api.fly.dev/v1/forecasts

# Get alerts
curl https://floodsight-api.fly.dev/v1/alerts
```

---

## Step 6: Deploy Scheduler (Optional - Run in Background)

The scheduler is included in the main app and runs automatically!

To verify scheduler is running:

```bash
# SSH into the container
flyctl ssh console

# Check running processes
ps aux | grep python

# Exit
exit
```

You should see:

- Main API process (uvicorn)
- Scheduler process (if enabled)

---

## Step 7: Update Frontend

Update the API URL in your deployed frontend:

1. **Option A: Update code (recommended)**

Already done! The API config points to:

```javascript
https://floodsight-api.fly.dev/v1
```

Just replace `floodsight-api` with your actual Fly.io app name if different.

2. **Push changes**

```bash
cd ..
git add .
git commit -m "feat: deploy backend to Fly.io"
git push origin main
```

Vercel will auto-deploy the updated frontend.

---

## Database Management

### Access PostgreSQL Database

```bash
# Connect to database
flyctl postgres connect -a floodsight-api-db

# Run SQL queries
SELECT * FROM stations;
SELECT COUNT(*) FROM forecasts;

# Exit
\q
```

### View Database Info

```bash
# Show database connection details
flyctl postgres db list -a floodsight-api-db

# Check database size
flyctl postgres db show floodsight-api-db
```

### Backup Database

```bash
# Create backup
flyctl postgres backup create -a floodsight-api-db

# List backups
flyctl postgres backup list -a floodsight-api-db
```

---

## Monitoring & Logging

### View Logs

```bash
# Real-time logs
flyctl logs

# Filter by severity
flyctl logs --filter error

# Show last 200 lines
flyctl logs -n 200
```

### Metrics Dashboard

```bash
# Open metrics dashboard in browser
flyctl dashboard

# Check resource usage
flyctl status
```

### Health Checks

Fly.io automatically checks `/v1/health` every 30 seconds.

If health check fails 3 times, Fly.io will restart the app.

---

## Scaling

### Vertical Scaling (More Resources)

```bash
# Upgrade to 512 MB RAM
flyctl scale memory 512

# Upgrade to 2 CPUs
flyctl scale count 2
```

### Horizontal Scaling (More Instances)

```bash
# Add more machines (for high availability)
flyctl scale count 2

# Deploy to multiple regions
flyctl regions add ams  # Amsterdam
flyctl regions add lhr  # London
```

---

## Cost Breakdown

### Free Tier Includes

- ✅ **3 shared-cpu-1x VMs** (256MB RAM each)
- ✅ **3GB persistent volumes**
- ✅ **PostgreSQL database** (Development tier)
- ✅ **160GB bandwidth/month**
- ✅ **No credit card required**

FloodSight fits within free tier:

- 1 VM for API + scheduler (256MB)
- 1 PostgreSQL database (free tier)
- Bandwidth: Typically <1GB/month for MVP

### Paid Plans (If Needed Later)

- **Hobby Plan**: $5/month
  - Production PostgreSQL (1GB)
  - More bandwidth
- **Scale Plan**: Pay as you go
  - Auto-scaling
  - 24/7 support

---

## Troubleshooting

### Build Fails

```bash
# Check build logs
flyctl logs --filter build

# Common issues:
# - Missing dependencies in requirements.txt
# - Docker build errors
# - Python version mismatch
```

### App Won't Start

```bash
# Check logs
flyctl logs

# SSH into container
flyctl ssh console

# Check if app is running
ps aux | grep uvicorn

# Check environment variables
env | grep DATABASE_URL
```

### Database Connection Error

```bash
# Verify database is running
flyctl postgres status -a floodsight-api-db

# Check connection string
flyctl secrets list

# Restart app
flyctl apps restart floodsight-api
```

### Scheduler Not Running

The scheduler is part of the main app. To enable it:

1. Make sure `app/workers/flows.py` is included
2. The scheduler auto-starts when the app boots
3. Check logs for scheduler output:

```bash
flyctl logs | grep scheduler
```

---

## CI/CD Integration (Optional)

### GitHub Actions Deployment

Create `.github/workflows/deploy-flyio.yml`:

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy to Fly.io
        run: flyctl deploy --remote-only
        working-directory: backend
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Get token: `flyctl auth token`

Add to GitHub Secrets: `FLY_API_TOKEN`

---

## Commands Cheat Sheet

```bash
# Deployment
flyctl deploy                    # Deploy app
flyctl deploy --remote-only      # Build in Fly.io (faster)

# Logs & Monitoring
flyctl logs                      # View logs
flyctl status                    # Check status
flyctl dashboard                 # Open web dashboard

# Database
flyctl postgres connect -a DB    # Connect to DB
flyctl postgres backup create    # Backup database

# Configuration
flyctl secrets set KEY=value     # Set env var
flyctl secrets list              # List secrets
flyctl scale memory 512          # Increase RAM

# SSH & Debug
flyctl ssh console               # SSH into container
flyctl ssh sftp                  # Transfer files

# App Management
flyctl apps restart              # Restart app
flyctl apps destroy              # Delete app (careful!)
```

---

## Security Best Practices

1. **Never commit secrets**
   - Use `flyctl secrets set`
   - Don't put secrets in `fly.toml`

2. **Use HTTPS only**
   - Already configured in `fly.toml`
   - Force HTTPS redirects enabled

3. **Keep dependencies updated**

   ```bash
   pip list --outdated
   pip install -U package-name
   ```

4. **Enable auto-updates**
   - Fly.io auto-updates Docker base images
   - You can enable auto-deploy on pushes

---

## Next Steps

1. ✅ Deploy backend to Fly.io
2. ✅ Verify API is accessible
3. ✅ Test dashboard with Fly.io API
4. ⏳ Set up custom domain (optional)
5. ⏳ Configure monitoring alerts
6. ⏳ Enable auto-backups

---

## Support

- **Fly.io Docs**: https://fly.io/docs
- **Community**: https://community.fly.io
- **Status**: https://status.fly.io
- **Support**: support@fly.io

---

## Quick Start Summary

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Login
flyctl auth login

# 3. Launch app (creates database automatically)
cd backend
flyctl launch

# 4. Set secrets
flyctl secrets set SECRET_KEY="$(openssl rand -hex 32)"

# 5. Deploy
flyctl deploy

# 6. Test
curl https://floodsight-api.fly.dev/v1/health

# 7. Update frontend (if needed)
# Change API URL in api-service.js to your Fly.io URL

# 8. Done! 🎉
```

Your complete stack:

- **Frontend**: Vercel (floodsight.vercel.app)
- **Backend API**: Fly.io (floodsight-api.fly.dev)
- **Database**: Fly Postgres (included)
- **Scheduler**: Running on Fly.io ✅
