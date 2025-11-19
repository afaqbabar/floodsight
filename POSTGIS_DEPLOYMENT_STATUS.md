# 🚀 PostGIS Deployment Status

## ✅ **Completed Steps**

1. ✅ **Updated `backend/Dockerfile.db`** - PostgreSQL 16 + PostGIS compilation
2. ✅ **Created GitHub Actions workflow** (`.github/workflows/postgres-postgis-ci.yml`)
   - Multi-arch builds (ARM64 + AMD64)
   - Matches your existing CI/CD pattern
3. ✅ **Created Kubernetes StatefulSet** (`deploy/k8s/base/postgres-statefulset.yaml`)
   - Uses PostGIS image from GHCR
   - Preserves existing PVC configuration
4. ✅ **Updated kustomization.yaml** - Added postgres-statefulset to resources
5. ✅ **Committed and pushed** changes to trigger GitHub Actions build

---

## ⏳ **In Progress**

### **GitHub Actions Build**

- **Workflow**: `postgres-postgis-ci.yml`
- **Status**: Building (takes ~5-10 minutes for PostGIS compilation)
- **Image**: `ghcr.io/afaqbabar/floodsight-postgres-postgis:latest`
- **Check status**: https://github.com/afaqbabar/floodsight/actions

---

## 🔄 **Next Steps (After Image Build Completes)**

### **1. Verify Image Availability**

```bash
# Check if image exists (requires authentication if private)
docker pull ghcr.io/afaqbabar/floodsight-postgres-postgis:latest --platform linux/arm64
```

### **2. Configure Image Pull Secret (If Image is Private)**

If the image repository is **private**, create a Kubernetes secret:

```bash
# Create GitHub Personal Access Token (PAT) with `read:packages` permission
# Then create secret:
kubectl create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=afaqbabar \
  --docker-password=<YOUR_GITHUB_PAT> \
  --docker-email=your@email.com \
  -n floodsight

# Update StatefulSet to use the secret
kubectl patch statefulset postgres -n floodsight --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/imagePullSecrets", "value": [{"name": "ghcr-creds"}]}]'
```

**Or make the repository public:**

- Go to: https://github.com/users/afaqbabar/packages/container/floodsight-postgres-postgis/settings
- Change visibility to **Public**

### **3. Update StatefulSet to Use PostGIS Image**

Once the image is built and accessible:

```bash
# Update StatefulSet to use PostGIS image
kubectl patch statefulset postgres -n floodsight --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/image", "value": "ghcr.io/afaqbabar/floodsight-postgres-postgis:latest"}]'

# Or apply the manifest directly
kubectl apply -f deploy/k8s/base/postgres-statefulset.yaml
```

### **4. Wait for Pod to Start**

```bash
# Watch pod status
kubectl get pods -n floodsight postgres-0 -w

# Check logs if issues
kubectl logs -n floodsight postgres-0
```

### **5. Verify PostGIS Installation**

```bash
# Wait for pod to be ready
kubectl wait --for=condition=ready pod -n floodsight postgres-0 --timeout=120s

# Verify PostGIS extension
kubectl exec -n floodsight postgres-0 -- psql -U postgres -d floodsight -c \
  "CREATE EXTENSION IF NOT EXISTS postgis; SELECT PostGIS_Version();"
```

**Expected output:**

```
CREATE EXTENSION
 postgis_version
------------------
 3.4.0
(1 row)
```

### **6. Run Database Migration**

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pods -n floodsight -l component=backend -o jsonpath='{.items[0].metadata.name}')

# Run Alembic migration
kubectl exec -n floodsight $BACKEND_POD -- alembic upgrade head
```

### **7. Test Vessel Detection**

```bash
# Port-forward backend service
kubectl port-forward -n floodsight svc/floodsight-backend 8080:8080

# In another terminal, test vessel detection
curl -X POST http://localhost:8080/v1/vessels/ingest

# List vessels
curl http://localhost:8080/v1/vessels | jq
```

---

## 📊 **Current State**

- ✅ **Code**: Committed and pushed
- ✅ **CI/CD**: Workflow triggered, building image
- ⏳ **Image**: Building (~5-10 min)
- ⏳ **K8s**: StatefulSet configured, waiting for image
- ⏳ **Database**: Currently using `postgres:16-alpine` (temporary)

---

## 🔍 **Troubleshooting**

### **Image Pull Errors**

**Error**: `403 Forbidden` or `ImagePullBackOff`

- **Solution**: Make repository public OR create imagePullSecrets

**Error**: `Image not found`

- **Solution**: Wait for GitHub Actions build to complete

### **PostGIS Extension Errors**

**Error**: `extension "postgis" is not available`

- **Solution**: Verify PostGIS was compiled correctly in Docker image
- **Check**: `kubectl exec -n floodsight postgres-0 -- ls /usr/local/share/postgresql/extension/ | grep postgis`

### **Migration Errors**

**Error**: `relation "vessel_detections" already exists`

- **Solution**: Migration already applied, this is normal

---

## 📝 **Files Changed**

1. `backend/Dockerfile.db` - PostGIS compilation
2. `.github/workflows/postgres-postgis-ci.yml` - CI/CD workflow
3. `deploy/k8s/base/postgres-statefulset.yaml` - Kubernetes manifest
4. `deploy/k8s/base/kustomization.yaml` - Added postgres-statefulset

---

## 🎯 **Summary**

Everything is set up and aligned with your existing infrastructure! The GitHub Actions workflow is building the PostGIS image. Once it completes (~5-10 minutes), you can:

1. Make the repository public OR configure imagePullSecrets
2. Update the StatefulSet to use the new image
3. Verify PostGIS is working
4. Run migrations
5. Test vessel detection

**Check GitHub Actions**: https://github.com/afaqbabar/floodsight/actions
