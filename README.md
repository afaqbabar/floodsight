# FloodSight

> **See floods before they happen**  
> Real-time flood monitoring, forecasting, and alerting for resilient cities and businesses.

[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black)](https://floodsight.vercel.app/)

## 🌊 Overview

FloodSight is a European flood intelligence platform powered by ECMWF & Copernicus open data. This repository contains the landing page and early-access signup flow.

- **Live Demo**: [floodsight.vercel.app](https://floodsight.vercel.app/)
- **Repository**: [github.com/afaqbabar/floodsight](https://github.com/afaqbabar/floodsight)

---

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** (for Vite dev server, building, linting, testing)

### Local Development

```bash
# Clone repository
git clone https://github.com/afaqbabar/floodsight.git
cd floodsight

# Install dependencies
npm install

# Start development server (Vite)
npm run dev
# Opens at http://localhost:5173
```

### Project Structure

```
floodsight/
├── 📁 public/              # Static site content
│   ├── index.html          # Main landing page
│   ├── dashboard.html      # Simple dashboard
│   ├── dashboard-figma.html # Full Figma dashboard with Leaflet map & Chart.js
│   ├── impressum.html      # Legal imprint (DE)
│   ├── privacy.html        # Privacy policy (EN/DE)
│   ├── cookies.html        # Cookie policy (EN/DE)
│   ├── terms.html          # Terms of service
│   ├── security.html       # Security disclosure
│   ├── thanks.html         # Form success page
│   ├── health.html         # Health check dashboard
│   ├── 404.html            # Custom 404 page
│   ├── assets/
│   │   ├── css/
│   │   │   ├── tokens.css         # Auto-generated design tokens
│   │   │   ├── floodsight.css     # Main homepage styles
│   │   │   ├── dashboard.css      # Simple dashboard styles
│   │   │   ├── dashboard-figma.css # Figma dashboard styles
│   │   │   └── cookie-banner.css  # GDPR cookie banner
│   │   └── js/
│   │       ├── main.js     # Entry point (ES module)
│   │       ├── nav.js      # Navigation logic
│   │       ├── forms.js    # Form validation
│   │       ├── utils.js    # Utilities
│   │       └── dom.js      # DOM helpers
│   ├── components/         # Reusable UI components (NEW)
│   │   ├── site/
│   │   │   ├── SiteHeader.js
│   │   │   └── SiteFooter.js
│   │   ├── dashboard/
│   │   │   ├── SidebarFilters.js
│   │   │   ├── MapPanel.js
│   │   │   └── RightPanel.js
│   │   └── privacy/
│   │       └── CookieBanner.js
│   ├── lib/                # Utility libraries (NEW)
│   │   └── consent.js      # GDPR consent management
│   ├── logos/              # Brand logos
│   ├── sitemap.xml         # SEO sitemap
│   └── robots.txt          # Crawler directives
├── 📁 design/              # Design tokens (NEW)
│   ├── figma-tokens.json   # Source of truth from Figma
│   ├── tokens.js           # Token export module
│   └── README.md           # Design system docs
├── 📁 docs/                # Documentation
│   ├── TESTING.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DEVELOPMENT_PROMPT.md
│   └── ...
├── 📁 deploy/              # Kubernetes & GitOps configs
│   ├── k8s/
│   │   ├── base/           # Base Kubernetes manifests
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── ingress.yaml
│   │   │   ├── configmap.yaml
│   │   │   ├── serviceaccount.yaml
│   │   │   ├── hpa.yaml
│   │   │   └── kustomization.yaml
│   │   └── overlays/
│   │       ├── production/  # Production overrides
│   │       └── staging/     # Staging overrides
│   ├── argocd/
│   │   ├── application.yaml         # Production ArgoCD app
│   │   └── application-staging.yaml # Staging ArgoCD app
│   └── flux/               # FluxCD GitOps (legacy)
├── 📁 scripts/
│   ├── lighthouse.js       # Lighthouse CI runner
│   ├── apply-tokens.js     # Design token generator
│   ├── build-meta.js       # Build metadata generator
│   └── update-design.sh    # Design token update helper
├── 📁 tests/
│   └── smoke.spec.js       # Playwright tests
├── 📁 .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD pipeline
├── .env.example            # Environment variables template
├── .dockerignore           # Docker build exclusions
├── vercel.json             # Vercel config (routes, headers, CSP)
├── vite.config.js          # Vite build configuration
├── docker/
│   ├── Dockerfile          # Multi-stage production container
│   ├── Dockerfile.nginx    # Nginx-based production container
│   └── docker-compose.yaml  # Local Docker development
└── package.json            # Dependencies & scripts
```

---

## 🛠️ Development Scripts

```bash
# Development
npm run dev              # Start Vite dev server (port 5173)
npm run build            # Build production bundle to dist/
npm run preview          # Preview production build (port 4173)

# Design Tokens (NEW)
npm run tokens:apply     # Generate CSS vars from figma-tokens.json

# Code Quality
npm run format           # Format code with Prettier
npm run format:check     # Check formatting
npm run lint             # Lint JavaScript with ESLint
npm run lint:html        # Validate HTML

# Testing
npm test                 # Run Playwright tests
npm run test:ui          # Run tests with UI

# Performance
npm run lighthouse       # Run Lighthouse audit (requires dev server running)
```

---

## 🎨 Design System

### Design Tokens

FloodSight now uses a design token system for consistent theming across the application.

**Token Categories**:

- **Colors**: Primary, secondary, accent, warning, danger, backgrounds
- **Typography**: Font families, sizes, weights
- **Spacing**: Consistent spacing scale (4px, 8px, 12px, etc.)
- **Border Radius**: sm, md, lg, xl
- **Shadows**: sm, md for depth

**Working with Tokens**:

1. **Source of truth**: `/design/figma-tokens.json`
2. **Generate CSS**: `npm run tokens:apply`
3. **Use in CSS**:
   ```css
   .my-component {
     color: var(--color-primary);
     border-radius: var(--radius-md);
     padding: var(--spacing-4);
   }
   ```

**Dark Mode**: Tokens automatically adapt via `.dark` class or `prefers-color-scheme: dark`.

See `/design/README.md` for full documentation.

---

## 🍪 GDPR Compliance

FloodSight is designed with privacy-first principles and GDPR compliance:

### Cookie Banner

- **Consent Categories**: Necessary (always on), Preferences, Analytics, Marketing
- **User Control**: Accept all, Reject all, or customize preferences
- **Persistent**: Stores consent in `fs_consent` cookie for 1 year
- **Re-consent**: Users can change settings via footer link

### Analytics Gating

The consent library (`/lib/consent.js`) gates all non-essential scripts:

```javascript
import { hasConsent, ConsentCategories } from '/lib/consent.js';

if (hasConsent(ConsentCategories.ANALYTICS)) {
  // Initialize analytics
}
```

### Legal Pages

- **Impressum** (`/impressum.html`) - German legal imprint
- **Privacy Policy** (`/privacy.html`) - EN/DE
- **Cookie Policy** (`/cookies.html`) - EN/DE
- **Terms** (`/terms.html`)

### Data Processing

- **Hosting**: Vercel (EU region: `fra1` - Frankfurt)
- **Forms**: Formspree (GDPR-compliant)
- **No tracking**: No analytics by default until consent is given

---

## 📦 Deployment

### Deploy to Vercel (EU Region)

FloodSight is configured to deploy to the **Frankfurt (fra1)** region for GDPR compliance.

1. **Connect Repository**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel auto-detects Vite framework

2. **Build Settings** (auto-configured via `vercel.json`):
   - Framework: `vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Region: `fra1` (Frankfurt, Germany)

3. **Environment Variables** (optional):
   - None required for static site
   - See `.env.example` for future features

4. **Deploy**:
   - Push to `main` branch → auto-deploys to production
   - Vercel provides preview URLs for PRs
   - EU region ensures GDPR compliance

### Custom Domain

1. Add domain in Vercel project settings
2. Update DNS records (Vercel provides instructions)
3. Update `sitemap.xml` and `index.html` canonical URLs

---

## 🎨 Features

### Current

- ✅ Responsive landing page with hero, features, pricing
- ✅ **Design token system** with Figma integration
- ✅ **Interactive Figma dashboard** with:
  - 📍 Real interactive map (Leaflet.js + OpenStreetMap)
  - 📊 Live forecast charts (Chart.js)
  - 🎯 Responsive 3-column layout (desktop) → vertical stack (mobile)
  - 🧭 Breadcrumb navigation + back button
  - 🌊 Wave-pattern logo design
- ✅ **GDPR-compliant cookie banner** with consent management
- ✅ Semantic HTML5 with ARIA landmarks
- ✅ Light theme with professional color scheme (matching dashboard)
- ✅ Smooth scroll navigation
- ✅ Mobile-friendly navigation toggle
- ✅ Form validation (submits to Formspree)
- ✅ Legal pages (Impressum, Privacy, Cookies, Terms, Security)
- ✅ SEO optimized (meta tags, sitemap, structured data)
- ✅ Security headers (HSTS, X-Frame-Options, CSP with external CDN support)
- ✅ Clean URLs via Vercel rewrites
- ✅ Custom 404 page
- ✅ **Complete CI/CD pipeline** with GitHub Actions:
  - Lint, format check, security audit
  - Automated tests (Playwright)
  - Docker image build & push to GHCR
  - Vercel deployment
  - ArgoCD GitOps sync
- ✅ **Multi-platform deployment**:
  - Vercel (static, EU region)
  - Docker containers (multi-arch: amd64, arm64)
  - Kubernetes with Kustomize overlays
  - ArgoCD GitOps (production + staging)

### Future Enhancements

- 🔜 i18n (DE/EN language toggle with localStorage)
- 🔜 Connect map to real-time flood data APIs
- 🔜 User authentication and personalized alerts
- 🔜 Backend API with flood forecasting models
- 🔜 Email/SMS alert notifications
- 🔜 API documentation (OpenAPI/Swagger)
- 🔜 Blog/changelog
- 🔜 Mobile app (React Native or PWA)

---

## 🧪 Testing

See [TESTING.md](./TESTING.md) for detailed testing instructions.

**Quick Test**:

```bash
npm install
npm test
```

---

## 📊 Performance

Target metrics (Lighthouse):

- **Performance**: ≥90
- **Accessibility**: ≥85
- **Best Practices**: ≥90
- **SEO**: ≥90

Run audit:

```bash
npm run dev &           # Start server in background
npm run lighthouse      # Run audit
```

Results saved to `lighthouse-report/`.

---

## 🔒 Security

- HTTPS enforced via Vercel
- Security headers configured in `vercel.json`
- No tracking or analytics by default
- Form submissions via Formspree (GDPR-compliant)
- Responsible disclosure: [security@floodsight.com](mailto:security@floodsight.com)

---

## 🛡️ Security & CI

### Continuous Integration

[![CI Status](https://github.com/afaqbabar/floodsight/actions/workflows/ci.yml/badge.svg)](https://github.com/afaqbabar/floodsight/actions/workflows/ci.yml)

Automated checks on every PR and push to `main`:

**Code Quality:**

- **ESLint** – JavaScript linting
- **Prettier** – Code formatting check
- **HTML Validation** – HTMLHint structure validation

**Security:**

- **npm audit** – Dependency vulnerability scanning
- **TruffleHog** – Secret scanning to prevent credential leaks

**Testing:**

- **Playwright** – End-to-end tests
- **Lighthouse** – Performance, accessibility, SEO audit

**Build & Deploy:**

- **Build verification** – Ensures production build succeeds
- **Docker image** – Multi-arch build & push to GHCR (main branch only)
- **Vercel deployment** – Automatic production deployment
- **ArgoCD sync** – GitOps deployment trigger

### Security Headers

Production site enforces strict security headers via `vercel.json`:

- **HSTS** (2 years, preload-ready)
- **CSP** (Content Security Policy)
- **X-Frame-Options** (DENY)
- **Permissions-Policy** (restricts geolocation, camera, microphone)

Verify headers:

```bash
curl -I https://floodsight.vercel.app | grep -i -E "content-security-policy|strict-transport-security|x-frame-options"
```

### Reporting Vulnerabilities

See [SECURITY.md](./SECURITY.md) for responsible disclosure guidelines.

### Environment Variables (Vercel)

If you need to add secrets later (e.g., analytics tokens):

1. Go to Vercel project settings → Environment Variables
2. Add variables (e.g., `ANALYTICS_KEY`)
3. Reference in code or via Vercel build-time injection

No secrets are required for the current static site.

---

## 🐳 Containers & GitOps

FloodSight supports containerized deployment with Docker and GitOps workflows.

### Build Container Locally

```bash
# Build with Docker (multi-stage)
docker build -t floodsight:latest .

# Run production container
docker run -p 8080:8080 floodsight:latest

# Or use docker-compose (includes dev server + mock API)
docker-compose up -d

# Development mode with hot reload
docker-compose --profile dev up

# Production mode with nginx proxy
docker-compose --profile production up
```

Visit http://localhost:8080 (production) or http://localhost:5173 (dev)

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace floodsight-prod

# Apply base manifests directly
kubectl apply -k deploy/k8s/base

# Or apply with production overlay (recommended)
kubectl apply -k deploy/k8s/overlays/production

# Apply staging overlay
kubectl apply -k deploy/k8s/overlays/staging

# Verify deployment
kubectl get all -n floodsight-prod
kubectl get ingress -n floodsight-prod

# Check logs
kubectl logs -f -n floodsight-prod -l app=floodsight

# Port forward for local testing
kubectl port-forward -n floodsight-prod svc/floodsight 8080:80
```

### GitOps with FluxCD

```bash
# Bootstrap Flux on your cluster
flux bootstrap github \
  --owner=afaqbabar \
  --repository=floodsight \
  --branch=main \
  --path=deploy/k8s/overlays/prod \
  --personal

# Flux will automatically:
# - Sync manifests from Git
# - Update images when new tags are pushed
# - Self-heal on drift
```

### GitOps with ArgoCD

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Deploy FloodSight Production via ArgoCD
kubectl apply -f deploy/argocd/application.yaml

# Deploy FloodSight Staging via ArgoCD
kubectl apply -f deploy/argocd/application-staging.yaml

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Visit: https://localhost:8080
# Username: admin
# Password: (from secret above)

# Sync application manually (if not auto-sync)
argocd app sync floodsight-frontend
argocd app sync floodsight-frontend-staging

# Watch sync status
argocd app get floodsight-frontend
argocd app get floodsight-frontend-staging
```

**ArgoCD Features Configured:**

- ✅ **Auto-sync** – Automatically deploys on git changes
- ✅ **Self-heal** – Fixes manual changes to cluster
- ✅ **Prune** – Removes deleted resources
- ✅ **Image updates** – Kustomize tracks image tags
- ✅ **Health checks** – Monitors deployment health
- ✅ **Notifications** – Slack alerts on sync/health events

### Container Registry (GHCR)

Images are automatically published to GitHub Container Registry via CI/CD:

```bash
# Pull latest multi-arch image (supports amd64 and arm64)
docker pull ghcr.io/afaqbabar/floodsight:latest

# Available tags (auto-generated by CI):
# - latest             (main branch, latest build)
# - main              (main branch alias)
# - v1.0.0            (semantic version tags)
# - 1.0               (major.minor)
# - main-abc1234      (branch + short SHA)
# - staging-latest    (develop branch)
```

**Multi-architecture support:**

- `linux/amd64` – For standard servers, VMs, x86 workstations
- `linux/arm64` – For Raspberry Pi, ARM servers, Apple Silicon

**Manual push to GHCR** (requires authentication):

```bash
# Authenticate with Personal Access Token
echo $GITHUB_TOKEN | docker login ghcr.io -u afaqbabar --password-stdin

# Build and push
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/afaqbabar/floodsight:v1.0.0 \
  --push .
```

**Image metadata:**

- Labels include: git commit, version, build date
- Scanned for vulnerabilities in CI
- Signed with cosign (optional)
- Health check: `curl http://localhost:8080/health.html`

---

### Docker

Build and run the containerized site with nginx:

```bash
# Build image
docker build -f docker/Dockerfile.nginx -t ghcr.io/afaqbabar/floodsight-frontend:dev-local .

# Run container
docker run -p 8080:80 ghcr.io/afaqbabar/floodsight-frontend:dev-local

# Or use docker-compose
docker-compose -f docker/docker-compose.yaml up
```

Visit http://localhost:8080

### Kubernetes

Deploy to Kubernetes using Kustomize:

```bash
# Dev environment
kubectl apply -k deploy/k8s/overlays/dev

# Production environment
kubectl apply -k deploy/k8s/overlays/prod
```

### Flux (GitOps)

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

See [deploy/flux/README.md](deploy/flux/README.md) for details.

### Release flow

- **Push to main** → CI builds/pushes `:latest` and `:dev-<sha>` to GHCR
- **Tag `v0.1.x`** → CI adds semver tags (`:v0.1.x`, `:0.1`, etc.)
- **Flux Image Automation** → bumps `overlays/prod` to the newest semver tag automatically

---

## 🔀 Dual Deployment Setup

FloodSight uses **two parallel deployment flows** from the same repository:

| Target           | Purpose                            | Trigger                    | Managed by        |
| ---------------- | ---------------------------------- | -------------------------- | ----------------- |
| **Vercel**       | Public landing page (static)       | Push to `main`             | Vercel auto-build |
| **k3s + FluxCD** | Local/Edge runtime (containerized) | Push to `main` or tag `v*` | FluxCD GitOps     |

### How It Works

Each environment is **isolated and independent**:

- **Vercel** ignores `deploy/`, `.github/`, Docker files via `.vercelignore`
  - Builds directly from `public/` static assets
  - Serves the marketing site at floodsight.vercel.app
- **FluxCD on k3s** ignores `vercel.json` and Vercel-specific configs
  - Pulls multi-arch images from `ghcr.io/afaqbabar/floodsight-frontend`
  - Runs containerized nginx serving the Vite-built site
  - Auto-updates when new semver tags are pushed

### Raspberry Pi Setup (k3s)

**Prerequisites:**

```bash
# Install k3s on Raspberry Pi
curl -sfL https://get.k3s.io | sh -
alias kubectl='sudo k3s kubectl'

# Install FluxCD
curl -s https://fluxcd.io/install.sh | sudo bash
```

**Bootstrap Flux:**

```bash
flux bootstrap github \
  --owner=afaqbabar \
  --repository=floodsight \
  --branch=main \
  --path=deploy/k8s/overlays/prod \
  --personal
```

**For private GHCR images**, create a pull secret:

```bash
kubectl -n floodsight create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=afaqbabar \
  --docker-password=<PAT_with_read:packages> \
  --docker-email=your@email.com

# Then add to deploy/k8s/base/frontend-deployment.yaml:
# spec:
#   template:
#     spec:
#       imagePullSecrets:
#         - name: ghcr-creds
```

**Verify deployment:**

```bash
# Check Flux status
flux check
flux get kustomizations -n flux-system
flux get imagerepositories -n flux-system

# Check app
kubectl get all -n floodsight
kubectl get svc -n floodsight  # Get service IP/port
```

### Benefits

✅ **Local testing** on real hardware (Raspberry Pi)  
✅ **Public presence** via Vercel's global CDN  
✅ **Single source of truth** - one repo, two outputs  
✅ **GitOps-driven** k8s updates on every tag  
✅ **Multi-arch support** - runs on amd64 and arm64

---

## 🏥 Health Endpoints

FloodSight includes comprehensive health monitoring endpoints for both Vercel and k3s deployments:

| Endpoint              | Purpose                                        | Format | Platform |
| --------------------- | ---------------------------------------------- | ------ | -------- |
| `/health.html`        | Interactive dashboard with auto-refresh        | HTML   | Both     |
| `/assets/health.json` | Build metadata (commit, tag, image, timestamp) | JSON   | Both     |
| `/version.txt`        | Plain text version info                        | Text   | Both     |
| `/healthz`            | Kubernetes probe endpoint                      | JSON   | k3s only |

### Health Dashboard

Visit `/health.html` for a live dashboard showing:

- ✅ **Status**: Application health
- 📦 **Commit**: Git SHA (short)
- 🏷️ **Tag**: Version tag
- 🌿 **Branch**: Git branch
- 🐳 **Image**: Container image reference
- ⏰ **Built At**: Build timestamp

The dashboard auto-refreshes every 5 seconds and displays a green/red status indicator.

### Quick Health Checks

```bash
# View health dashboard in browser
open http://localhost:8080/health.html

# Get JSON health data
curl -s http://localhost:8080/assets/health.json | jq .

# Check plain text version
curl http://localhost:8080/version.txt

# Kubernetes probe endpoint (200 OK)
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/healthz
```

### Kubernetes Probes

The k8s deployment includes:

- **Readiness Probe**: `/healthz` (checks every 5s, starts after 3s)
- **Liveness Probe**: `/healthz` (checks every 10s, starts after 10s)

```bash
# Check probe status
kubectl describe pod -n floodsight -l app=frontend | grep -A 5 "Liveness\|Readiness"

# View health data from inside pod
kubectl exec -n floodsight deployment/frontend -- curl -s http://localhost/healthz
kubectl exec -n floodsight deployment/frontend -- cat /usr/share/nginx/html/version.txt
```

---

## 📄 License

MIT License - see [LICENSE](./LICENSE) (if applicable)

---

## 📧 Contact

- **Email**: [hello@floodsight.com](mailto:hello@floodsight.com)
- **Security**: [security@floodsight.com](mailto:security@floodsight.com)
- **Website**: [floodsight.vercel.app](https://floodsight.vercel.app/)

---

## 🙏 Acknowledgments

- **Data Sources**: ECMWF, Copernicus, National Water Agencies
- **Hosting**: Vercel
- **Forms**: Formspree
- **Icons**: Inline SVG
- **Fonts**: System UI fonts (no external requests)

---

Built with ❤️ for climate resilience.
