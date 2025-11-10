# ArgoCD Deployment

This directory contains ArgoCD Application manifests for GitOps deployment of FloodSight.

## Prerequisites

1. **Kubernetes cluster** (v1.24+)
2. **ArgoCD installed** in your cluster

### Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Access ArgoCD UI

```bash
# Port forward to access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Access at: `https://localhost:8080` (username: `admin`)

## Deploying FloodSight

### Option 1: Using kubectl

```bash
# Apply the ArgoCD Application
kubectl apply -f deploy/argocd/application.yaml

# Check status
kubectl get application -n argocd floodsight-frontend

# View sync status
kubectl describe application -n argocd floodsight-frontend
```

### Option 2: Using ArgoCD CLI

```bash
# Install ArgoCD CLI
brew install argocd  # macOS
# or download from https://argo-cd.readthedocs.io/en/stable/cli_installation/

# Login
argocd login localhost:8080

# Create application from manifest
argocd app create -f deploy/argocd/application.yaml

# Sync the application
argocd app sync floodsight-frontend

# Watch sync status
argocd app get floodsight-frontend --watch
```

## Configuration

The Application manifest points to:
- **Repository**: `https://github.com/afaqbabar/floodsight.git`
- **Path**: `deploy/k8s/overlays/prod`
- **Target Namespace**: `floodsight`
- **Sync Policy**: Automated with self-healing

### Automated Sync

The application is configured with:
- **Auto-sync**: Changes in the repository are automatically deployed
- **Self-heal**: Kubernetes resources that drift from Git are automatically corrected
- **Prune**: Removed resources from Git are deleted from the cluster

## Environments

To deploy to different environments, modify the `source.path` in the Application:

- **Development**: `deploy/k8s/overlays/dev`
- **Production**: `deploy/k8s/overlays/prod`

## Troubleshooting

### Check application health

```bash
argocd app get floodsight-frontend
```

### View sync history

```bash
argocd app history floodsight-frontend
```

### Manual sync

```bash
argocd app sync floodsight-frontend --force
```

### View logs

```bash
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller
```

## Cleanup

```bash
# Delete the application
kubectl delete -f deploy/argocd/application.yaml

# Or using CLI
argocd app delete floodsight-frontend
```

