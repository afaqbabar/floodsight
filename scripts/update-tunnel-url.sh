#!/bin/bash
# Script to update Cloudflare tunnel URL in CI/CD workflows and backend config
# Usage: ./scripts/update-tunnel-url.sh

set -e

# Get the current tunnel URL from logs
TUNNEL_URL=$(sudo grep -Eo "https://[a-z0-9-]+\.trycloudflare\.com" /var/log/cloudflared-tunnel.log | tail -1)

if [ -z "$TUNNEL_URL" ]; then
    echo "❌ Could not find tunnel URL in logs"
    exit 1
fi

echo "🔍 Found tunnel URL: $TUNNEL_URL"

# Update CI workflow
sed -i "s|https://[a-z0-9-]*\.trycloudflare\.com/v1|${TUNNEL_URL}/v1|g" .github/workflows/ci.yml
echo "✅ Updated .github/workflows/ci.yml"

# Update build-and-push workflow
sed -i "s|https://[a-z0-9-]*\.trycloudflare\.com/v1|${TUNNEL_URL}/v1|g" .github/workflows/build-and-push.yml
echo "✅ Updated .github/workflows/build-and-push.yml"

# Update backend CORS config
sed -i "s|https://[a-z0-9-]*\.trycloudflare\.com|${TUNNEL_URL}|g" deploy/k8s/base/backend-configmap.yaml
echo "✅ Updated deploy/k8s/base/backend-configmap.yaml"

echo ""
echo "📝 Changes made. To apply:"
echo "  1. Review changes: git diff"
echo "  2. Commit: git add . && git commit -m 'chore: update cloudflare tunnel url'"
echo "  3. Push: git push origin main"
echo "  4. Apply backend config: kubectl apply -f deploy/k8s/base/backend-configmap.yaml"
echo "  5. Restart backend: kubectl rollout restart deployment floodsight-backend -n floodsight"

