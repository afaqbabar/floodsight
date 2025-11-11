"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

from app.api.v1.endpoints import router as v1_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.session import close_db, init_db

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "floodsight_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "floodsight_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time flood monitoring and forecasting API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for Prometheus metrics
@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Collect Prometheus metrics for each request."""
    if settings.METRICS_ENABLED and request.url.path != "/metrics":
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(duration)
        
        return response
    else:
        return await call_next(request)


# Include API router
app.include_router(v1_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }


# Prometheus metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint.
    
    Exposes application metrics in Prometheus format.
    """
    if not settings.METRICS_ENABLED:
        return Response(content="Metrics disabled", status_code=404)
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

