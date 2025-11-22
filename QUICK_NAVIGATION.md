# 🧭 Quick Navigation Guide

## 📁 Directory Structure

```
/home/lenovo/scrimba/floodsight/
├── backend/                    # Backend code & local testing
│   ├── test-local.sh          # Run from here or project root
│   ├── docker-compose.yml     # Backend services config
│   └── app/                   # FastAPI application
│
└── deploy/                    # Deployment files
    └── k8s/                   # ← YOU NEED TO BE HERE for K8s
        ├── deploy-backend.sh  # K8s deployment script
        └── base/
            ├── backend-secrets.yaml.example  # ← Template file
            └── backend-secrets.yaml          # ← Your secrets (create this)
```

---

## ⚡ Quick Commands

### **For Local Testing:**
```bash
# From anywhere:
cd /home/lenovo/scrimba/floodsight
./backend/test-local.sh
```

### **For K8s Deployment:**
```bash
# Step 1: Navigate to k8s directory
cd /home/lenovo/scrimba/floodsight/deploy/k8s

# Step 2: Copy secrets template
cp base/backend-secrets.yaml.example base/backend-secrets.yaml

# Step 3: Edit secrets
nano base/backend-secrets.yaml

# Step 4: Deploy
./deploy-backend.sh
```

---

## 🎯 Where to Run Each Script

| Script | Where to Run | Command |
|--------|--------------|---------|
| **Local Testing** | Anywhere in project | `./backend/test-local.sh` |
| **K8s Deployment** | `deploy/k8s/` | `./deploy-backend.sh` |
| **GloFAS Test** | Anywhere in project | `./backend/test-glofas-integration.sh` |
| **API Testing** | Anywhere in project | `./backend/test-api-comprehensive.sh` |
| **Health Monitor** | Anywhere in project | `./backend/monitor-health.sh` |

---

## 🔧 Current Issue Fix

**Problem:** You're in `/deploy` but need to be in `/deploy/k8s`

**Solution:**
```bash
# From where you are now (/deploy):
cd k8s
cp base/backend-secrets.yaml.example base/backend-secrets.yaml

# Or use absolute path:
cd /home/lenovo/scrimba/floodsight/deploy/k8s
cp base/backend-secrets.yaml.example base/backend-secrets.yaml
```

---

## 📝 Editing Secrets

After copying the template:

```bash
# Edit the secrets file
nano base/backend-secrets.yaml

# Minimum required changes:
# 1. Update database-url with your PostgreSQL connection string
# 2. (Optional) Add CDS API key for real GloFAS data
# 3. Save and exit (Ctrl+X, then Y, then Enter)

# Apply the secrets
kubectl apply -f base/backend-secrets.yaml
```

---

## 🚀 Complete K8s Deployment Flow

```bash
# Step 1: Go to the right directory
cd /home/lenovo/scrimba/floodsight/deploy/k8s

# Step 2: Check you're in the right place
pwd
# Should show: /home/lenovo/scrimba/floodsight/deploy/k8s

# Step 3: Copy secrets template
cp base/backend-secrets.yaml.example base/backend-secrets.yaml

# Step 4: Edit secrets (minimal: just database URL)
nano base/backend-secrets.yaml
# Change: postgresql+asyncpg://postgres:password@postgres:5432/floodsight

# Step 5: Apply secrets
kubectl apply -f base/backend-secrets.yaml

# Step 6: Deploy backend
./deploy-backend.sh

# Step 7: Check status
kubectl get pods -n floodsight
```

---

## 💡 Pro Tips

### Always Know Where You Are
```bash
pwd  # Print Working Directory
```

### List Files in Current Directory
```bash
ls -la
```

### Check if Script Exists
```bash
ls -lh deploy-backend.sh
# If you see it, you're in the right place!
```

### Go Back to Project Root
```bash
cd /home/lenovo/scrimba/floodsight
```

---

## 🎯 Quick Reference

| I want to... | Go here first |
|--------------|---------------|
| Test backend locally | `cd /home/lenovo/scrimba/floodsight` |
| Deploy to K8s | `cd /home/lenovo/scrimba/floodsight/deploy/k8s` |
| Edit backend code | `cd /home/lenovo/scrimba/floodsight/backend` |
| View Docker Compose logs | `cd /home/lenovo/scrimba/floodsight/backend` |
| Run API tests | Anywhere, script handles it |

---

## ✅ Verify Your Location

Run this to see where you are and what's available:

```bash
# Check current directory
echo "📍 You are here:"
pwd

echo ""
echo "📁 Files in current directory:"
ls -lh

echo ""
echo "🔍 Looking for deployment scripts..."
find . -name "*.sh" -type f 2>/dev/null | head -5
```

---

**Now you know exactly where to go!** 🎯

