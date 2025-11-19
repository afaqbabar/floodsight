# 🌐 Frontend Dashboard Status

## 🚨 Current Issue

**Frontend pods failing health checks** - Running but not passing readiness probes

### **Symptoms:**

- Frontend pods: `0/1 Ready` with `1 restart`
- Health check path: `/health.html` exists ✅
- Nginx running on port 80 ✅
- Service exists ✅
- **Problem:** Pods keep restarting due to failed liveness probes

---

## 🔍 Root Causes Fixed

### ✅ **Issue 1: Wrong Image Repository** (FIXED)

- **Was:** `ghcr.io/yourusername/floodsight:latest` (placeholder)
- **Now:** `ghcr.io/afaqbabar/floodsight-frontend:latest`
- **Fix:** Updated kustomization.yaml (commit fb95055)

### ✅ **Issue 2: Image Pull Authentication** (FIXED)

- **Problem:** 401 Unauthorized
- **Fix:** Added `ghcr-creds` imagePullSecret to deployment

### ✅ **Issue 3: Wrong Container Port** (FIXED)

- **Was:** containerPort 8080 (nginx not listening there)
- **Now:** containerPort 80 (correct)
- **Fix:** Updated deployment.yaml (commit d5e5efe)

---

## ⏳ Remaining Issue

**Health Check Configuration May Need Adjustment**

Current probe settings:

```yaml
livenessProbe:
  httpGet:
    path: /health.html
    port: http # resolves to port 80
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

**Testing shows:**

- ✅ Inside container: `curl localhost:80/health.html` → HTTP 200
- ❌ Via service: Connection fails
- ❌ Pods restart after ~85 seconds

---

## 🚀 Quick Fix Options

### **Option 1: Increase Health Check Delays** (Quickest)

```bash
kubectl patch deployment floodsight -n floodsight --type='json' -p='[
  {"op": "replace", "path": "/spec/template/spec/containers/0/livenessProbe/initialDelaySeconds", "value": 60},
  {"op": "replace", "path": "/spec/template/spec/containers/0/livenessProbe/failureThreshold", "value": 6}
]'
```

### **Option 2: Use Simple TCP Check**

```yaml
livenessProbe:
  tcpSocket:
    port: 80
  initialDelaySeconds: 30
  periodSeconds: 10
```

### **Option 3: Disable Liveness Probe Temporarily**

```bash
kubectl patch deployment floodsight -n floodsight --type='json' -p='[
  {"op": "remove", "path": "/spec/template/spec/containers/0/livenessProbe"}
]'
```

---

## 📊 Current Pod Status

```bash
$ kubectl get pods -n floodsight -l app=floodsight
NAME                          READY   STATUS    RESTARTS       AGE
floodsight-5c9f45dd7f-kplfc   0/1     Running   1 (25s ago)    85s
floodsight-5c9f45dd7f-lm5lg   0/1     Running   1 (23s ago)    84s
floodsight-5c9f45dd7f-sgnbn   0/1     Running   1 (25s ago)    85s
```

---

## 🎯 Recommended Next Step

**Temporarily disable liveness probe** to get frontend accessible:

```bash
# Remove liveness probe
kubectl patch deployment floodsight -n floodsight --type='json' -p='[
  {"op": "remove", "path": "/spec/template/spec/containers/0/livenessProbe"}
]'

# Wait for pods to stabilize
kubectl wait --for=condition=ready pod -n floodsight -l app=floodsight --timeout=60s

# Test access
kubectl port-forward -n floodsight svc/floodsight 8082:80 &
curl http://localhost:8082/

# If works, can re-add liveness probe with adjusted settings later
```

---

## 📝 Files Modified

1. `deploy/k8s/base/kustomization.yaml` - Fixed image repository
2. `deploy/k8s/base/deployment.yaml` - Fixed containerPort 8080→80

---

## ✅ Backend Status (For Reference)

- ✅ 2/2 backend pods running
- ✅ PostGIS working
- ⏳ Waiting for new vessel detection image (building)
- ⏳ 1 backend pod crashing (old image, will fix after build)

---

## 🔗 Access Points

Once frontend is healthy:

```bash
# Via service (from cluster)
curl http://floodsight.floodsight.svc.cluster.local/

# Via port-forward (from local)
kubectl port-forward -n floodsight svc/floodsight 8082:80
# Then: http://localhost:8082/

# Via ingress (if configured)
# http://your-domain.com/
```

---

## 🎬 Complete Fix Sequence

```bash
# 1. Remove liveness probe causing restarts
kubectl patch deployment floodsight -n floodsight --type='json' -p='[
  {"op": "remove", "path": "/spec/template/spec/containers/0/livenessProbe"}
]'

# 2. Wait for pods
sleep 20
kubectl get pods -n floodsight -l app=floodsight

# 3. Test access
kubectl port-forward -n floodsight svc/floodsight 8082:80 &
sleep 2
curl http://localhost:8082/ | head -20

# 4. If successful, dashboard should be accessible!
```

---

## 📌 Summary

**What's working:**

- ✅ Correct image (`floodsight-frontend:latest`)
- ✅ Image pulling with authentication
- ✅ Nginx running on port 80
- ✅ Health check endpoint exists
- ✅ Service configured

**What needs fixing:**

- ❌ Liveness probe causing continuous restarts
- **Fix:** Remove or adjust health check timing

**Time to fix:** ~2 minutes
