# Multi-stage Dockerfile for FloodSight
# Stage 1: Build
FROM node:20-alpine AS builder

LABEL maintainer="FloodSight Team"
LABEL description="FloodSight - Real-time flood monitoring and forecasting"

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy source code
COPY . .

# Build application
RUN npm run build

# Stage 2: Production
FROM nginx:alpine AS production

# Install Node.js for any runtime scripts (optional)
RUN apk add --no-cache nodejs npm

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Copy health check script
COPY --from=builder /app/public/health.html /usr/share/nginx/html/health.html

# Create non-root user
RUN addgroup -g 1001 -S floodsight && \
    adduser -S floodsight -u 1001 && \
    chown -R floodsight:floodsight /usr/share/nginx/html && \
    chown -R floodsight:floodsight /var/cache/nginx && \
    chown -R floodsight:floodsight /var/log/nginx && \
    chown -R floodsight:floodsight /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R floodsight:floodsight /var/run/nginx.pid

# Switch to non-root user
USER floodsight

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health.html || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

