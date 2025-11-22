# 🐳 Kubernetes PostGIS Setup - **Option 1 (Aligned with Existing Setup)**

## ✅ **Why Option 1 is Best**

Your existing infrastructure uses:
- ✅ **GitHub Actions CI/CD** for building Docker images
- ✅ **Multi-arch builds** (ARM64 + AMD64) via Docker Buildx
- ✅ **GHCR registry** (`ghcr.io/afaqbabar/floodsight-*`)
- ✅ **Kustomize** for Kubernetes manifests
- ✅ **FluxCD GitOps** for automated deployments

**Option 1 (Custom Docker Image)** matches this pattern perfectly!

---

## 🚀 **Implementation Steps**

### **1. Build and Push PostGIS Image**

The GitHub Actions workflow (`.github/workflows/postgres-postgis-ci.yml`) will automatically:
- Build PostGIS-enabled PostgreSQL image
- Push to `ghcr.io/afaqbabar/floodsight-postgres-postgis:latest`
- Support ARM64 (Raspberry Pi) + AMD64

**Trigger the build:**
```bash
# Push changes or manually trigger workflow
git add backend/Dockerfile.db .github/workflows/postgres-postgis-ci.yml
git commit -m "Add PostGIS Docker image build"
git push origin main
```

**Or manually trigger:**
- Go to GitHub Actions → "PostGIS Database Image CI/CD" → "Run workflow"

---

### **2. Update Kubernetes StatefulSet**

The new `deploy/k8s/base/postgres-statefulset.yaml` uses the PostGIS image:

```yaml
image: ghcr.io/afaqbabar/floodsight-postgres-postgis:latest
```

**Apply to cluster:**
```bash
kubectl apply -k deploy/k8s/base
```

**Or let FluxCD sync automatically** (if GitOps is configured).

---

### **3. Verify PostGIS Installation**

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

---

### **4. Run Database Migration**

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pods -n floodsight -l component=backend -o jsonpath='{.items[0].metadata.name}')

# Run Alembic migration
kubectl exec -n floodsight $BACKEND_POD -- alembic upgrade head
```

---

### **5. Test Vessel Detection**

```bash
# Port-forward backend service
kubectl port-forward -n floodsight svc/floodsight-backend 8080:8080

# In another terminal, test vessel detection
curl -X POST http://localhost:8080/v1/vessels/ingest

# List vessels
curl http://localhost:8080/v1/vessels | jq
```

---

## 📊 **What Changed**

### **Files Created/Modified:**

1. ✅ **`backend/Dockerfile.db`** - Updated to PostgreSQL 16 + PostGIS compilation
2. ✅ **`.github/workflows/postgres-postgis-ci.yml`** - CI/CD workflow for PostGIS image
3. ✅ **`deploy/k8s/base/postgres-statefulset.yaml`** - Kubernetes StatefulSet using PostGIS image
4. ✅ **`deploy/k8s/base/kustomization.yaml`** - Added postgres-statefulset.yaml to resources

---

## ⚠️ **Build Time Note**

Compiling PostGIS from source takes **~5-10 minutes** per build. This is acceptable because:
- ✅ Builds are cached via GitHub Actions cache
- ✅ Only rebuilds when `Dockerfile.db` changes
- ✅ Multi-arch builds run in parallel
- ✅ Production-ready and version-controlled

**Alternative (faster builds):** If you're okay upgrading to PostgreSQL 17, we can use Alpine's PostGIS package directly (builds in ~1 minute).

---

## 🔄 **GitOps Integration**

If FluxCD is configured, it will automatically:
1. Detect new PostGIS image tags
2. Update StatefulSet with new image
3. Roll out changes to cluster

**Check FluxCD status:**
```bash
flux get images -n floodsight
flux get kustomizations -n floodsight
```

---

## ✅ **Status**

- ✅ **Dockerfile updated** (PostgreSQL 16 + PostGIS)
- ✅ **CI/CD workflow created** (matches your existing pattern)
- ✅ **Kubernetes manifest created** (uses GHCR image)
- ⏳ **Waiting for**: Image build + cluster deployment

---

## 🎯 **Next Steps**

1. **Push changes** to trigger GitHub Actions build
2. **Wait for image** to be built and pushed to GHCR
3. **Apply Kubernetes manifests** (or let FluxCD sync)
4. **Verify PostGIS** is working
5. **Run migrations** to create vessel_detections table
6. **Test vessel detection** API endpoints

**Everything is aligned with your existing CI/CD and GitOps setup!** 🚀
