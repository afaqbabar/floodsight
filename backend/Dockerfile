# Multi-stage Dockerfile for FloodSight Backend API
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev --no-interaction --no-ansi

# Production stage
FROM python:3.11-slim

LABEL maintainer="FloodSight Team"
LABEL description="FloodSight Backend API - Real-time flood monitoring and forecasting"

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Create non-root user
RUN useradd -m -u 1001 -s /bin/bash floodsight && \
    chown -R floodsight:floodsight /app

# Switch to non-root user
USER floodsight

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/v1/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

