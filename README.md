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
│   ├── impressum.html      # Legal imprint (DE)
│   ├── privacy.html        # Privacy policy (EN/DE)
│   ├── terms.html          # Terms of service
│   ├── security.html       # Security disclosure
│   ├── thanks.html         # Form success page
│   ├── 404.html            # Custom 404 page
│   ├── assets/
│   │   ├── css/
│   │   │   └── floodsight.css  # Styles
│   │   └── js/
│   │       ├── main.js     # Entry point (ES module)
│   │       ├── nav.js      # Navigation logic
│   │       ├── forms.js    # Form validation
│   │       ├── utils.js    # Utilities
│   │       └── dom.js      # DOM helpers
│   ├── logos/              # Brand logos
│   ├── sitemap.xml         # SEO sitemap
│   └── robots.txt          # Crawler directives
├── 📁 docs/                # Documentation
│   ├── TESTING.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── ...
├── 📁 deploy/              # Kubernetes & Flux configs
│   ├── k8s/
│   └── flux/
├── 📁 scripts/
│   └── lighthouse.js       # Lighthouse CI runner
├── 📁 tests/
│   └── smoke.spec.js       # Playwright tests
├── vercel.json             # Vercel config (routes, headers)
├── vite.config.js          # Build configuration
├── Dockerfile.nginx        # Container build
└── package.json            # Dependencies & scripts
```

---

## 🛠️ Development Scripts

```bash
# Development
npm run dev              # Start Vite dev server (port 5173)
npm run build            # Build production bundle to dist/
npm run preview          # Preview production build (port 4173)

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

## 📦 Deployment

### Deploy to Vercel

1. **Connect Repository**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel auto-detects static site

2. **Build Settings** (auto-configured):
   - Framework: `Other`
   - Build Command: (none)
   - Output Directory: `.` (root)

3. **Environment Variables** (optional):
   - None required for static site
   - See `.env.example` for future features

4. **Deploy**:
   - Push to `main` branch → auto-deploys
   - Vercel provides preview URLs for PRs

### Custom Domain

1. Add domain in Vercel project settings
2. Update DNS records (Vercel provides instructions)
3. Update `sitemap.xml` and `index.html` canonical URLs

---

## 🎨 Features

### Current

- ✅ Responsive landing page with hero, features, pricing
- ✅ Semantic HTML5 with ARIA landmarks
- ✅ Dark theme with CSS custom properties
- ✅ Smooth scroll navigation
- ✅ Mobile-friendly navigation toggle
- ✅ Form validation (submits to Formspree)
- ✅ Legal pages (Impressum, Privacy, Terms, Security)
- ✅ SEO optimized (meta tags, sitemap, structured data)
- ✅ Security headers (HSTS, X-Frame-Options, CSP-ready)
- ✅ Clean URLs via Vercel rewrites
- ✅ Custom 404 page

### Future Enhancements

- 🔜 i18n (DE/EN language toggle with localStorage)
- 🔜 Interactive demo dashboard
- 🔜 API documentation
- 🔜 Blog/changelog

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
- **Link check** (Lychee) – Detects broken links in HTML/Markdown
- **Secret scan** (Gitleaks) – Prevents accidental credential leaks
- **SAST** (Semgrep) – Static analysis for JavaScript security issues
- **HTML lint** (HTMLHint) – Validates HTML structure
- **Lighthouse** (LHCI) – Performance, accessibility, and SEO audit

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

### Build locally

```bash
npm i
npm run build      # Builds to dist/ with Vite
npm run preview    # Preview production build at http://localhost:4173
```

### Docker

Build and run the containerized site with nginx:

```bash
# Build image
docker build -f Dockerfile.nginx -t ghcr.io/afaqbabar/floodsight-frontend:dev-local .

# Run container
docker run -p 8080:80 ghcr.io/afaqbabar/floodsight-frontend:dev-local

# Or use docker-compose
docker-compose up
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

| Target | Purpose | Trigger | Managed by |
|--------|----------|----------|-------------|
| **Vercel** | Public landing page (static) | Push to `main` | Vercel auto-build |
| **k3s + FluxCD** | Local/Edge runtime (containerized) | Push to `main` or tag `v*` | FluxCD GitOps |

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

| Endpoint | Purpose | Format | Platform |
|----------|---------|--------|----------|
| `/health.html` | Interactive dashboard with auto-refresh | HTML | Both |
| `/assets/health.json` | Build metadata (commit, tag, image, timestamp) | JSON | Both |
| `/version.txt` | Plain text version info | Text | Both |
| `/healthz` | Kubernetes probe endpoint | JSON | k3s only |

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

