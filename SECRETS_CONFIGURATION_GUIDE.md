# 🔐 Secrets Configuration Guide

## Choose Your Scenario

### 📋 **Scenario 1: Minimal Setup (Testing/Development)** ⭐ RECOMMENDED TO START

Use this to quickly test if the deployment works with fake data.

**Copy this entire block to your `base/backend-secrets.yaml`:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: floodsight-backend-secrets
  namespace: floodsight
  labels:
    app: floodsight
    component: backend
type: Opaque
stringData:
  # Database - will be auto-created by deploy script
  database-url: "postgresql+asyncpg://postgres:postgres@postgres.floodsight.svc.cluster.local:5432/floodsight"
  
  # All other fields are optional - backend will use fake data
  cds-api-key: "fake-key-for-testing"
```

**What this gives you:**
- ✅ Works immediately
- ✅ Uses PostgreSQL deployed in K8s (script will deploy it for you)
- ✅ Uses fake forecast data (no CDS API needed)
- ✅ Perfect for testing the deployment

---

### 📋 **Scenario 2: With Real GloFAS Data**

Use this if you've registered for ECMWF CDS and want real flood data.

**First, get your CDS API key:**
1. Register: https://cds.climate.copernicus.eu/
2. Accept license: https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-glofas-forecast
3. Get API key from your profile (format: `UID:API_KEY`)

**Then use this:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: floodsight-backend-secrets
  namespace: floodsight
  labels:
    app: floodsight
    component: backend
type: Opaque
stringData:
  # Database
  database-url: "postgresql+asyncpg://postgres:postgres@postgres.floodsight.svc.cluster.local:5432/floodsight"
  
  # ECMWF CDS API - REPLACE WITH YOUR ACTUAL VALUES
  cds-api-key: "12345:abcd1234-ef56-7890-ghij-klmnopqrstuv"  # ← Your UID:API_KEY
  cds-api-url: "https://cds.climate.copernicus.eu/api/v2"
```

---

### 📋 **Scenario 3: External PostgreSQL Database**

Use this if you have an existing PostgreSQL database outside of K8s.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: floodsight-backend-secrets
  namespace: floodsight
  labels:
    app: floodsight
    component: backend
type: Opaque
stringData:
  # External Database - REPLACE WITH YOUR VALUES
  database-url: "postgresql+asyncpg://your_user:your_password@your_db_host:5432/floodsight"
  
  # Optional: Real data
  cds-api-key: "fake-key-for-testing"  # Or your real CDS key
```

**Example for local Raspberry Pi PostgreSQL:**
```yaml
database-url: "postgresql+asyncpg://postgres:mypassword@192.168.1.100:5432/floodsight"
```

---

## 🚀 Step-by-Step Instructions

### **For First-Time Setup (Recommended: Scenario 1)**

```bash
# Step 1: Go to the right directory
cd /home/lenovo/scrimba/floodsight/deploy/k8s

# Step 2: Create the secrets file
cat > base/backend-secrets.yaml << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: floodsight-backend-secrets
  namespace: floodsight
  labels:
    app: floodsight
    component: backend
type: Opaque
stringData:
  database-url: "postgresql+asyncpg://postgres:postgres@postgres.floodsight.svc.cluster.local:5432/floodsight"
  cds-api-key: "fake-key-for-testing"
EOF

# Step 3: Verify the file was created
cat base/backend-secrets.yaml

# Step 4: Apply the secrets (do this after the namespace is created)
# The deploy script will create the namespace for you
kubectl create namespace floodsight --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f base/backend-secrets.yaml

# Step 5: Deploy the backend
./deploy-backend.sh
```

---

## 🔍 Understanding the Database URL

The database URL format is:
```
postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
```

**Examples:**

| Scenario | URL |
|----------|-----|
| **K8s PostgreSQL** | `postgresql+asyncpg://postgres:postgres@postgres.floodsight.svc.cluster.local:5432/floodsight` |
| **Local Raspberry Pi** | `postgresql+asyncpg://postgres:mypass@192.168.1.5:5432/floodsight` |
| **External server** | `postgresql+asyncpg://user:pass@db.example.com:5432/floodsight` |
| **Docker Compose** | `postgresql+asyncpg://postgres:postgres@db:5432/floodsight` |

---

## 📝 Quick Edit Method

If you prefer to edit manually:

```bash
cd /home/lenovo/scrimba/floodsight/deploy/k8s

# Copy template
cp base/backend-secrets.yaml.example base/backend-secrets.yaml

# Edit with nano
nano base/backend-secrets.yaml

# Find this line (around line 22):
# database-url: "postgresql+asyncpg://postgres:password@postgres-service:5432/floodsight"

# Change it to:
# database-url: "postgresql+asyncpg://postgres:postgres@postgres.floodsight.svc.cluster.local:5432/floodsight"

# Save and exit: Ctrl+X, then Y, then Enter
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Wrong:** `database-url: postgresql://postgres:postgres@...`  
✅ **Correct:** `database-url: postgresql+asyncpg://postgres:postgres@...`

❌ **Wrong:** `@postgres-service:5432` (old placeholder)  
✅ **Correct:** `@postgres.floodsight.svc.cluster.local:5432` (correct K8s DNS)

❌ **Wrong:** Forgetting quotes around the URL  
✅ **Correct:** `database-url: "postgresql+asyncpg://..."`

---

## 🧪 Test Your Secrets

After creating the secrets file:

```bash
# Check the file exists
ls -lh base/backend-secrets.yaml

# Preview the contents (safe - just YAML)
cat base/backend-secrets.yaml

# Apply to K8s
kubectl apply -f base/backend-secrets.yaml

# Verify it was created
kubectl get secret floodsight-backend-secrets -n floodsight

# Check the database URL is set (won't show actual value)
kubectl describe secret floodsight-backend-secrets -n floodsight
```

---

## 🎯 Recommended Path for You

Since you're just getting started, I recommend:

1. **Use Scenario 1** (Minimal Setup with fake data)
2. **Let the deploy script create PostgreSQL for you**
3. **Test that everything deploys**
4. **Later upgrade to real GloFAS data** (Scenario 2)

---

## 📚 What You DON'T Need to Configure (Optional)

These are all **optional** and the backend works fine without them:

- ❌ `supabase-*` - Only if you want JWT authentication
- ❌ `smtp-*` - Only if you want email notifications
- ❌ `twilio-*` - Only if you want SMS notifications
- ❌ `fcm-*` - Only if you want push notifications
- ❌ `cds-api-key` - Can use fake data initially

**Only `database-url` is required!**

---

## ✅ Ready to Deploy?

Once you've created `base/backend-secrets.yaml` with at minimum the `database-url`, you can run:

```bash
cd /home/lenovo/scrimba/floodsight/deploy/k8s
./deploy-backend.sh
```

The script will:
1. ✅ Create namespace
2. ✅ Check for secrets (you just created them!)
3. ✅ Ask if you want to deploy PostgreSQL (say **yes**)
4. ✅ Deploy backend
5. ✅ Run migrations
6. ✅ Test deployment

---

## 🆘 Still Confused?

**Just copy-paste this complete command:**

```bash
cd /home/lenovo/scrimba/floodsight/deploy/k8s && \
cat > base/backend-secrets.yaml << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: floodsight-backend-secrets
  namespace: floodsight
  labels:
    app: floodsight
    component: backend
type: Opaque
stringData:
  database-url: "postgresql+asyncpg://postgres:postgres@postgres.floodsight.svc.cluster.local:5432/floodsight"
  cds-api-key: "fake-key-for-testing"
EOF
echo "✅ Secrets file created!" && \
echo "📝 Location: $(pwd)/base/backend-secrets.yaml" && \
echo "🚀 Now run: ./deploy-backend.sh"
```

This single command will create the secrets file with working values for you!

---

**Now you have all the information you need!** 🎉

