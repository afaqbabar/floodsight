# FluxCD Bootstrap

Bootstrap Flux on your cluster once:

```bash
curl -s https://fluxcd.io/install.sh | sudo bash
flux bootstrap github \
  --owner=afaqbabar \
  --repository=floodsight \
  --branch=main \
  --path=deploy/k8s/overlays/prod \
  --personal
```

This will:
- Install Flux controllers in your cluster
- Configure Flux to watch the repository
- Automatically sync and deploy changes
- Enable image automation to update prod overlay with new semver tags

