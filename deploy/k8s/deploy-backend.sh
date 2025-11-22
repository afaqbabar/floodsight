#!/bin/bash
# FloodSight Backend - K3s/K8s Deployment Script
# Automates the deployment of FloodSight backend to Kubernetes

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="floodsight"
DEPLOYMENT_NAME="floodsight-backend"
SERVICE_NAME="floodsight-backend"
BACKEND_IMAGE="ghcr.io/afaqbabar/floodsight-backend:latest"
MAX_WAIT_TIME=300  # 5 minutes

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FloodSight Backend - K8s Deployment ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for deployment to be ready
wait_for_deployment() {
    local deployment=$1
    local namespace=$2
    local timeout=$3
    
    echo -e "${YELLOW}⏳ Waiting for deployment ${deployment} to be ready...${NC}"
    
    if kubectl wait --for=condition=available --timeout=${timeout}s \
        deployment/${deployment} -n ${namespace} 2>/dev/null; then
        echo -e "${GREEN}✅ Deployment is ready!${NC}"
        return 0
    else
        echo -e "${RED}❌ Deployment failed to become ready within ${timeout}s${NC}"
        return 1
    fi
}

# Function to wait for pods to be ready
wait_for_pods() {
    local label=$1
    local namespace=$2
    local timeout=$3
    
    echo -e "${YELLOW}⏳ Waiting for pods with label ${label} to be ready...${NC}"
    
    if kubectl wait --for=condition=ready pod -l ${label} \
        -n ${namespace} --timeout=${timeout}s 2>/dev/null; then
        echo -e "${GREEN}✅ Pods are ready!${NC}"
        return 0
    else
        echo -e "${RED}❌ Pods failed to become ready within ${timeout}s${NC}"
        return 1
    fi
}

# Step 0: Pre-flight checks
echo -e "${BLUE}Step 0: Running pre-flight checks...${NC}"

# Check if kubectl is installed
if ! command_exists kubectl; then
    echo -e "${RED}❌ kubectl is not installed. Please install kubectl first.${NC}"
    echo "Install: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
echo -e "${GREEN}✅ kubectl is installed${NC}"

# Check if kubectl can connect to cluster
if ! kubectl cluster-info > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to Kubernetes cluster.${NC}"
    echo "Please configure kubectl with your cluster credentials."
    exit 1
fi
echo -e "${GREEN}✅ Connected to Kubernetes cluster${NC}"

# Display cluster info
CLUSTER_NAME=$(kubectl config current-context)
echo -e "📍 Current context: ${BLUE}${CLUSTER_NAME}${NC}"

echo ""

# Step 1: Create namespace
echo -e "${BLUE}Step 1: Creating namespace...${NC}"
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✅ Namespace ${NAMESPACE} ready${NC}"
echo ""

# Step 2: Check for secrets
echo -e "${BLUE}Step 2: Checking for secrets...${NC}"

if kubectl get secret floodsight-backend-secrets -n ${NAMESPACE} > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Secrets already exist${NC}"
else
    echo -e "${YELLOW}⚠️  Secrets not found!${NC}"
    echo ""
    echo "You need to create secrets before proceeding."
    echo ""
    echo "1. Copy the template:"
    echo "   cp base/backend-secrets.yaml.example base/backend-secrets.yaml"
    echo ""
    echo "2. Edit the file with your actual values:"
    echo "   nano base/backend-secrets.yaml"
    echo ""
    echo "3. Apply the secrets:"
    echo "   kubectl apply -f base/backend-secrets.yaml -n ${NAMESPACE}"
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
    fi
fi
echo ""

# Step 3: Deploy PostgreSQL (optional)
echo -e "${BLUE}Step 3: Checking for PostgreSQL...${NC}"

if kubectl get statefulset postgres -n ${NAMESPACE} > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL already deployed${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL not found${NC}"
    read -p "Do you want to deploy PostgreSQL in K8s? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deploying PostgreSQL...${NC}"
        
        # Create postgres password secret
        kubectl create secret generic postgres-credentials \
            --from-literal=password=$(openssl rand -base64 32) \
            -n ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
        
        # Deploy PostgreSQL
        cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: ${NAMESPACE}
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_DB
          value: floodsight
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: ${NAMESPACE}
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
EOF
        
        echo -e "${GREEN}✅ PostgreSQL deployed${NC}"
        
        # Wait for PostgreSQL to be ready
        wait_for_pods "app=postgres" ${NAMESPACE} 120
    else
        echo -e "${YELLOW}Skipping PostgreSQL deployment (using external DB)${NC}"
    fi
fi
echo ""

# Step 4: Apply backend configuration
echo -e "${BLUE}Step 4: Applying backend configuration...${NC}"
kubectl apply -f base/backend-configmap.yaml -n ${NAMESPACE}
echo -e "${GREEN}✅ ConfigMap applied${NC}"
echo ""

# Step 5: Deploy backend application
echo -e "${BLUE}Step 5: Deploying backend application...${NC}"
kubectl apply -f base/backend-deployment.yaml -n ${NAMESPACE}
echo -e "${GREEN}✅ Backend deployment applied${NC}"
echo ""

# Step 6: Deploy backend services
echo -e "${BLUE}Step 6: Deploying backend services...${NC}"
kubectl apply -f base/backend-service.yaml -n ${NAMESPACE}
echo -e "${GREEN}✅ Backend services applied${NC}"
echo ""

# Step 7: Deploy backend ingress
echo -e "${BLUE}Step 7: Deploying backend ingress...${NC}"
kubectl apply -f base/backend-ingress.yaml -n ${NAMESPACE}
echo -e "${GREEN}✅ Backend ingress applied${NC}"
echo ""

# Step 8: Wait for deployment to be ready
echo -e "${BLUE}Step 8: Waiting for deployment to be ready...${NC}"

if ! wait_for_deployment ${DEPLOYMENT_NAME} ${NAMESPACE} ${MAX_WAIT_TIME}; then
    echo -e "${RED}Deployment failed. Checking logs...${NC}"
    kubectl logs -l component=backend -n ${NAMESPACE} --tail=50
    exit 1
fi
echo ""

# Step 9: Run database migrations
echo -e "${BLUE}Step 9: Running database migrations...${NC}"

POD_NAME=$(kubectl get pod -l component=backend -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD_NAME" ]; then
    echo -e "${RED}❌ No backend pod found${NC}"
    exit 1
fi

echo "Using pod: ${POD_NAME}"

kubectl exec ${POD_NAME} -n ${NAMESPACE} -- alembic upgrade head

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations complete${NC}"
else
    echo -e "${RED}❌ Migrations failed${NC}"
    exit 1
fi
echo ""

# Step 10: Seed sample data
echo -e "${BLUE}Step 10: Seeding sample data...${NC}"

read -p "Do you want to seed sample stations? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    kubectl exec ${POD_NAME} -n ${NAMESPACE} -- python -m app.services.seed
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Seeding complete${NC}"
    else
        echo -e "${YELLOW}⚠️  Seeding failed (may already exist)${NC}"
    fi
fi
echo ""

# Step 11: Display deployment status
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}       Deployment Status                ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get pods
echo -e "${YELLOW}📦 Pods:${NC}"
kubectl get pods -l app=floodsight,component=backend -n ${NAMESPACE}
echo ""

# Get services
echo -e "${YELLOW}🌐 Services:${NC}"
kubectl get svc -l component=backend -n ${NAMESPACE}
echo ""

# Get ingress
echo -e "${YELLOW}🔗 Ingress:${NC}"
kubectl get ingress floodsight-backend -n ${NAMESPACE}
echo ""

# Get LoadBalancer IP
LOADBALANCER_IP=$(kubectl get svc floodsight-backend-external -n ${NAMESPACE} \
    -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)

if [ -n "$LOADBALANCER_IP" ]; then
    echo -e "${GREEN}📍 LoadBalancer IP: ${LOADBALANCER_IP}${NC}"
    echo ""
    echo -e "${YELLOW}Configure DNS:${NC}"
    echo "  api.floodsight.com -> ${LOADBALANCER_IP}"
    echo ""
fi

# Step 12: Test deployment
echo -e "${BLUE}Step 12: Testing deployment...${NC}"

# Port-forward for testing
echo -e "${YELLOW}Setting up port-forward for testing...${NC}"
kubectl port-forward -n ${NAMESPACE} svc/${SERVICE_NAME} 8080:8080 > /dev/null 2>&1 &
PF_PID=$!

# Wait a moment for port-forward to establish
sleep 3

# Test health endpoint
if curl -s -f http://localhost:8080/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    
    # Get health response
    HEALTH=$(curl -s http://localhost:8080/v1/health)
    echo "Response: $HEALTH"
else
    echo -e "${RED}❌ Health check failed${NC}"
fi

# Kill port-forward
kill $PF_PID 2>/dev/null || true

echo ""

# Step 13: Display summary and next steps
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}     🎉 Deployment Complete! 🎉        ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}📊 Deployment Summary:${NC}"
echo "  • Namespace: ${NAMESPACE}"
echo "  • Image: ${BACKEND_IMAGE}"
echo "  • Replicas: 2 (backend) + 1 (scheduler)"
echo ""

echo -e "${YELLOW}🔧 Useful Commands:${NC}"
echo ""
echo "View pods:"
echo "  kubectl get pods -n ${NAMESPACE} -l component=backend"
echo ""
echo "View logs:"
echo "  kubectl logs -f -n ${NAMESPACE} -l component=backend"
echo ""
echo "View scheduler logs:"
echo "  kubectl logs -f -n ${NAMESPACE} -l component=scheduler"
echo ""
echo "Port-forward to test:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/${SERVICE_NAME} 8080:8080"
echo "  curl http://localhost:8080/v1/health"
echo ""
echo "Scale deployment:"
echo "  kubectl scale deployment ${DEPLOYMENT_NAME} -n ${NAMESPACE} --replicas=3"
echo ""
echo "Update image:"
echo "  kubectl set image deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE} backend=${BACKEND_IMAGE}"
echo ""
echo "Restart deployment:"
echo "  kubectl rollout restart deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE}"
echo ""

if [ -n "$LOADBALANCER_IP" ]; then
    echo -e "${YELLOW}🌐 Access URLs (after DNS configuration):${NC}"
    echo "  API Docs: https://api.floodsight.com/docs"
    echo "  Health: https://api.floodsight.com/v1/health"
    echo "  Metrics: https://api.floodsight.com/metrics"
    echo ""
fi

echo -e "${YELLOW}📚 Documentation:${NC}"
echo "  • Deployment Guide: deploy/k8s/README_BACKEND.md"
echo "  • API Docs: http://localhost:8080/docs (via port-forward)"
echo ""

echo -e "${GREEN}✅ Backend is deployed and running in Kubernetes!${NC}"

