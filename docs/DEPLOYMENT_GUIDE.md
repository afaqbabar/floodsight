# FloodSight Deployment Guide

## Overview

This guide documents the complete DevOps setup for FloodSight, including:

- ✅ Vite build system for bundling assets
- ✅ Docker containerization with nginx
- ✅ GitHub Actions CI/CD for multi-arch images
- ✅ Kubernetes manifests with Kustomize
- ✅ FluxCD GitOps automation
- ✅ Vercel deployment (unchanged)

## 1. Build System (Vite)

### Configuration

**`vite.config.js`** - Multi-page build configuration

- Bundles `/assets/js/main.js` and dependencies
- Processes all HTML pages (index, impressum, privacy, terms, security, thanks, 404, verify-assets, google verification)
- Outputs to `dist/` directory
- Uses relative paths (`base: './'`) for portability

### Commands

```bash
npm run dev      # Dev server at http://localhost:5173
npm run build    # Production build to dist/
npm run preview  # Preview build at http://localhost:4173
```

### Files Modified/Created

- ✅ `package.json` - Added Vite dependency and updated scripts
- ✅ `vite.config.js` - Created build configuration

## 2. Docker Setup

### Dockerfile

**`Dockerfile.nginx`** - Multi-stage build

- **Stage 1**: Node.js build (npm ci → vite build)
- **Stage 2**: Nginx runtime serving `dist/`

### Files Created

- ✅ `Dockerfile.nginx` - Container build configuration
- ✅ `.dockerignore` - Excludes node_modules, dist, .git
- ✅ `docker-compose.yml` - Local development setup

### Local Testing

```bash
# Build image
docker build -f Dockerfile.nginx -t ghcr.io/afaqbabar/floodsight-frontend:dev-local .

# Run container
docker run -p 8080:80 ghcr.io/afaqbabar/floodsight-frontend:dev-local

# Or use docker-compose
docker-compose up
```

Visit: http://localhost:8080

## 3. GitHub Actions CI/CD

### Workflow

**`.github/workflows/build-and-push.yml`**

**Triggers:**

- Push to `main` branch
- Manual workflow dispatch

**What it does:**

1. Checks out code
2. Logs into GitHub Container Registry (GHCR)
3. Sets up Docker Buildx for multi-arch builds
4. Builds for `linux/amd64` and `linux/arm64` (supports Raspberry Pi 5!)
5. Pushes to `ghcr.io/afaqbabar/floodsight-frontend` with tags:
   - `:latest` (always points to latest main)
   - `:dev-<git-sha>` (specific commit)
6. Uses layer caching for faster builds

**Image location:** `ghcr.io/afaqbabar/floodsight-frontend:latest`

## 4. Kubernetes Manifests

### Base Resources

Location: `deploy/k8s/base/`

**Resources:**

- `namespace.yaml` - Creates `floodsight` namespace
- `frontend-deployment.yaml` - 2 replicas, resource limits
- `frontend-service.yaml` - ClusterIP service on port 80
- `ingress.yaml` - Nginx ingress (customize domain)
- `kustomization.yaml` - Base kustomization file

### Deployment Spec

```yaml
replicas: 2
resources:
  requests: { cpu: '50m', memory: '64Mi' }
  limits: { cpu: '300m', memory: '256Mi' }
```

### Deploy Base

```bash
kubectl apply -k deploy/k8s/base
```

## 5. Kustomize Overlays

### Dev Environment

Location: `deploy/k8s/overlays/dev/`

- Uses base manifests
- Image tag: `:dev`

```bash
kubectl apply -k deploy/k8s/overlays/dev
```

### Production Environment

Location: `deploy/k8s/overlays/prod/`

- Uses base manifests
- Image tag: `:v0.1.0` (semver)

```bash
kubectl apply -k deploy/k8s/overlays/prod
```

## 6. FluxCD GitOps

### Components

Location: `deploy/flux/`

**Resources:**

- `image-repositories.yaml` - Watches GHCR for new images
- `image-policies.yaml` - Filters by semver (>=0.1.0)
- `image-update.yaml` - Auto-updates prod overlay

### Bootstrap Flux

**One-time setup on your cluster:**

```bash
# Install Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# Bootstrap (requires GitHub PAT)
flux bootstrap github \
  --owner=afaqbabar \
  --repository=floodsight \
  --branch=main \
  --path=deploy/k8s/overlays/prod \
  --personal
```

### What Flux Does

1. **Watches** GHCR for new images matching semver policy
2. **Updates** `deploy/k8s/overlays/prod/kustomization.yaml` automatically
3. **Commits** changes back to main branch
4. **Syncs** cluster to match Git state

## 7. Release Workflow

### Standard Flow

```
Developer pushes to main
  ↓
GitHub Actions builds & pushes
  • ghcr.io/.../floodsight-frontend:latest
  • ghcr.io/.../floodsight-frontend:dev-abc1234
  ↓
Manually tag for production
  git tag v0.1.1
  git push --tags
  ↓
(Optional) Configure CI to push :v0.1.1 tag
  ↓
Flux detects new semver tag
  ↓
Flux updates deploy/k8s/overlays/prod/kustomization.yaml
  ↓
Flux syncs cluster → production updated!
```

### Tagging Best Practices

```bash
# Create annotated tag
git tag -a v0.1.1 -m "Release v0.1.1 - Feature description"

# Push tag
git push origin v0.1.1

# Optional: Configure GitHub Actions to build tagged releases
```

## 8. Vercel Deployment

**Status:** ✅ Unchanged

- `vercel.json` remains untouched
- Static site continues deploying to Vercel
- Security headers preserved
- Clean URLs via rewrites still work

## 9. Directory Structure

```
floodsight/
├── .github/
│   └── workflows/
│       └── build-and-push.yml          # CI/CD workflow
├── deploy/
│   ├── flux/
│   │   ├── image-repositories.yaml     # GHCR watcher
│   │   ├── image-policies.yaml         # Semver filter
│   │   ├── image-update.yaml           # Auto-update config
│   │   └── README.md                   # Flux bootstrap guide
│   └── k8s/
│       ├── base/
│       │   ├── namespace.yaml
│       │   ├── frontend-deployment.yaml
│       │   ├── frontend-service.yaml
│       │   ├── ingress.yaml
│       │   └── kustomization.yaml
│       └── overlays/
│           ├── dev/
│           │   └── kustomization.yaml  # Dev config
│           └── prod/
│               └── kustomization.yaml  # Prod config
├── assets/
│   ├── css/
│   │   └── floodsight.css
│   └── js/
│       ├── main.js                     # Entry point
│       ├── dom.js
│       ├── floodsight.js
│       ├── forms.js
│       ├── nav.js
│       └── utils.js
├── Dockerfile.nginx                    # Multi-stage build
├── .dockerignore                       # Build excludes
├── docker-compose.yml                  # Local dev
├── vite.config.js                      # Build config
├── package.json                        # Updated scripts
└── vercel.json                         # Unchanged
```

## 10. Acceptance Checklist

### Local Build

- [ ] `npm run build` produces `dist/` directory
- [ ] All HTML pages present in `dist/`
- [ ] `npm run preview` serves site correctly

### Docker

- [ ] Image builds successfully
- [ ] Container serves site on port 80
- [ ] All pages accessible

### GitHub Actions

- [ ] Workflow runs on push to main
- [ ] Multi-arch build succeeds (amd64, arm64)
- [ ] Images pushed to `ghcr.io/afaqbabar/floodsight-frontend:latest`

### Kubernetes

- [ ] `kubectl apply -k deploy/k8s/overlays/dev` creates resources
- [ ] Deployment healthy with 2/2 pods running
- [ ] Service routes traffic correctly

### FluxCD

- [ ] Flux bootstrap completes successfully
- [ ] ImageRepository scans GHCR
- [ ] ImagePolicy filters semver correctly
- [ ] ImageUpdateAutomation commits work

### Vercel

- [ ] Vercel deployment still works
- [ ] `vercel.json` unchanged
- [ ] Site accessible at floodsight.vercel.app

## 11. Troubleshooting

### Build Issues

```bash
# Clear cache
rm -rf node_modules dist
npm install
npm run build
```

### Docker Issues

```bash
# Check logs
docker logs <container-id>

# Test locally
docker-compose up --build

# Prune old images
docker image prune -a
```

### Kubernetes Issues

```bash
# Check pod status
kubectl get pods -n floodsight

# View logs
kubectl logs -n floodsight deployment/frontend

# Describe deployment
kubectl describe deployment frontend -n floodsight

# Check ingress
kubectl get ingress -n floodsight
```

### Flux Issues

```bash
# Check Flux status
flux check

# View image automation
flux get images -A

# Reconcile manually
flux reconcile image repository floodsight-frontend
flux reconcile image policy frontend-policy
flux reconcile image update floodsight-updater
```

## 12. Next Steps

### Recommended Enhancements

1. **Add staging environment**
   - Create `deploy/k8s/overlays/staging`
   - Use `:dev-*` tags for auto-deployment

2. **Configure semantic versioning CI**
   - Add GitHub Action to tag releases
   - Build versioned images automatically

3. **Add monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert rules

4. **Add backup strategy**
   - ArgoCD as alternative to Flux
   - Velero for cluster backups

5. **Custom domain for K8s**
   - Update `ingress.yaml` with real domain
   - Configure TLS with cert-manager

## 13. Support

For issues or questions:

- **Repository:** github.com/afaqbabar/floodsight
- **Email:** hello@floodsight.com
- **Security:** security@floodsight.com

---

Built with ❤️ for climate resilience.
