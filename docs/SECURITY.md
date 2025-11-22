# Security Policy

## Reporting a vulnerability

Please email security@floodsight.app or open a private GitHub Security Advisory. Do **not** file public issues for sensitive reports.

## Practices

- No secrets in the repository; use GitHub Actions Secrets and Vercel Environment Variables.
- CI runs: Link check (Lychee), Secret scan (Gitleaks), Static analysis (Semgrep), HTML lint (HTMLHint), Lighthouse (production).
- Security headers are enforced via `vercel.json`.

## Scope

Static site (HTML/CSS/JS). Issues are typically: missing headers, broken links, unsafe external assets, or leaked secrets.
