# 🔐 FloodSight — Post-Merge Security Hardening Checklist

Your initial DevSecOps baseline is live ✅  
Next steps focus on incremental hardening, automation, and audit readiness.

---

## 1️⃣ Platform & Workflow
- [ ] **Protect `main` branch**  
  → Settings ▸ Branches ▸ Add rule ▸ Require pull request reviews & "CI must pass".
- [ ] **Dependabot for GitHub Actions**  
  ```yaml
  # .github/dependabot.yml
  version: 2
  updates:
    - package-ecosystem: "github-actions"
      directory: "/"
      schedule: { interval: "weekly" }
  ```
- [ ] **Status badge in README**  
  ```markdown
  ![CI](https://github.com/afaqbabar/floodsight/actions/workflows/ci.yml/badge.svg)
  ```
- [ ] **Enable GitHub security features**  
  - Dependabot alerts
  - Code scanning (use default CodeQL or Semgrep)
  - Secret scanning

## 2️⃣ Continuous Verification
- [ ] Run `curl -I https://floodsight.vercel.app` weekly or add a cron job to verify headers.
- [ ] Use Lighthouse CI scores to track regressions.
- [ ] Review CI logs for any Lychee broken links.

## 3️⃣ Privacy & Legal
- [ ] Review privacy.html and terms.html for completeness (align with GDPR).
- [ ] Add link to SECURITY.md in footer ("Responsible Disclosure").
- [ ] Document any cookies or analytics tools.

## 4️⃣ Future Hardening Ideas
- [ ] Integrate OWASP ZAP scan in staging.
- [ ] Add S3/OBS access policy review (when backend/API added).
- [ ] Add audit logs retention (if backend introduced).
- [ ] Consider DNS CNAME verification for sub-domain integrity.

---

## ✅ Verification command
```bash
curl -I https://floodsight.vercel.app | grep -i -E "content-security-policy|strict-transport-security|x-frame-options|referrer-policy"
```

---

**Last updated:** November 5, 2025
