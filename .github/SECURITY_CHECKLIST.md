# Security Checklist for Public Repository

## ✅ Verified Safe

### Environment Variables
- [x] `.env` files are in `.gitignore`
- [x] `.env.local` files are in `.gitignore`
- [x] `.env.example` files contain only placeholder values
- [x] No `.env` files exist in the repository
- [x] No `.env` files in git history

### Credentials & Secrets
- [x] No hardcoded passwords in code
- [x] No API keys in code
- [x] No database credentials in code
- [x] No JWT secrets in code
- [x] All secrets use environment variables

### Configuration Files
- [x] `backend/app/core/config.py` uses only default/placeholder values
- [x] Kubernetes ConfigMaps contain only non-sensitive configuration
- [x] No Kubernetes Secrets committed to repository
- [x] Docker Compose files use environment variables

### Git History
- [x] No `.env` files in git history
- [x] No credentials accidentally committed

### GitHub Secrets (Not in Repository)
The following are stored as GitHub Secrets:
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `GHCR_TOKEN` (GitHub Container Registry)

### Kubernetes Secrets (Not in Repository)
The following are created manually in Kubernetes:
- `floodsight-backend-secrets` (DATABASE_URL, SECRET_KEY, CDS_API_KEY, etc.)
- `ghcr-creds` (Docker registry credentials)

## 🔒 Sensitive Information Locations

### Local Only (Never Commit)
1. **Backend Environment**:
   - `backend/.env` - Database credentials, API keys, secrets
   
2. **Kubernetes Secrets**:
   - Created with `kubectl create secret` commands
   - Not stored in git

3. **Cloudflare Tunnel**:
   - Tunnel token stored in systemd service file on Pi
   - Not in repository

### GitHub Secrets (Encrypted)
- Stored in GitHub repository settings
- Used by GitHub Actions workflows
- Never exposed in logs

## 📋 Before Making Repository Public

### 1. Review Default Values
Check these files have safe defaults:
- [ ] `backend/app/core/config.py` - Line 48 (DATABASE_URL)
- [ ] `backend/app/core/config.py` - Line 53 (SECRET_KEY)

### 2. Update Documentation
- [ ] Add setup instructions for `.env` files
- [ ] Document required environment variables
- [ ] Add Kubernetes secrets setup guide

### 3. Final Scan
```bash
# Scan for potential secrets
git secrets --scan-history

# Or use gitleaks
gitleaks detect --source . --verbose

# Or use trufflehog
trufflehog git file://. --only-verified
```

## 🛡️ Security Best Practices

### For Contributors
1. **Never commit**:
   - `.env` files
   - API keys or tokens
   - Passwords or credentials
   - Private keys

2. **Always use**:
   - Environment variables for secrets
   - `.env.example` for documentation
   - GitHub Secrets for CI/CD
   - Kubernetes Secrets for production

3. **Before committing**:
   ```bash
   # Check what you're committing
   git diff --staged
   
   # Verify no secrets
   git diff --staged | grep -iE 'password|secret|token|api[_-]?key'
   ```

### For Repository Owner
1. **Rotate secrets** if repository was ever private with secrets
2. **Enable GitHub security features**:
   - Secret scanning
   - Dependabot alerts
   - Code scanning (CodeQL)

3. **Monitor access**:
   - Review who has access to GitHub Secrets
   - Review who can deploy to production
   - Audit Kubernetes RBAC

## 🚨 If Secrets Are Exposed

1. **Immediately rotate** all exposed credentials
2. **Remove from git history**:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/secret" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (if repository is not public yet)
4. **Notify users** if repository was already public

## 📚 Additional Resources

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [12 Factor App: Config](https://12factor.net/config)

