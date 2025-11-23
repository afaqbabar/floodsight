# Repository Structure

This document describes the improved organization of the FloodSight repository.

## 📁 Directory Structure

```
floodsight/
├── .github/
│   └── workflows/          # CI/CD workflows
│       ├── ci.yml          # Main CI pipeline
│       └── build-and-push.yml  # Docker build & push
│
├── backend/               # Python FastAPI backend
│   ├── app/               # Application code
│   ├── alembic/          # Database migrations
│   ├── tests/             # Backend tests
│   └── ...
│
├── public/                # Frontend static site
│   ├── *.html             # HTML pages
│   ├── assets/            # CSS, JS, images
│   ├── components/        # Reusable components
│   └── lib/               # JavaScript libraries
│
├── docker/                # Docker configuration
│   ├── Dockerfile         # Multi-stage production container
│   ├── Dockerfile.nginx   # Nginx-based container
│   └── docker-compose.yaml # Local development setup
│
├── deploy/                # Deployment configurations
│   ├── k8s/               # Kubernetes manifests
│   │   ├── base/          # Base configurations
│   │   └── overlays/      # Environment overlays (dev/prod)
│   ├── flux/              # FluxCD GitOps configs
│   └── argocd/            # ArgoCD configs
│
├── docs/                  # Documentation
│   ├── deployment/        # Deployment guides
│   │   ├── DEPLOYMENT_STRATEGY.md
│   │   ├── EXPOSE_PI_BACKEND.md
│   │   ├── FLY_IO_DEPLOYMENT.md
│   │   └── RASPBERRY_PI_SETUP.md
│   ├── development/       # Development guides
│   │   ├── FRONTEND_BACKEND_INTEGRATION.md
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   ├── PRODUCTION_STATUS.md
│   │   └── FOLDER_STRUCTURE_IMPROVEMENTS.md
│   ├── phases/            # Phase summaries
│   │   ├── PHASE_A_SUMMARY.md
│   │   ├── PHASE_B_SUMMARY.md
│   │   └── PHASE_B2_SUMMARY.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── SECURITY.md
│   ├── TESTING.md
│   └── ...
│
├── scripts/               # Utility scripts
│   ├── add-global-stations.sh
│   ├── QUICK_START_CLOUDFLARE.sh
│   ├── apply-tokens.js
│   ├── build-meta.js
│   ├── lighthouse.js
│   └── update-design.sh
│
├── tests/                 # Frontend E2E tests
│   └── *.spec.js          # Playwright tests
│
├── nginx/                 # Nginx configuration
│   └── health.conf        # Health check config
│
├── dist/                  # Build output (gitignored)
├── node_modules/          # Node dependencies (gitignored)
├── data/                  # Data files (gitignored)
│
├── package.json           # Node.js dependencies
├── vite.config.js         # Vite build configuration
├── playwright.config.js   # Playwright test config
├── vercel.json            # Vercel deployment config
├── .gitignore             # Git ignore rules
├── .prettierignore        # Prettier ignore rules
└── README.md              # Main documentation
```

## 📋 Key Directories

### Root Level
- **Configuration files** (`package.json`, `vite.config.js`, etc.) stay in root for easy access
- **README.md** - Main project documentation
- **Build artifacts** (`dist/`, `node_modules/`) are gitignored

### `/public/`
Frontend static site content:
- HTML pages (index, dashboard, legal pages)
- Assets (CSS, JavaScript, images)
- Components and libraries

### `/backend/`
Python FastAPI backend:
- Application code
- Database migrations (Alembic)
- Backend tests

### `/docker/`
Docker configuration files:
- `Dockerfile` - Multi-stage production build
- `Dockerfile.nginx` - Nginx-based container
- `docker-compose.yaml` - Local development

### `/deploy/`
Infrastructure as Code:
- Kubernetes manifests (Kustomize)
- FluxCD GitOps configurations
- ArgoCD configurations

### `/docs/`
All documentation organized by category:
- **deployment/** - Deployment guides and strategies
- **development/** - Development guides and summaries
- **phases/** - Project phase summaries

### `/scripts/`
Utility scripts for:
- Development tasks
- Deployment automation
- Build processes

## 🔄 Migration Notes

### Docker Files
- Moved from root to `docker/` directory
- Updated CI/CD workflows to reference `docker/Dockerfile.nginx`
- Update local commands: `docker build -f docker/Dockerfile.nginx .`

### Documentation
- All `.md` files (except README.md) moved to `docs/`
- Organized by category (deployment, development, phases)
- Security documentation in `docs/SECURITY.md`

### Scripts
- Shell scripts moved to `scripts/` directory
- JavaScript build scripts remain in `scripts/`

## 🚀 Quick Reference

### Build Docker Image
```bash
docker build -f docker/Dockerfile.nginx -t floodsight:latest .
```

### Run Docker Compose
```bash
docker-compose -f docker/docker-compose.yaml up
```

### Find Documentation
- Deployment guides: `docs/deployment/`
- Development guides: `docs/development/`
- Phase summaries: `docs/phases/`

## 📝 Best Practices

1. **Keep root clean** - Only essential config files in root
2. **Organize by purpose** - Group related files together
3. **Document structure** - Update this file when adding new directories
4. **Use .gitignore** - Exclude build artifacts and dependencies





