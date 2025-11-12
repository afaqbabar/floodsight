# Vercel Functions API

This directory contains the Vercel serverless function that runs the FloodSight FastAPI backend.

## How It Works

1. **`index.py`** - Entry point for Vercel Function
   - Uses Mangum to adapt FastAPI to ASGI/AWS Lambda format
   - Imports the main FastAPI app from `backend/app/main.py`
   - Disables lifespan events (Vercel handles cold starts differently)

2. **`requirements.txt`** - Python dependencies for the serverless function
   - Vercel installs these when building the function
   - Includes Mangum adapter for serverless compatibility

## Deployment

When you push to `main`, Vercel automatically:
1. Detects Python function in `/api` directory
2. Installs dependencies from `requirements.txt`
3. Deploys function to `https://floodsight.vercel.app/api/*`

## API Endpoints

All backend API routes are available at:
- `https://floodsight.vercel.app/api/v1/health`
- `https://floodsight.vercel.app/api/v1/stations`
- `https://floodsight.vercel.app/api/v1/forecasts`
- `https://floodsight.vercel.app/api/v1/alerts`

## Environment Variables

Configure these in Vercel Dashboard → Project Settings → Environment Variables:

### Required
- `DATABASE_URL` - PostgreSQL connection string (use Vercel Postgres or external)

### Optional
- `SECRET_KEY` - Application secret key
- `JWT_SECRET_KEY` - JWT signing key
- `ENVIRONMENT` - Set to `production`
- `DEBUG` - Set to `false`

## Limitations

### ⚠️ Scheduler Not Supported
The APScheduler worker (`backend/app/workers/flows.py`) **cannot run in Vercel Functions** because:
- Serverless functions are stateless and short-lived
- No persistent background processes
- Cold starts every ~5 minutes

**Solution:** Deploy scheduler separately:
1. **Vercel Cron Jobs** - Use Vercel's cron feature to trigger an API endpoint
2. **GitHub Actions** - Schedule workflows to call your API
3. **External Service** - Use Railway/Render for the scheduler worker

### Database Connections
- Vercel Functions have a 10-second execution limit
- Use connection pooling carefully
- Consider using Vercel Postgres or Supabase for better integration

### Cold Starts
- First request after idle may take 1-3 seconds
- Subsequent requests are faster (warm)
- Consider adding a health check endpoint ping

## Local Testing

Test the Vercel function locally:

```bash
# Install Vercel CLI
npm install -g vercel

# Run local dev server
vercel dev
```

## Monitoring

Check function logs in Vercel Dashboard:
- Project → Deployments → Click deployment → Functions tab
- Shows execution time, errors, and logs

## Database Setup for Vercel

### Option 1: Vercel Postgres (Recommended)
```bash
vercel postgres create
# Follow prompts, then link to project
vercel env pull
```

### Option 2: External Provider
Use Supabase, Neon, or Railway:
1. Create database on provider
2. Get connection string
3. Add as `DATABASE_URL` in Vercel env vars

## Troubleshooting

### Import errors
- Ensure `backend/` is in Python path (handled in `index.py`)
- Check that all dependencies are in `requirements.txt`

### Database connection fails
- Verify `DATABASE_URL` is set in Vercel env vars
- Check firewall allows Vercel IPs
- Use `asyncpg` (not `psycopg2`) for async support

### Function timeout
- Optimize queries (add indexes)
- Reduce data fetched per request
- Consider caching frequently accessed data

