# 🌍 Setup with Real GloFAS Data

## Your CDS API Key Format

Your CDS API key should look like:

```
UID:API_KEY
```

Example: `12345:abcd1234-ef56-7890-ghij-klmnopqrstuv`

**Where to find it:**

1. Go to: https://cds.climate.copernicus.eu/user
2. Scroll down to "API key" section
3. Copy both the UID and API key
4. Format: `UID:API_KEY` (separated by colon, no spaces)

---

## 🚀 Create Secrets with Real Data

Replace `YOUR_UID:YOUR_API_KEY` with your actual credentials:

```bash
cd /home/lenovo/scrimba/floodsight/deploy/k8s

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
  # Database - PostgreSQL in K8s
  database-url: "postgresql+asyncpg://postgres:postgres@postgres.floodsight.svc.cluster.local:5432/floodsight"

  # ECMWF CDS API - REPLACE WITH YOUR ACTUAL VALUES
  cds-api-key: "YOUR_UID:YOUR_API_KEY"
  cds-api-url: "https://cds.climate.copernicus.eu/api/v2"
EOF

echo "✅ Secrets file created with real CDS credentials!"
```

**IMPORTANT:** Replace `YOUR_UID:YOUR_API_KEY` with your actual credentials!

---

## 📝 Example with Real Credentials

If your CDS credentials are:

- UID: `123456`
- API Key: `abcd1234-5678-90ef-ghij-klmnopqrstuv`

Then use:

```bash
cd /home/lenovo/scrimba/floodsight/deploy/k8s

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
  cds-api-key: "123456:abcd1234-5678-90ef-ghij-klmnopqrstuv"
  cds-api-url: "https://cds.climate.copernicus.eu/api/v2"
EOF
```

---

## 🔐 Secure Method (Manual Edit)

If you prefer not to have your credentials in command history:

```bash
cd /home/lenovo/scrimba/floodsight/deploy/k8s

# Copy template
cp base/backend-secrets.yaml.example base/backend-secrets.yaml

# Edit with nano
nano base/backend-secrets.yaml
```

**Find these lines (around line 22 and 33):**

```yaml
database-url: 'postgresql+asyncpg://postgres:password@postgres-service:5432/floodsight'

cds-api-key: '<your-cds-api-key>'
```

**Change to:**

```yaml
database-url: 'postgresql+asyncpg://postgres:postgres@postgres.floodsight.svc.cluster.local:5432/floodsight'

cds-api-key: 'YOUR_UID:YOUR_API_KEY'
```

Save: `Ctrl+X`, then `Y`, then `Enter`

---

## ✅ Verify Configuration

After creating the secrets:

```bash
# Check file exists
ls -lh base/backend-secrets.yaml

# Verify it has your CDS key (will show in plaintext - be careful!)
grep "cds-api-key" base/backend-secrets.yaml
# Should show: cds-api-key: "YOUR_UID:YOUR_API_KEY"
```

---

## 🚀 Deploy with Real Data

Now deploy:

```bash
cd /home/lenovo/scrimba/floodsight/deploy/k8s

# Apply secrets
kubectl create namespace floodsight --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f base/backend-secrets.yaml

# Deploy backend
./deploy-backend.sh
```

**When asked about PostgreSQL, say `y` (yes)**

---

## 🌍 What Happens with Real Data

Once deployed, the backend will:

1. ✅ Connect to ECMWF CDS API every hour
2. ✅ Download real GloFAS forecast data
3. ✅ Process discharge forecasts for all stations
4. ✅ Store in PostgreSQL
5. ✅ Compute flood alerts based on real data
6. ✅ Update automatically

**First ingestion may take 5-15 minutes** (CDS API processing time)

---

## 📊 Verify Real Data After Deployment

```bash
# Check scheduler logs (wait ~5 minutes after deployment)
kubectl logs -f -l component=scheduler -n floodsight

# Look for:
# ✅ "Attempting real GloFAS ingestion via ECMWF CDS..."
# ✅ "Successfully ingested X forecasts from real GloFAS data"

# Check data source
kubectl port-forward -n floodsight svc/floodsight-backend 8080:8080 &
curl http://localhost:8080/v1/forecasts | jq '.[0].source'
# Should show: "GloFAS"
```

---

## ⚠️ Important Checklist

Before deploying with real data, make sure:

- [ ] You have registered at https://cds.climate.copernicus.eu/
- [ ] You have accepted the GloFAS license (VERY IMPORTANT!)
  - Go to: https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-glofas-forecast
  - Scroll down and click "Accept terms"
- [ ] You have your UID and API key from your profile
- [ ] Your credentials are in format: `UID:API_KEY` (with colon, no spaces)
- [ ] You've updated `base/backend-secrets.yaml` with your real credentials

---

## 🔍 Troubleshooting Real Data

### Error: "Invalid API key"

- Check format is `UID:API_KEY` with colon
- No spaces before or after
- No quotes inside the credentials

### Error: "You have not accepted the license"

- Visit: https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-glofas-forecast
- Scroll down and click "Accept terms"
- Wait a few minutes
- Try again

### Timeout errors

- CDS API can be slow (5-15 minutes)
- Check queue: https://cds.climate.copernicus.eu/live/queue
- Try during off-peak hours (nighttime in Europe)

### Still getting fake data

- Check scheduler logs: `kubectl logs -l component=scheduler -n floodsight`
- Verify secrets were applied: `kubectl get secret -n floodsight`
- Check CDS API key is set: `kubectl describe secret floodsight-backend-secrets -n floodsight`

---

## 📈 Real vs Fake Data Comparison

| Feature          | Fake Data    | Real Data             |
| ---------------- | ------------ | --------------------- |
| **Setup Time**   | Instant      | 5-15 min first run    |
| **Data Quality** | Random       | ECMWF NWP             |
| **Updates**      | Each run     | Hourly from CDS       |
| **Requirements** | None         | CDS account + license |
| **Cost**         | Free         | Free (non-commercial) |
| **Accuracy**     | Testing only | Production-ready      |

---

## 🎯 Ready to Deploy with Real Data!

Once you've created `base/backend-secrets.yaml` with your real CDS credentials:

```bash
cd /home/lenovo/scrimba/floodsight/deploy/k8s
./deploy-backend.sh
```

Your FloodSight backend will now ingest real global flood forecasts from ECMWF! 🌍🚀

---

## 🆘 Need Your Credentials?

**Get your CDS API key:**

```bash
# Open your browser to:
https://cds.climate.copernicus.eu/user

# Scroll down to "API key" section
# You'll see:
#   UID: 123456
#   API Key: abcd1234-5678-90ef-ghij-klmnopqrstuv

# Format for secrets:
# cds-api-key: "123456:abcd1234-5678-90ef-ghij-klmnopqrstuv"
```

---

**You're all set to use real flood forecast data!** 🌊📊
