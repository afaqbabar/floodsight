# FloodSight Backend - K8s Deployment Guide

This guide covers deploying the FloodSight Backend API to Kubernetes (K3s on Raspberry Pi or any K8s cluster).

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Ingress (NGINX)                   │
│              api.floodsight.com (TLS)               │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│            Service: floodsight-backend              │
│                  (ClusterIP:8080)                   │
└─────────────┬───────────────────┬───────────────────┘
              │                   │
              ▼                   ▼
    ┌─────────────────┐   ┌─────────────────┐
    │  Backend Pod 1  │   │  Backend Pod 2  │
    │  (FastAPI API)  │   │  (FastAPI API)  │
    └─────────┬───────┘   └─────────┬───────┘
              │                     │
              └──────────┬──────────┘
                         ▼
              ┌──────────────────────┐
              │   Scheduler Pod      │
              │  (APScheduler Flow)  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │    PostgreSQL DB     │
              │    (with PostGIS)    │
              └──────────────────────┘
```

## 📋 Prerequisites

1. **Kubernetes cluster** (K3s, K8s, or managed cluster)
2. **kubectl** configured to access your cluster
3. **Nginx Ingress Controller** installed
4. **cert-manager** for TLS certificates (optional but recommended)
5. **MetalLB** for LoadBalancer IPs (if on bare metal)
6. **PostgreSQL** database accessible from cluster

## 🚀 Deployment Steps

### 1. Create Namespace

```bash
kubectl create namespace floodsight
kubectl config set-context --current --namespace=floodsight
```

### 2. Setup PostgreSQL Database

**Option A: Use external PostgreSQL**

Skip this step if you have an external database.

**Option B: Deploy PostgreSQL in K8s**

```bash
# Create PostgreSQL deployment
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_DB
          value: floodsight
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
EOF

# Create postgres password secret
kubectl create secret generic postgres-credentials \
  --from-literal=password=$(openssl rand -base64 32)
```

### 3. Configure Backend Secrets

```bash
# Copy the secrets template
cp base/backend-secrets.yaml.example base/backend-secrets.yaml

# Edit the secrets file with your actual values
nano base/backend-secrets.yaml

# Required secrets:
# - database-url: PostgreSQL connection string
# - cds-api-key: ECMWF CDS API key (for GloFAS data)
# Optional secrets:
# - supabase-jwks-url: For JWT authentication
# - smtp-*: For email notifications
# - twilio-*: For SMS notifications
# - etc.

# Apply the secrets
kubectl apply -f base/backend-secrets.yaml

# Verify secrets are created
kubectl get secrets floodsight-backend-secrets
```

**Example database-url format:**

```
postgresql+asyncpg://postgres:password@postgres.floodsight.svc.cluster.local:5432/floodsight
```

### 4. Run Database Migrations

```bash
# Create a one-time job to run Alembic migrations
kubectl run alembic-migrate \
  --image=ghcr.io/afaqbabar/floodsight-backend:latest \
  --restart=Never \
  --env="DATABASE_URL=$(kubectl get secret floodsight-backend-secrets -o jsonpath='{.data.database-url}' | base64 -d)" \
  --command -- alembic upgrade head

# Wait for migration to complete
kubectl wait --for=condition=complete --timeout=300s job/alembic-migrate

# Check logs
kubectl logs alembic-migrate

# Clean up
kubectl delete pod alembic-migrate
```

### 5. Deploy Backend Application

```bash
# Apply all K8s manifests
kubectl apply -k base/

# Or apply individually:
kubectl apply -f base/backend-configmap.yaml
kubectl apply -f base/backend-deployment.yaml
kubectl apply -f base/backend-service.yaml
kubectl apply -f base/backend-ingress.yaml
```

### 6. Verify Deployment

```bash
# Check pods are running
kubectl get pods -l component=backend

# Check services
kubectl get svc floodsight-backend

# Check ingress
kubectl get ingress floodsight-backend

# View logs
kubectl logs -l component=backend --tail=50 -f

# Check health endpoint
kubectl port-forward svc/floodsight-backend 8080:8080
curl http://localhost:8080/v1/health
```

Expected health response:

```json
{
  "status": "ok",
  "app": "FloodSight Backend API",
  "version": "0.1.0",
  "environment": "production",
  "database": "connected"
}
```

### 7. Seed Initial Data

```bash
# Run the seed script to populate sample stations
kubectl exec -it deployment/floodsight-backend -- python -m app.services.seed

# Verify stations were created
kubectl exec -it deployment/floodsight-backend -- \
  curl http://localhost:8080/v1/stations
```

### 8. Configure DNS

Point your domain to the Ingress IP:

```bash
# Get the ingress IP
kubectl get ingress floodsight-backend

# Add DNS A record:
# api.floodsight.com -> <INGRESS_IP>
```

### 9. Test API Endpoints

```bash
# Health check
curl https://api.floodsight.com/v1/health

# List stations
curl https://api.floodsight.com/v1/stations

# Trigger forecast ingestion (manual)
curl -X POST https://api.floodsight.com/v1/forecasts/ingest-dev

# Compute alerts
curl -X POST https://api.floodsight.com/v1/alerts/compute

# View alerts
curl https://api.floodsight.com/v1/alerts

# API documentation
open https://api.floodsight.com/docs
```

## 📊 Monitoring

### Prometheus Metrics

The backend exposes Prometheus metrics at `/metrics`:

```bash
# Port-forward to access metrics
kubectl port-forward svc/floodsight-backend 8080:8080
curl http://localhost:8080/metrics
```

### Logs

```bash
# View API logs
kubectl logs -l component=backend -f

# View scheduler logs
kubectl logs -l component=scheduler -f

# View logs from specific pod
kubectl logs <pod-name> -f

# View logs with timestamps
kubectl logs -l component=backend --timestamps=true
```

### Resource Usage

```bash
# Check resource usage
kubectl top pods -l component=backend

# Describe deployment
kubectl describe deployment floodsight-backend

# View events
kubectl get events --sort-by='.lastTimestamp'
```

## 🔄 Updates & Rollbacks

### Update Backend Image

```bash
# Update to a new version
kubectl set image deployment/floodsight-backend \
  backend=ghcr.io/afaqbabar/floodsight-backend:v0.2.0

# Watch rollout status
kubectl rollout status deployment/floodsight-backend

# View rollout history
kubectl rollout history deployment/floodsight-backend
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/floodsight-backend

# Rollback to specific revision
kubectl rollout undo deployment/floodsight-backend --to-revision=2
```

## 🔧 Troubleshooting

### Pod won't start

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check events
kubectl get events --field-selector involvedObject.name=<pod-name>
```

### Database connection issues

```bash
# Test database connectivity from pod
kubectl exec -it deployment/floodsight-backend -- \
  python -c "import asyncio; from app.db.session import init_db; asyncio.run(init_db())"

# Check database secret
kubectl get secret floodsight-backend-secrets -o yaml
```

### Ingress not working

```bash
# Check ingress status
kubectl describe ingress floodsight-backend

# Check nginx ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Test service directly
kubectl port-forward svc/floodsight-backend 8080:8080
curl http://localhost:8080/v1/health
```

### Scheduler not running

```bash
# Check scheduler pod
kubectl get pods -l component=scheduler

# View scheduler logs
kubectl logs -l component=scheduler -f

# Manually trigger ingestion flow
kubectl exec -it deployment/floodsight-scheduler -- \
  python -m app.workers.flows once
```

## 🔐 Security Best Practices

1. **Secrets Management**
   - Never commit `backend-secrets.yaml` to git
   - Use external secrets management (e.g., Sealed Secrets, External Secrets Operator)
   - Rotate secrets regularly

2. **TLS/HTTPS**
   - Always use TLS in production
   - Configure cert-manager for automatic certificate renewal
   - Use strong cipher suites

3. **Network Policies**
   - Implement network policies to restrict pod-to-pod communication
   - Only allow necessary ingress/egress traffic

4. **RBAC**
   - Use service accounts with minimal permissions
   - Implement RBAC policies for API access

5. **Image Security**
   - Use official base images
   - Scan images with Trivy (automated in CI)
   - Keep images up-to-date with Dependabot

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale backend API
kubectl scale deployment floodsight-backend --replicas=5

# Enable auto-scaling (HPA)
kubectl autoscale deployment floodsight-backend \
  --min=2 --max=10 --cpu-percent=70
```

### Vertical Scaling

Edit `backend-deployment.yaml` to adjust resource requests/limits:

```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

## 🧪 Testing

### End-to-End Test Flow

```bash
# 1. Check health
curl https://api.floodsight.com/v1/health

# 2. List stations
curl https://api.floodsight.com/v1/stations

# 3. Trigger ingestion
curl -X POST https://api.floodsight.com/v1/forecasts/ingest-dev

# 4. Check forecasts
curl https://api.floodsight.com/v1/forecasts?limit=10

# 5. Compute alerts
curl -X POST https://api.floodsight.com/v1/alerts/compute

# 6. View alerts
curl https://api.floodsight.com/v1/alerts
```

## 📚 Additional Resources

- [Backend README](../../backend/README.md)
- [API Documentation](https://api.floodsight.com/docs)
- [K8s Documentation](https://kubernetes.io/docs/)
- [K3s Documentation](https://docs.k3s.io/)
- [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [cert-manager](https://cert-manager.io/)

## 🆘 Support

For issues or questions:

- GitHub Issues: https://github.com/afaqbabar/floodsight/issues
- Documentation: https://github.com/afaqbabar/floodsight/tree/main/docs
