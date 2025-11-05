## Summary

Adds DevSecOps baseline for FloodSight static site:
- ✅ Enhanced security headers (HSTS 2yr, CSP, Permissions-Policy)
- ✅ CI/CD with 5 automated checks (Lychee, Gitleaks, Semgrep, HTMLHint, Lighthouse)
- ✅ Security policy (SECURITY.md)
- ✅ Documentation updates (README, TESTING)
- ✅ No changes to HTML/CSS/JS or routes

## Changes

### New Files
- `.github/workflows/ci.yml` – CI pipeline (runs on PR, push, weekly)
- `.htmlhintrc` – HTML validation config
- `SECURITY.md` – Vulnerability reporting guidelines
- `.pre-commit-config.yaml` – Optional local hooks

### Modified Files
- `vercel.json` – Enhanced security headers
  - HSTS: 2 years with preload
  - X-Frame-Options: DENY (upgraded from SAMEORIGIN)
  - Content-Security-Policy: strict directives
  - Permissions-Policy: restrict geolocation, camera, microphone
  - X-XSS-Protection: 0 (disable legacy filter)
- `README.md` – Added "Security & CI" section with badge
- `TESTING.md` – Added CI workflow and header verification documentation

## CI Jobs

1. **link-check** (Lychee) – Detect broken links in HTML/Markdown
2. **secret-scan** (Gitleaks) – Prevent credential leaks in git history
3. **sast-js** (Semgrep) – Static analysis for JavaScript security issues
4. **html-lint** (HTMLHint) – Validate HTML structure
5. **lighthouse** (LHCI) – Performance, accessibility, and SEO audit

## ⚠️ Repository Configuration Required

**Before merging**, ensure the following repository setting is enabled:

**Settings → Actions → General → Workflow permissions**
- Select: ✅ **"Read and write permissions"**

This is required for the Gitleaks job to write security events and interact with pull requests.

Without this setting, the `secret-scan` job will fail with permission errors.

## Validation Checklist

- [ ] CI passes all 5 jobs (check Actions tab)
- [ ] Headers verified on production after merge
- [ ] No broken links (Lychee clean)
- [ ] Mobile layout unchanged
- [ ] Legal pages still accessible (`/privacy`, `/terms`, `/impressum`, `/security`)

## Testing After Merge

Verify headers are applied:
```bash
curl -I https://floodsight.vercel.app | grep -i -E "content-security-policy|strict-transport-security|x-frame-options"
```

Expected output:
```
strict-transport-security: max-age=63072000; includeSubDomains; preload
x-frame-options: DENY
content-security-policy: default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'
permissions-policy: geolocation=(), microphone=(), camera=()
```

## If CSP Causes Issues

If Content-Security-Policy blocks functionality:
1. Temporarily switch to `Content-Security-Policy-Report-Only` in `vercel.json`
2. Check browser console for violation reports
3. Adjust directives as needed
4. Re-deploy and test
5. Switch back to enforcing mode

See [TESTING.md](./TESTING.md) for full verification steps.

