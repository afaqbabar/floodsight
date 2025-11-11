# Folder Structure Improvements

## Summary
The folder structure has been reorganized to improve maintainability and follow best practices for project organization.

## Changes Made

### 1. Removed Duplicates
- **Deleted**: `docker-compose.yml` (duplicate)
- **Kept**: `docker-compose.yaml` (comprehensive version with dev/prod profiles)
- **Reason**: Having two docker-compose files was confusing. The `.yaml` version is more comprehensive with multiple service profiles.

### 2. Moved Development Artifacts
- **Moved**: `prompt.txt` → `docs/DEVELOPMENT_PROMPT.md`
- **Reason**: This 1455-line development prompt file is documentation, not a root-level file. Moved to docs/ and renamed with `.md` extension for clarity.

### 3. Consolidated Scripts
- **Moved**: `UPDATE_DESIGN.sh` → `scripts/update-design.sh`
- **Added**: npm script `npm run update-design` for convenience
- **Updated**: Usage instructions in the script header
- **Made executable**: `chmod +x scripts/update-design.sh`
- **Reason**: All scripts should be in the `scripts/` directory for consistency. Also renamed to lowercase for convention.

### 4. Consolidated Nginx Configs
- **Moved**: `nginx.conf` → `nginx/nginx.conf`
- **Updated**: References in `Dockerfile` and `docker-compose.yaml`
- **Result**: All nginx-related configs are now in the `nginx/` directory:
  - `nginx/nginx.conf` - Main nginx configuration
  - `nginx/health.conf` - Health check configuration
- **Reason**: Related configuration files should be grouped together.

### 5. Updated References
- Updated `Dockerfile` to reference `nginx/nginx.conf`
- Updated `docker-compose.yaml` to reference `nginx/nginx.conf`
- Updated `README.md` project structure documentation
- Updated `scripts/update-design.sh` usage instructions
- Added `update-design` npm script to `package.json`

## Current Structure

```
floodsight/
├── deploy/              # Kubernetes & GitOps configs
├── design/              # Design tokens & Figma integration
├── docs/                # All documentation (including DEVELOPMENT_PROMPT.md)
├── nginx/               # All nginx configs (nginx.conf, health.conf)
├── public/              # Static site content
├── scripts/             # All scripts (build, tokens, lighthouse, update-design)
├── tests/               # Test files
├── docker-compose.yaml  # Single docker-compose file
├── Dockerfile           # Multi-stage production build
├── Dockerfile.nginx     # Simple nginx build
├── package.json         # Dependencies & npm scripts
├── vite.config.js       # Vite configuration
└── vercel.json          # Vercel deployment config
```

## Benefits

1. **Cleaner Root Directory**: Removed clutter from the project root
2. **Better Organization**: Related files are now grouped together
3. **Consistency**: All scripts in one place, all configs in their respective directories
4. **Easier Maintenance**: Developers can find files more intuitively
5. **Updated Documentation**: README reflects the new structure

## Migration Notes

### For Developers

If you had local references to the moved files:

**Docker Builds:**
```bash
# No changes needed - Dockerfile has been updated
docker build -t floodsight .
docker-compose up
```

**Design Token Updates:**
```bash
# Old way:
./UPDATE_DESIGN.sh

# New way (either):
npm run update-design
# or
./scripts/update-design.sh
```

**Nginx Config:**
- The nginx config is now at `nginx/nginx.conf`
- Docker builds automatically reference the new location

### For CI/CD

- All CI/CD pipelines should continue to work without changes
- Docker builds reference the updated paths
- No environment variables or deployment configs need updating

## No Action Required

✅ All references have been automatically updated  
✅ No breaking changes for existing workflows  
✅ Docker builds work with new structure  
✅ CI/CD pipelines unaffected  

---

**Date**: November 11, 2025  
**Status**: ✅ Complete

