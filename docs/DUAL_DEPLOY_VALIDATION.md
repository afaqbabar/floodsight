# Dual Deployment Validation Checklist

This document provides validation steps to ensure both Vercel and k3s+FluxCD deployments are working correctly.

## Prerequisites

- [ ] Repository pushed to GitHub
- [ ] Vercel project configured
- [ ] Raspberry Pi with k3s installed
- [ ] FluxCD installed on k3s cluster
- [ ] GitHub Personal Access Token (PAT) with `read:packages` and `write:packages`

---

## 1️⃣ Vercel Deployment Validation

### Build Success

```bash
# Trigger Vercel build by pushing to main
git push origin main

# Expected outcome:
# ✅ Vercel detects push
# ✅ Runs: npm install && npm run build
# ✅ Outputs to dist/ directory
# ✅ Deploys successfully
```

### Verify Live Site

- [ ] Visit: https://floodsight.vercel.app
- [ ] Homepage loads correctly
- [ ] All navigation links work (/privacy, /terms, /impressum, /security)
- [ ] Assets load (CSS, JS, images, logos)
- [ ] No 404 errors in browser console
- [ ] Mobile responsive layout works

### Check Headers

```bash
curl -I https://floodsight.vercel.app | grep -i -E "content-security-policy|strict-transport-security|x-frame-options"
```

**Expected:**

- ✅ `Strict-Transport-Security` header present
- ✅ `Content-Security-Policy` header present
- ✅ `X-Frame-Options: DENY` header present

### Verify Vercel Ignores K8s Files

Check Vercel build logs - should **not** see:

- ❌ `deploy/` directory processing
- ❌ Docker builds
- ❌ Kubernetes manifests

---

## 2️⃣ Docker Image Build Validation

### GitHub Actions Workflow

```bash
# Trigger workflow
git push origin main
# or
git tag v0.1.0 && git push origin v0.1.0

# Check GitHub Actions
# Navigate to: https://github.com/afaqbabar/floodsight/actions
```

**Expected workflow steps:**

- [ ] ✅ Checkout code
- [ ] ✅ Login to GHCR
- [ ] ✅ Setup Buildx
- [ ] ✅ Generate Docker metadata
- [ ] ✅ Build & Push multi-arch (linux/amd64, linux/arm64)

### Verify Images on GHCR

```bash
# Check if image exists (requires authentication)
docker login ghcr.io
docker pull ghcr.io/afaqbabar/floodsight-frontend:latest

# Check image for arm64 (on Raspberry Pi)
docker pull ghcr.io/afaqbabar/floodsight-frontend:latest --platform linux/arm64
```

**Expected tags:**

- [ ] `:latest` (from main branch)
- [ ] `:main` (branch name)
- [ ] `:dev-<sha>` (short SHA)
- [ ] `:v0.1.0` (if tagged)
- [ ] `:0.1` (semver pattern)

### Local Docker Test

```bash
# Test image locally
docker run -p 8080:80 ghcr.io/afaqbabar/floodsight-frontend:latest

# Visit: http://localhost:8080
```

- [ ] Site loads in browser
- [ ] All pages accessible
- [ ] Assets served correctly
- [ ] No errors in docker logs

---

## 3️⃣ FluxCD on k3s Validation

### k3s Cluster Status

```bash
# On Raspberry Pi
sudo k3s kubectl get nodes
sudo k3s kubectl get pods -A
```

**Expected:**

- [ ] ✅ Node is `Ready`
- [ ] ✅ All system pods running

### Flux Bootstrap

```bash
# Install Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# Bootstrap Flux
flux bootstrap github \
  --owner=afaqbabar \
  --repository=floodsight \
  --branch=main \
  --path=deploy/k8s/overlays/prod \
  --personal \
  --token-auth

# Verify Flux installation
flux check
```

**Expected:**

```
✅ flux-system namespace exists
✅ source-controller running
✅ kustomize-controller running
✅ helm-controller running
✅ notification-controller running
✅ image-reflector-controller running
✅ image-automation-controller running
```

### Check Flux Resources

```bash
# Check GitRepository
flux get sources git -n flux-system

# Check Kustomizations
flux get kustomizations -n flux-system

# Check Image Repositories
flux get imagerepositories -n flux-system

# Check Image Policies
flux get imagepolicies -n flux-system

# Check Image Updates
flux get imageupdateautomations -n flux-system
```

**Expected all:**

- [ ] ✅ Status: `True`
- [ ] ✅ No errors
- [ ] ✅ Ready/Succeeded

### FloodSight Application Status

```bash
# Check namespace
kubectl get ns floodsight

# Check all resources
kubectl get all -n floodsight

# Check deployment
kubectl get deployment -n floodsight
kubectl describe deployment frontend -n floodsight

# Check pods
kubectl get pods -n floodsight
kubectl logs -n floodsight -l app=frontend

# Check service
kubectl get svc -n floodsight
```

**Expected:**

- [ ] ✅ Namespace `floodsight` exists
- [ ] ✅ Deployment `frontend` has 2/2 replicas ready
- [ ] ✅ Pods are `Running` (not `ImagePullBackOff`)
- [ ] ✅ Service exposes port 80

### Private Image Pull Secret (if needed)

```bash
# If pods show ImagePullBackOff, create secret:
kubectl -n floodsight create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=afaqbabar \
  --docker-password=<YOUR_PAT> \
  --docker-email=your@email.com

# Verify secret
kubectl get secret ghcr-creds -n floodsight

# Restart deployment
kubectl rollout restart deployment/frontend -n floodsight
```

### Test Application Access

```bash
# Get service details
kubectl get svc frontend -n floodsight

# Port-forward to test locally
kubectl port-forward -n floodsight svc/frontend 8080:80

# Visit: http://localhost:8080
```

- [ ] Site loads correctly
- [ ] All pages work
- [ ] Assets served properly

### Test Ingress (if configured)

```bash
# Get ingress
kubectl get ingress -n floodsight

# Describe ingress
kubectl describe ingress floodsight -n floodsight

# Update /etc/hosts or DNS to point to cluster IP
# Then visit: http://floodsight.example.com
```

---

## 4️⃣ GitOps Image Update Validation

### Tag a New Version

```bash
# Create and push a new tag
git tag v0.1.1
git push origin v0.1.1
```

### Watch GitHub Actions

- [ ] Workflow triggers
- [ ] Multi-arch build succeeds
- [ ] Images pushed with `:v0.1.1`, `:0.1`, `:latest` tags

### Watch FluxCD Auto-Update

```bash
# Watch image repository scanning
flux get imagerepositories -n flux-system --watch

# Watch image policy evaluation
flux get imagepolicies -n flux-system --watch

# Watch for image update automation
flux get imageupdateautomations -n flux-system --watch

# Watch kustomization reconciliation
flux get kustomizations -n flux-system --watch

# Watch deployment rollout
kubectl rollout status deployment/frontend -n floodsight
```

**Expected flow:**

1. ✅ ImageRepository detects new tag `v0.1.1`
2. ✅ ImagePolicy evaluates semver policy (range: `>=0.1.0`)
3. ✅ ImageUpdateAutomation updates `deploy/k8s/overlays/prod/kustomization.yaml`
4. ✅ Flux commits change to Git
5. ✅ Kustomization controller detects change
6. ✅ Deployment updated with new image
7. ✅ Pods restart with new version

### Verify Git Commit

```bash
# Pull latest changes
git pull origin main

# Check commit history
git log -1 --oneline

# Should see: "chore(images): update ghcr.io/afaqbabar/floodsight-frontend:v0.1.1"
```

---

## 5️⃣ Both Environments Running Simultaneously

### Parallel Operation Check

- [ ] ✅ Vercel site accessible at https://floodsight.vercel.app
- [ ] ✅ k3s app running at local cluster endpoint
- [ ] ✅ Both serve the same site content
- [ ] ✅ Both independent of each other
- [ ] ✅ Single git push updates both (Vercel immediately, k3s via GitOps)

### Verify Isolation

```bash
# Check .vercelignore exists
cat .vercelignore

# Check .dockerignore exists
cat .dockerignore

# Confirm Vercel doesn't build Docker
# Check Vercel dashboard build logs

# Confirm Docker doesn't include Vercel files
docker run --rm ghcr.io/afaqbabar/floodsight-frontend:latest ls -la / | grep vercel
# Should return nothing
```

---

## 🎯 Success Criteria

All checkboxes above should be checked ✅ for full dual deployment validation.

### Quick Health Check Commands

**Vercel:**

```bash
curl -I https://floodsight.vercel.app | head -1
# Expected: HTTP/2 200
```

**GHCR:**

```bash
docker pull ghcr.io/afaqbabar/floodsight-frontend:latest
# Expected: Pull complete
```

**k3s:**

```bash
kubectl get pods -n floodsight
# Expected: All pods Running
```

**Flux:**

```bash
flux check
# Expected: All prerequisites met
```

---

## 🐛 Troubleshooting

### Vercel Build Fails

- Check build logs in Vercel dashboard
- Verify `npm run build` works locally
- Check `vercel.json` configuration
- Ensure `public/` directory exists

### Docker Build Fails

- Check GitHub Actions logs
- Verify Dockerfile.nginx syntax
- Check if vite.config.js is correct
- Test build locally: `npm run build`

### Pods in ImagePullBackOff

- Check image name matches in deployment
- Create imagePullSecrets if GHCR is private
- Verify GitHub PAT has `read:packages` scope
- Check image exists: `docker pull <image>`

### Flux Not Updating Images

- Check ImageRepository scanning interval
- Verify ImagePolicy semver range
- Check ImageUpdateAutomation has write access to repo
- Check Flux has SSH key or PAT for Git push

### Service Not Accessible

- Check service type (ClusterIP vs NodePort vs LoadBalancer)
- Use port-forward for testing: `kubectl port-forward ...`
- Check ingress configuration
- Verify firewall rules on Raspberry Pi

---

## 📝 Notes

- **Vercel** updates instantly on push to main
- **FluxCD** updates within 1-2 minutes after image tag is created
- **Multi-arch** images work on both x86_64 (Vercel build) and ARM64 (Raspberry Pi)
- **GitOps** ensures k3s deployment is always in sync with Git state

Last updated: 2025-11-05
