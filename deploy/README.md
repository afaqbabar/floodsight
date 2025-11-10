# FloodSight Deployment

This directory contains deployment configurations for FloodSight using Kubernetes and GitOps.

## 📁 Directory Structure

```
deploy/
├── k8s/                    # Kubernetes manifests
│   ├── base/               # Base resources (namespace, deployment, service, ingress)
│   └── overlays/           # Environment-specific overlays
│       ├── dev/            # Development environment
│       └── prod/           # Production environment
├── flux/                   # FluxCD GitOps configuration
│   ├── image-repositories.yaml
│   ├── image-policies.yaml
│   ├── image-update.yaml
│   └── README.md
├── argocd/                 # ArgoCD GitOps configuration
│   ├── application.yaml
│   └── README.md
└── README.md              # This file
```

## 🚀 Deployment Options

### Option 1: Vercel (Recommended for Frontend)

The easiest way to deploy FloodSight is using Vercel:

```bash
# Connect your repository to Vercel
vercel

# Or use the Vercel GitHub integration (automatic)
```

See the main [README.md](../README.md#deployment) for details.

### Option 2: Docker + Docker Compose

For local or server-based deployments:

```bash
# Build and run with docker-compose
docker-compose up -d

# Or build manually
docker build -f Dockerfile.nginx -t floodsight:latest .
docker run -p 8080:80 floodsight:latest
```

### Option 3: Kubernetes

Deploy to any Kubernetes cluster using `kubectl`:

```bash
# Apply base manifests
kubectl apply -k deploy/k8s/base

# Or apply production overlay
kubectl apply -k deploy/k8s/overlays/prod
```

### Option 4: GitOps with FluxCD

Continuous deployment with FluxCD:

```bash
# Bootstrap Flux
flux bootstrap github \
  --owner=afaqbabar \
  --repository=floodsight \
  --branch=main \
  --path=deploy/k8s/overlays/prod \
  --personal

# Flux will automatically sync changes from Git
```

See [flux/README.md](flux/README.md) for details.

### Option 5: GitOps with ArgoCD

Alternative GitOps with ArgoCD:

```bash
# Apply ArgoCD Application
kubectl apply -f deploy/argocd/application.yaml

# ArgoCD will sync and manage the deployment
```

See [argocd/README.md](argocd/README.md) for details.

## 🐳 Container Images

FloodSight frontend images are published to GitHub Container Registry (GHCR):

```
ghcr.io/afaqbabar/floodsight-frontend:latest
ghcr.io/afaqbabar/floodsight-frontend:v1.0.0
ghcr.io/afaqbabar/floodsight-frontend:sha-abc1234
```

### Building Images Locally

```bash
# Build with build args
docker build \
  -f Dockerfile.nginx \
  --build-arg GIT_SHA=$(git rev-parse HEAD) \
  --build-arg GIT_TAG=$(git describe --tags --always) \
  -t ghcr.io/afaqbabar/floodsight-frontend:local \
  .

# Test locally
docker run -p 8080:80 ghcr.io/afaqbabar/floodsight-frontend:local
```

### Pushing to GHCR

```bash
# Authenticate to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag and push
docker tag floodsight:latest ghcr.io/afaqbabar/floodsight-frontend:v1.0.0
docker push ghcr.io/afaqbabar/floodsight-frontend:v1.0.0
```

## 🌍 Environment Configuration

### Development

- **Replicas**: 1
- **Resources**: Minimal (cpu: 25m, memory: 32Mi)
- **Domain**: `dev.floodsight.io`

### Production

- **Replicas**: 2+
- **Resources**: Standard (cpu: 50m, memory: 64Mi)
- **Domain**: `floodsight.io`
- **Auto-scaling**: HPA configured for load
- **GDPR**: Deployed to EU region

## 📊 Monitoring & Health Checks

All deployments include:

- **Readiness probe**: `GET /healthz` (checks if container is ready to serve traffic)
- **Liveness probe**: `GET /healthz` (checks if container is alive)

The `/api/healthz.json` endpoint returns:

```json
{
  "ok": true,
  "status": "healthy",
  "timestamp": "2025-11-10T00:00:00.000Z",
  "version": "1.0.0"
}
```

## 🔒 Security

### Image Pull Secrets

For private registries, create a secret:

```bash
kubectl create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=USERNAME \
  --docker-password=$GITHUB_TOKEN \
  --namespace=floodsight
```

### Security Context

Containers run with:
- **Non-root user**: UID 101 (nginx user)
- **Read-only root filesystem**: Enabled
- **No privilege escalation**: Enforced

### Network Policies

Consider adding NetworkPolicies to restrict traffic:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-netpol
  namespace: floodsight
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 80
```

## 🔄 CI/CD Integration

### GitHub Actions

The CI/CD pipeline (`.github/workflows/ci.yml`) automatically:
1. Builds the application
2. Runs tests and security scans
3. Builds Docker image
4. Pushes to GHCR (on main branch)
5. GitOps updates image tag (FluxCD automation)

### Manual Deployment

To trigger a deployment manually:

```bash
# Update image in kustomization
cd deploy/k8s/overlays/prod
kustomize edit set image ghcr.io/afaqbabar/floodsight-frontend:v1.0.0

# Commit and push
git add .
git commit -m "chore(deploy): update frontend to v1.0.0"
git push

# GitOps will automatically sync
```

## 📝 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [FluxCD Documentation](https://fluxcd.io/docs/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GHCR Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## 🆘 Troubleshooting

### Check pod status

```bash
kubectl get pods -n floodsight
kubectl describe pod <pod-name> -n floodsight
kubectl logs <pod-name> -n floodsight
```

### Check ingress

```bash
kubectl get ingress -n floodsight
kubectl describe ingress -n floodsight
```

### Check service endpoints

```bash
kubectl get endpoints -n floodsight
```

### Force rollout restart

```bash
kubectl rollout restart deployment/frontend -n floodsight
```

