# 🔒 Fix Image Pull Authentication Issue

## 🚨 Problem

Your Kubernetes cluster can't pull the backend image because the GitHub Container Registry repository is **private**:

```
Error: 401 Unauthorized
Repository: ghcr.io/afaqbabar/floodsight-backend
```

The pods are using the **old cached image** from Nov 13 (no vessel detection code).

---

## ✅ Solution: Make Repository Public (Recommended)

### **Step 1: Go to GHCR Package Settings**

🔗 https://github.com/users/afaqbabar/packages/container/floodsight-backend/settings

### **Step 2: Change Visibility**

1. Scroll down to "**Danger Zone**"
2. Click "**Change visibility**"
3. Select "**Public**"
4. Type the repository name to confirm
5. Click "**I understand, change package visibility**"

### **Step 3: Restart Pods**

```bash
# Delete pods to pull fresh image
kubectl delete pods -n floodsight -l component=backend

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -n floodsight -l component=backend --timeout=120s

# Verify new image
BACKEND_POD=$(kubectl get pods -n floodsight -l component=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n floodsight $BACKEND_POD -- ls -la /app/app/services/sentinel1.py
```

---

## 🔐 Alternative: Use imagePullSecret (If Keeping Private)

### **Step 1: Create GitHub Personal Access Token**

1. Go to: https://github.com/settings/tokens
2. Click "**Generate new token (classic)**"
3. Select scopes:
   - ✅ `read:packages` - Download packages from GitHub Package Registry
4. Click "**Generate token**"
5. **Copy the token** (you won't see it again!)

### **Step 2: Create Kubernetes Secret**

```bash
# Replace <YOUR_GITHUB_PAT> with your token
kubectl create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=afaqbabar \
  --docker-password=<YOUR_GITHUB_PAT> \
  --docker-email=your@email.com \
  -n floodsight

# Verify secret
kubectl get secret ghcr-creds -n floodsight
```

### **Step 3: Update Deployment**

```bash
# Add imagePullSecrets to deployment
kubectl patch deployment floodsight-backend -n floodsight -p '{
  "spec": {
    "template": {
      "spec": {
        "imagePullSecrets": [{"name": "ghcr-creds"}]
      }
    }
  }
}'

# Also update scheduler
kubectl patch deployment floodsight-scheduler -n floodsight -p '{
  "spec": {
    "template": {
      "spec": {
        "imagePullSecrets": [{"name": "ghcr-creds"}]
      }
    }
  }
}'

# Delete pods to pull fresh image
kubectl delete pods -n floodsight -l component=backend
kubectl delete pods -n floodsight -l component=scheduler
```

---

## ✅ Verify Success

After either solution:

```bash
# 1. Check pods are running
kubectl get pods -n floodsight -l component=backend

# 2. Verify sentinel1.py exists
BACKEND_POD=$(kubectl get pods -n floodsight -l component=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n floodsight $BACKEND_POD -- ls -la /app/app/services/sentinel1.py

# Expected output:
# -rw-r--r-- 1 floodsight floodsight 7384 Nov 19 XX:XX /app/app/services/sentinel1.py

# 3. Test vessel detection
kubectl port-forward -n floodsight svc/floodsight-backend 8081:8080 &
curl -X POST http://localhost:8081/v1/vessels/ingest | jq

# Expected output:
# {
#   "status": "success",
#   "message": "Detected 118 vessels",
#   "vessels_detected": 118
# }
```

---

## 🎯 Recommendation

**Use Option 1 (Make Public)** because:

- ✅ Simpler setup
- ✅ No secrets to manage
- ✅ Works immediately
- ✅ Standard for open-source projects

**Use Option 2 (imagePullSecret)** if:

- 🔒 Repository must stay private
- 🔒 Contains proprietary code
- 🔒 Enterprise/compliance requirements

---

## 📊 Current Status

- ✅ Backend code committed and pushed
- ✅ Docker image built successfully (GitHub Actions)
- ✅ Image pushed to GHCR
- ❌ **Kubernetes can't pull image (401 Unauthorized)**
- ⏳ **Waiting for: Repository visibility change OR imagePullSecret**

---

## 🚀 After Fix

Once authentication is resolved:

1. Pods will pull the new image
2. Vessel detection endpoints will work
3. You can test with `curl -X POST .../v1/vessels/ingest`
4. Maritime monitoring is live! 🛰️🚢
