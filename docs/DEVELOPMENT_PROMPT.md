1.  Project: FloodSight landing site & minimal app
    Repo: https://github.com/afaqbabar/floodsight
    Hosting: Vercel

Your job in this workspace:

Understand the codebase

Read README._, index.html, /assets, /css, floodsight.js, any /pages (privacy, terms/impressum), and deployment files (vercel.json, .env_ if any).

Generate a concise, bullet-point Codebase Overview (files, responsibilities, data flow).

Fix & improve

Routing & links: Ensure all nav/footer links work on Vercel (e.g., /impressum, /privacy, /terms). Add clean routes or anchors so 404s don’t happen.

SEO: Add <title>, meta description, Open Graph/Twitter cards, canonical link, robots.txt, sitemap.xml. Validate that i18n toggle doesn’t hide metadata.

Performance: Lighthouse pass ≥ 90 for Performance/Best Practices/SEO; ≥ 85 Accessibility. Lazy-load images, compress assets, defer non-critical JS, remove unused CSS.

Mobile layout: Fix any mobile misalignment and CLS (use responsive grid/flex, proper image sizing, no layout jank).

Forms: Make forms submit safely (Netlify removed → use Vercel). Add a no-backend mode (mailto: or Formspree) behind a config flag.

I18n copy: Ensure DE/EN toggles work on all pages; persist selection in localStorage.

Legal pages: Ensure Impressum (DE), Privacy/Datenschutz, and Terms exist and link correctly. Add basic accessible headings and landmarks.

JS quality: Refactor floodsight.js into modules: dom.js (selectors & helpers), i18n.js, forms.js, analytics.js (optional), routes.js. No global leaks; use ES modules.

Build/deploy: Provide a minimal script (npm run build if applicable) or document static export. Confirm vercel.json routes, trailingSlash, and headers (security headers).

Safety & quality gates

Add Prettier + ESLint with sensible web defaults.

Add a lightweight Playwright smoke test for critical links (home → privacy → impressum).

Add HTML validity check (e.g., npm run lint:html with html-validate).

Produce a Lighthouse report (CI-free local run; include instructions and results markdown).

Deliverables

A short PLAN.md describing changes.

A DIFF summary of all modified/added files.

Updated files implementing the plan.

A TESTING.md with: how to run locally, how to build, how to run Playwright, and a lighthouse checklist.

If something is unclear, make the smallest reasonable assumption and proceed.

Constraints

Keep stack simple (static site). Don’t introduce frameworks unless truly needed.

No tracking by default. If adding analytics hooks, guard them behind an env/config flag that is off.

Acceptance criteria

All links work on Vercel.

Lighthouse thresholds met (see above).

npm run format and npm run lint pass.

I18n toggle persists and doesn’t break SEO/social previews.

Legal pages present and accessible.

README.md shows clear local dev + deploy steps for Vercel.

Now do this sequence automatically:

Generate the Codebase Overview.

Propose a one-screen PLAN.md. Wait for my “approve” keyword.

After I say approve, implement changes,

2.  We deployed FloodSight successfully to Vercel and Lighthouse scores are excellent.
    However, there are some 404 errors for missing SVG assets:

- /hero-map-placeholder.svg
- /logos/citylab.svg
- /logos/insurtech.svg
- /logos/university.svg
- /logos/iot.svg

Fix these missing assets.

If the images are used in the landing page (like partner logos or hero placeholders), do one of the following:

1. Preferably add simple placeholder SVGs (grey or white logos) inside /public/logos/ and /public/.
2. If any image is not needed, remove or comment out the <img> tags in index.html.

After fixing, ensure there are **no 404s** in the browser console and all visual elements still render cleanly.

Then:

- Update the commit with a short summary (e.g. "Fix: missing SVG assets").
- Push the changes to main.
- Confirm that the site redeploys successfully on Vercel.

3.  verify in browser console that no 404 errors remain after deployment

4.  then output:

DIFF summary

Updated files

TESTING.md

Lighthouse instructions/results

Any notes for Vercel (vercel.json routes)
#######################################

Devsecops

Project: FloodSight landing site (static HTML/CSS/JS)
Repo: https://github.com/afaqbabar/floodsight

Hosting: Vercel
Goal: Add a lightweight, no-friction DevSecOps baseline suitable for a static site without changing the stack.

Read & understand

Read README._, index.html, /assets, /css, any _.js (e.g., floodsight.js), legal pages (/privacy.html, /terms.html, /impressum.html), and existing vercel.json.

Produce a short Codebase Overview (files, responsibilities, nav/links, deployment specifics).

What to implement (security + quality)

Security headers on Vercel (extend, don’t replace)

Keep the existing vercel.json content (rewrites/routes).

Add a "headers" section that applies to /(.\*) with:

Strict-Transport-Security: max-age=63072000; includeSubDomains; preload

X-Content-Type-Options: nosniff

X-Frame-Options: DENY

Referrer-Policy: no-referrer-when-downgrade

Permissions-Policy: geolocation=(), microphone=(), camera=()

X-XSS-Protection: 0

Content-Security-Policy: default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'

If CSP breaks anything, temporarily switch to Content-Security-Policy-Report-Only, test, then re-tighten.

GitHub Actions CI (create .github/workflows/ci.yml)
Jobs to add:

Link check with Lychee (scan _.html, \*\*/_.md; sensible timeouts; use ${{ secrets.GITHUB_TOKEN }}).

Secrets scan with Gitleaks (use full history, --redact, --exit-code 1).

SAST for JS/HTML with Semgrep (config: p/ci).

HTML lint with HTMLHint (add a small .htmlhintrc).

Lighthouse (production URL) using npx @lhci/cli autorun against https://floodsight.vercel.app.

Trigger on pull_request, push to main, and a weekly cron.

.htmlhintrc (root)

Rules: attr-no-duplication, doctype-html5, tag-pair, id-unique, spec-char-escape, img-alt-require, etc. (common-sense defaults).

SECURITY.md (root)

How to report vulnerabilities (email or GitHub Security Advisory).

Statement of practice: no secrets in repo; CI = Lychee + Gitleaks + Semgrep + HTMLHint + Lighthouse; headers via vercel.json.

(Optional, local) .pre-commit-config.yaml

Hooks: lychee, trailing whitespace, EOF fixer, large files.

Add instructions in TESTING.md for enabling locally.

Minimal docs

PLAN.md (one-screen plan of changes).

TESTING.md with: how to run locally, what CI does, how to check headers (DevTools + curl -I), and how to read Lighthouse output.

Update README.md with a short “Security & CI” section and how to add env vars in Vercel (if needed later).

Do not break routes

Ensure existing rewrites for /privacy, /terms, /impressum still work.

If any links 404, fix paths or create routes (prefer clean routes that map to HTML files).

Constraints

Do not introduce frameworks or a build system; keep it static.

Keep CI fast (< ~3–4 min).

Don’t commit secrets; use GitHub/Vercel envs if needed later.

Keep diffs minimal and well-scoped.

Acceptance criteria

Security headers present on production (verified by DevTools/curl -I).

CI passes: Lychee, Gitleaks, Semgrep, HTMLHint, Lighthouse.

No broken links (site & console clean of 404s).

No change in visual layout; mobile still OK.

Clear docs (PLAN.md, TESTING.md, README section).

Delivery format & sequence

Output:

Codebase Overview (bullets)

PLAN.md proposal (one screen)

DIFF summary (file list + brief changes)

Exact file contents for:

.github/workflows/ci.yml

.htmlhintrc

SECURITY.md

(optional) .pre-commit-config.yaml

Updated vercel.json (merged headers, not replaced)

README and TESTING updates

Wait for my keyword: approve

After I say approve:

Create a branch security-setup

Apply all changes

Open a PR titled “Add lightweight DevSecOps (headers + CI)” with a concise description

Post CI run results, Lighthouse link, and header verification snippet (e.g., curl -I output)

If CI flags anything, fix and update the PR until green

After merge:

Confirm Vercel deployment is live

Re-check headers and console (no 404s)

Templates (use these exact contents unless repo needs minor tweaks)

.github/workflows/ci.yml

name: ci
on:
pull_request:
push: { branches: [main] }
schedule: - cron: "0 2 \* \* 0"

permissions:
contents: read

jobs:
link-check:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v4 - name: Check links with lychee
uses: lycheeverse/lychee-action@v1
with:
args: --verbose --no-progress --max-concurrency 5 --retry-wait-time 2 --timeout 20s "._\\.html" "\*\*/_.md"
env:
GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

secret-scan:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v4
with: { fetch-depth: 0 } - name: Gitleaks (secrets scanning)
uses: gitleaks/gitleaks-action@v2
with:
args: detect --no-banner --source . --redact --exit-code 1

sast-js:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v4 - name: Semgrep scan
uses: returntocorp/semgrep-action@v1
with:
auditOn: push
config: p/ci

html-lint:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v4 - run: npm i -g htmlhint - run: htmlhint "\*_/_.html"

lighthouse:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v4 - uses: actions/setup-node@v4
with: { node-version: "20" } - name: Run Lighthouse CI on production
run: npx @lhci/cli autorun --collect.url=https://floodsight.vercel.app --upload.target=temporary-public-storage

.htmlhintrc

{
"attr-lowercase": true,
"attr-no-duplication": true,
"doctype-first": false,
"doctype-html5": true,
"tagname-lowercase": true,
"tag-pair": true,
"tag-self-close": false,
"id-unique": true,
"spec-char-escape": true,
"head-script-disabled": false,
"img-alt-require": true
}

SECURITY.md

# Security Policy

## Reporting a vulnerability

Please email security@floodsight.app or open a private GitHub Security Advisory. Do **not** file public issues for sensitive reports.

## Practices

- No secrets in the repository; use GitHub Actions Secrets and Vercel Environment Variables.
- CI runs: Link check (Lychee), Secret scan (Gitleaks), Static analysis (Semgrep), HTML lint (HTMLHint), Lighthouse (production).
- Security headers are enforced via `vercel.json`.

## Scope

Static site (HTML/CSS/JS). Issues are typically: missing headers, broken links, unsafe external assets, or leaked secrets.

vercel.json (merge example)

Keep existing keys (rewrites/routes). Add this headers block; do not remove current content.

{
"rewrites": [
{ "source": "/privacy", "destination": "/privacy.html" },
{ "source": "/terms", "destination": "/terms.html" },
{ "source": "/impressum", "destination": "/impressum.html" }
],
"headers": [
{
"source": "/(.\*)",
"headers": [
{ "key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload" },
{ "key": "X-Content-Type-Options", "value": "nosniff" },
{ "key": "X-Frame-Options", "value": "DENY" },
{ "key": "Referrer-Policy", "value": "no-referrer-when-downgrade" },
{ "key": "Permissions-Policy", "value": "geolocation=(), microphone=(), camera=()" },
{ "key": "X-XSS-Protection", "value": "0" },
{ "key": "Content-Security-Policy",
"value": "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
}
]
}
]
}

PLAN.md (sample)

# PLAN

- Add DevSecOps baseline for static Vercel site:
  1. Security headers via `vercel.json` (merge, not replace)
  2. CI: Lychee, Gitleaks, Semgrep, HTMLHint, Lighthouse
  3. Docs: TESTING.md + README updates; SECURITY.md
- Keep stack simple; no framework or build changes.
- Validate: headers visible on prod; CI green; no 404s.

TESTING.md (sample)

# Testing & Verification

## Headers

- Browser: DevTools → Network → Document → Response Headers (check CSP, HSTS, etc.)
- CLI: `curl -I https://floodsight.vercel.app | grep -i -E "content-security-policy|strict-transport-security|x-content-type-options|x-frame-options"`

## CI

- See GitHub → Actions → `ci` workflow for:
  - Lychee, Gitleaks, Semgrep, HTMLHint, Lighthouse
- Re-run workflow on latest commit or open a PR.

## Lighthouse

- Run in Chrome Lighthouse panel or rely on CI step (LHCI output link in logs).

## Optional pre-commit

- `pip install pre-commit && pre-commit install`
- Hooks: lychee, whitespace, EOF fixer, large files.

If anything is unclear

Make the smallest reasonable assumption and proceed.

Maintain small, readable commits with clear messages.

############
Update the Gitleaks job in .github/workflows/ci.yml to use the new syntax:

remove the deprecated args: input

add permissions: { contents: read, security-events: write }

pass env: GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
The workflow should run without needing a manually created token.
###########
Update the secret-scan job to keep gitleaks/gitleaks-action@v2, add permissions: { contents: read, pull-requests: read, security-events: write }, and set env: GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}. Also note in the PR description that the repo setting “Workflow permissions → Read and write” must be enabled.
#######

🪜 Step-by-Step: Add SECURITY_NEXT.md
1️⃣ Open your repo in VS Code (or Cursor)

Open the folder:
C:\Users\Lenovo\scrimba\floodsight\floodsight

or in GitHub web UI → click Add file ▸ Create new file

2️⃣ File name

SECURITY_NEXT.md (all caps)

3️⃣ Paste this content

# 🔐 FloodSight — Post-Merge Security Hardening Checklist

Your initial DevSecOps baseline is live ✅  
Next steps focus on incremental hardening, automation, and audit readiness.

---

## 1️⃣ Platform & Workflow

- [ ] **Protect `main` branch**  
      → Settings ▸ Branches ▸ Add rule ▸ Require pull request reviews & “CI must pass”.
- [ ] **Dependabot for GitHub Actions**
  ```yaml
  # .github/dependabot.yml
  version: 2
  updates:
    - package-ecosystem: 'github-actions'
      directory: '/'
      schedule: { interval: 'weekly' }
  ```

Status badge in README

![CI](https://github.com/afaqbabar/floodsight/actions/workflows/ci.yml/badge.svg)

Enable GitHub security features

Dependabot alerts

Code scanning (use default CodeQL or Semgrep)

Secret scanning

2️⃣ Continuous Verification

Run curl -I https://floodsight.vercel.app weekly or add a cron job to verify headers.

Use Lighthouse CI scores to track regressions.

Review CI logs for any Lychee broken links.

3️⃣ Privacy & Legal

Review privacy.html and terms.html for completeness (align with GDPR).

Add link to SECURITY.md in footer (“Responsible Disclosure”).

Document any cookies or analytics tools.

4️⃣ Future Hardening Ideas

Integrate OWASP ZAP scan in staging.

Add S3/OBS access policy review (when backend/API added).

Add audit logs retention (if backend introduced).

Consider DNS CNAME verification for sub-domain integrity.

✅ Verification command
curl -I https://floodsight.vercel.app | grep -i -E "content-security-policy|strict-transport-security|x-frame-options|referrer-policy"

Last updated: {{current_date}}

Replace `{{current_date}}` with today’s date.

---

### 4️⃣ Commit and push

If using VS Code:

```bash
git add SECURITY_NEXT.md
git commit -m "Add post-merge security hardening checklist"
git push


If using GitHub UI:
Click Commit directly to main.
####

Cursor Agent Prompt — “Bundle assets/js + Containerize + GitOps (FloodSight)”

Role: Senior DevOps/FE engineer on github.com/afaqbabar/floodsight.

Goal:
Add a minimal build step with Vite (bundles assets/js/main.js), then containerize with nginx, add GitHub Actions to push multi-arch images to GHCR, add Kustomize (dev/prod) and FluxCD image automation. Do not break the existing Vercel deploy — keep vercel.json as-is.

Project facts (use these exact paths)

JS entry: /assets/js/main.js (ESM, imports other modules)

Other JS files: /assets/js/{dom,floodsight,forms,nav,utils}.js

CSS: /assets/css/floodsight.css

HTML pages (multi-page build):
index.html, impressum.html, privacy.html, terms.html, security.html, thanks.html, 404.html, verify-assets.html, google5b12900a10441c99.html

1) Add Vite (bundle + multi-page)

Update package.json:

Add devDependency: "vite": "^5.4.0" (or latest)

Add scripts (keep current ones):

{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "format": "prettier --write \"**/*.{html,css,js,json,md}\"",
    "format:check": "prettier --check \"**/*.{html,css,js,json,md}\"",
    "lint": "eslint \"assets/js/**/*.js\"",
    "lint:html": "html-validate \"*.html\"",
    "test": "playwright test",
    "test:ui": "playwright test --ui",
    "lighthouse": "node scripts/lighthouse.js"
  }
}


Create vite.config.js at repo root:

import { resolve } from 'node:path';

export default {
  root: '.',              // project root is repository root
  base: './',             // keep relative paths for nginx or any hosting
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'index.html'),
        impressum: resolve(__dirname, 'impressum.html'),
        privacy: resolve(__dirname, 'privacy.html'),
        terms: resolve(__dirname, 'terms.html'),
        security: resolve(__dirname, 'security.html'),
        thanks: resolve(__dirname, 'thanks.html'),
        '404': resolve(__dirname, '404.html'),
        'verify-assets': resolve(__dirname, 'verify-assets.html'),
        'google5b12900a10441c99': resolve(__dirname, 'google5b12900a10441c99.html')
      }
    }
  },
  server: {
    port: 5173,
    open: false
  }
};


HTML & scripts:

Leave <script type="module" src="/assets/js/main.js"> in index.html. Vite will rewrite to the bundled file for dist/.

Other pages don’t currently load JS; that’s fine. Vite will still process and output them to dist/.

Run locally to verify:

npm i
npm run build
npm run preview

2) Docker (nginx runtime)

Add Dockerfile.nginx (root):

FROM node:20-alpine AS build
WORKDIR /site
COPY package*.json ./
RUN npm ci || npm i
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /site/dist /usr/share/nginx/html
EXPOSE 80


Add .dockerignore:

node_modules
dist
.git
.gitignore
Dockerfile
Dockerfile.nginx


Optional docker-compose.yml:

version: "3.9"
services:
  web:
    build:
      context: .
      dockerfile: ./Dockerfile.nginx
    ports: ["8080:80"]

3) CI to GHCR (multi-arch)

Create .github/workflows/build-and-push.yml:

name: Build static site & push image
on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Setup Buildx
        uses: docker/setup-buildx-action@v3

      - name: Derive image name
        id: iv
        run: |
          echo "IMAGE=ghcr.io/${{ github.repository }}-frontend" >> $GITHUB_OUTPUT
          echo "TAG=dev-${GITHUB_SHA::7}" >> $GITHUB_OUTPUT

      - name: Build & Push (multi-arch)
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./Dockerfile.nginx
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            ${{ steps.iv.outputs.IMAGE }}:${{ steps.iv.outputs.TAG }}
            ${{ steps.iv.outputs.IMAGE }}:latest
          cache-from: type=registry,ref=${{ steps.iv.outputs.IMAGE }}:buildcache
          cache-to: type=registry,ref=${{ steps.iv.outputs.IMAGE }}:buildcache,mode=max


This pushes ghcr.io/afaqbabar/floodsight-frontend:{dev-<sha>,latest} (works on cloud + Raspberry Pi 5).

4) Kubernetes (Kustomize)

Create files:

deploy/k8s/base/namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: floodsight


deploy/k8s/base/frontend-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: floodsight
spec:
  replicas: 2
  selector: { matchLabels: { app: frontend } }
  template:
    metadata: { labels: { app: frontend } }
    spec:
      containers:
        - name: frontend
          image: ghcr.io/afaqbabar/floodsight-frontend:latest
          ports: [{ containerPort: 80 }]
          resources:
            requests: { cpu: "50m", memory: "64Mi" }
            limits:   { cpu: "300m", memory: "256Mi" }


deploy/k8s/base/frontend-service.yaml

apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: floodsight
spec:
  selector: { app: frontend }
  ports:
    - port: 80
      targetPort: 80


deploy/k8s/base/ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: floodsight
  namespace: floodsight
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: floodsight.example.com # TODO: set your domain
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port: { number: 80 }


deploy/k8s/overlays/dev/kustomization.yaml

apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: floodsight
resources: [ ../../base ]
images:
  - name: ghcr.io/afaqbabar/floodsight-frontend
    newTag: dev


deploy/k8s/overlays/prod/kustomization.yaml

apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: floodsight
resources: [ ../../base ]
images:
  - name: ghcr.io/afaqbabar/floodsight-frontend
    newTag: v0.1.0

5) FluxCD (GitOps + Image Automation)

Create:

deploy/flux/image-repositories.yaml

apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: floodsight-frontend
  namespace: flux-system
spec:
  image: ghcr.io/afaqbabar/floodsight-frontend
  interval: 1m


deploy/flux/image-policies.yaml

apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: frontend-policy
  namespace: flux-system
spec:
  imageRepositoryRef: { name: floodsight-frontend }
  policy:
    semver:
      range: ">=0.1.0"


deploy/flux/image-update.yaml

apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageUpdateAutomation
metadata:
  name: floodsight-updater
  namespace: flux-system
spec:
  interval: 1m
  sourceRef:
    kind: GitRepository
    name: flux-system
  git:
    commit:
      author:
        name: fluxcdbot
        email: flux@example.com
      messageTemplate: "chore(images): update {{range .Changed.Entries}}{{.ImageRef}}{{end}}"
    push:
      branch: main
  update:
    strategy: Setters
    path: ./deploy/k8s/overlays/prod


Bootstrap Flux on your cluster once:

curl -s https://fluxcd.io/install.sh | sudo bash
flux bootstrap github \
  --owner=afaqbabar \
  --repository=floodsight \
  --branch=main \
  --path=deploy/k8s/overlays/prod \
  --personal

6) README (append “Build, Docker & GitOps”)

Add a section with:

## Containers & GitOps

### Build locally
npm i
npm run build
npm run preview

### Docker
docker build -f Dockerfile.nginx -t ghcr.io/afaqbabar/floodsight-frontend:dev-local .
docker run -p 8080:80 ghcr.io/afaqbabar/floodsight-frontend:dev-local

### Kubernetes
kubectl apply -k deploy/k8s/overlays/dev

### Flux (once, on cluster)
# see commands in deploy/flux/README (or above)

### Release flow
- Push to main → CI builds/pushes `:latest` and `:dev-<sha>`.
- Tag `v0.1.x` → optionally configure CI to add image tag `:v0.1.x`.
- Flux Image Automation bumps `overlays/prod` to the newest semver.


Guardrails

Do not change vercel.json.

Keep HTML structure; Vite will emit dist/ pages and hashed assets.

Leave Playwright/ESLint configs untouched.

Acceptance checks (Cursor should verify)

npm run build produces dist/ with all listed HTML pages.

Docker image serves site on port 80.

Push to main produces ghcr.io/afaqbabar/floodsight-frontend:latest.

kubectl apply -k deploy/k8s/overlays/dev yields a healthy Deployment/Service.

Commit plan

chore: add Vite config & scripts

chore: add Dockerfile.nginx, .dockerignore, compose

ci: GHCR multi-arch workflow

feat(k8s): base + dev/prod overlays

feat(flux): image automation

docs: README – Containers & GitOps
########
🧠 Cursor Agent Prompt — “Dual Deploy: Vercel + k3s (FluxCD)”

Role: Senior DevOps + Platform Engineer for the afaqbabar/floodsight repo.

Goal:
Maintain one repo that supports two deployment targets:

Vercel → static frontend / landing page

FluxCD on local k3s (Raspberry Pi) → GitOps-managed containerized deployment

Ensure both pipelines coexist without conflict and work automatically on each Git push.

Tasks
🟩 1. Keep current Vercel deployment intact

Do not modify or delete:

vercel.json

root HTML/CSS/JS assets under /assets and /index.html

Add .vercelignore at root to skip irrelevant files for Vercel builds:

deploy/
.github/
Dockerfile.nginx
flux.yaml
kustomization.yaml


Verify that a push to main still triggers a successful Vercel build.

🟦 2. Confirm Docker + FluxCD setup for k3s

Ensure Dockerfile.nginx builds from Vite output (dist/) at root.

Ensure .dockerignore excludes:

.vercel
vercel.json
deploy/
.github/


Verify .github/workflows/build-and-push.yml:

Context: .

File: ./Dockerfile.nginx

Platforms: linux/amd64,linux/arm64

Tags:

tags: |
  ${{ steps.iv.outputs.IMAGE }}:${{ steps.iv.outputs.TAG }}
  ${{ steps.iv.outputs.IMAGE }}:latest
  ${{ steps.iv.outputs.IMAGE }}:${{ github.ref_name }}


Triggers:

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

🧭 3. Prepare for local FluxCD deployment on Raspberry Pi (k3s)

Expect k3s installed via:

curl -sfL https://get.k3s.io | sh -
alias kubectl='sudo k3s kubectl'


Verify deploy/k8s/overlays/prod path is correct.

Flux bootstrap command (for documentation):

flux bootstrap github \
  --owner=afaqbabar \
  --repository=floodsight \
  --branch=main \
  --path=deploy/k8s/overlays/prod \
  --personal


Confirm all Flux files are located under deploy/flux/:

image-repositories.yaml

image-policies.yaml

image-update.yaml

Ensure all CR references (namespace: flux-system) are consistent.

⚙️ 4. Separate environment responsibilities

Add a short README section called “Dual Deploy Setup” explaining:

Vercel → static site

k3s + FluxCD → edge deployment

Mention that both run from the same branch, independently.

Example doc snippet for README (Cursor should append it):

## Dual Deployment Setup

FloodSight uses two parallel deployment flows:

| Target | Purpose | Trigger | Managed by |
|--------|----------|----------|-------------|
| **Vercel** | Public landing page | Push to `main` | Vercel auto-build |
| **k3s + FluxCD** | Local/Edge runtime | Push to `main` or tag | FluxCD GitOps |

Each environment is isolated:
- Vercel ignores `deploy/`, `.github/`, Dockerfiles.
- FluxCD ignores `vercel.json` and static-only configs.

This setup allows local Kubernetes testing and continuous public deployment from the same repo.

🔒 5. Optional: Private image handling for Flux

If GHCR images are private, document the creation of a Kubernetes pull secret:

kubectl -n floodsight create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=afaqbabar \
  --docker-password=<PAT with read:packages> \
  --docker-email=<you@example.com>


and link it under spec.template.spec.imagePullSecrets in the Deployment.

🧪 6. Final validation tasks

Vercel build succeeds and deploys the landing page.

GitHub Action pushes images to ghcr.io/afaqbabar/floodsight-frontend.

flux check on Pi passes all controllers.

flux get kustomizations -n flux-system shows successful reconciliation.

kubectl get svc -n floodsight confirms app reachable locally.

Expected deliverables

.vercelignore and .dockerignore files created.

Updated workflow (.github/workflows/build-and-push.yml) includes tag builds.

README section “Dual Deployment Setup” appended.

Verified manifests under deploy/ unchanged and valid.

PR created titled:
“feat: dual deploy support (Vercel + FluxCD k3s)”

####################
Cursor Agent Prompt — “Add health endpoint + deploy dashboard (Vercel + k3s)”

Role: Senior DevOps/FE engineer for afaqbabar/floodsight.

Goal:
Add a tiny /healthz JSON endpoint (served by nginx) and a friendly /health.html dashboard that shows build info (commit, tag, build time, image). Make it work on Vercel and in Kubernetes (k3s via Flux). Add Kubernetes liveness/readiness probes.

Constraints

Keep Vercel deploy intact (vercel.json untouched).

Continue using Vite for bundling.

Current Docker runtime is nginx (Dockerfile.nginx).

K8s manifests live under deploy/k8s/....

Tasks
1) Build metadata generator (Node script)

Create scripts/build-meta.js that writes assets/health.json at build time:

Fields:

status: "ok"

app: "floodsight"

commit: process.env.GIT_SHA || ""

tag: process.env.GIT_TAG || ""

branch: process.env.GIT_BRANCH || ""

image: process.env.IMAGE_REF || ""

builtAt: new Date().toISOString()

Ensure directory exists, pretty-print JSON.

Update package.json:

{
  "scripts": {
    "prebuild": "node scripts/build-meta.js",
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}

2) Health dashboard page

Add health.html (minimal page) that:

fetches /assets/health.json and shows the JSON in a pretty table

auto-refreshes every 5s

shows green/red status dot

Also add a plain-text version: version.txt (emit during prebuild in the same script, include commit/tag/builtAt on one line) — helpful for curl checks and Vercel.

3) Nginx /healthz endpoint (container)

Create nginx/health.conf:

server {
  listen 80 default_server;
  listen [::]:80 default_server;

  root   /usr/share/nginx/html;
  index  index.html;

  # JSON health endpoint
  location = /healthz {
    default_type application/json;
    return 200 '{"status":"ok"}';
  }

  # try static files first
  location / {
    try_files $uri $uri/ /index.html;
  }
}


Update Dockerfile.nginx to use this config:

FROM node:20-alpine AS build
WORKDIR /site
COPY package*.json ./
RUN npm ci || npm i
COPY . .
ARG GIT_SHA
ARG GIT_TAG
ARG GIT_BRANCH
ARG IMAGE_REF
ENV GIT_SHA=$GIT_SHA GIT_TAG=$GIT_TAG GIT_BRANCH=$GIT_BRANCH IMAGE_REF=$IMAGE_REF
RUN npm run build

FROM nginx:alpine
COPY --from=build /site/dist /usr/share/nginx/html
COPY nginx/health.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

4) CI: inject build metadata

Edit .github/workflows/build-and-push.yml:

Add build args so the image knows commit/tag/branch:

- name: Build & Push (multi-arch)
  uses: docker/build-push-action@v6
  with:
    context: .
    file: ./Dockerfile.nginx
    platforms: linux/amd64,linux/arm64
    push: true
    build-args: |
      GIT_SHA=${{ github.sha }}
      GIT_TAG=${{ github.ref_type == 'tag' && github.ref_name || '' }}
      GIT_BRANCH=${{ github.ref_name }}
      IMAGE_REF=ghcr.io/${{ github.repository }}-frontend:${{ github.ref_type == 'tag' && github.ref_name || 'latest' }}
    tags: |
      ${{ steps.iv.outputs.IMAGE }}:${{ steps.iv.outputs.TAG }}
      ${{ steps.iv.outputs.IMAGE }}:latest
      ${{ steps.iv.outputs.IMAGE }}:${{ github.ref_name }}


(Keep your existing login/setup/cache steps as-is.)

5) Kubernetes probes + annotations

Update deploy/k8s/base/frontend-deployment.yaml container spec to include probes:

readinessProbe:
  httpGet:
    path: /healthz
    port: 80
  initialDelaySeconds: 3
  periodSeconds: 5
livenessProbe:
  httpGet:
    path: /healthz
    port: 80
  initialDelaySeconds: 10
  periodSeconds: 10


Also add a label so you can see version in kubectl:

metadata:
  labels:
    app: frontend
    app.kubernetes.io/name: floodsight-frontend
    app.kubernetes.io/version: "v{{TAG}}" # Cursor: substitute with Kustomize var or leave static


(If you prefer immutable labels, keep it static; the health page already shows dynamic info.)

6) README additions (Vercel + k3s)

Append a section:

## Health endpoints

- **App dashboard:** `/health.html` (auto-refresh, shows commit/tag/time/image)
- **JSON probe:** `/assets/health.json`
- **Plain health:** `/healthz` (200 OK JSON, served by nginx)
- **Plain text version:** `/version.txt`

### Quick checks
- Browser: `http://<host>/health.html`
- Curl JSON: `curl -s http://<host>/assets/health.json | jq .`
- Probe: `curl -s -o /dev/null -w "%{http_code}\n" http://<host>/healthz`
- Text: `curl http://<host>/version.txt`

7) Vercel compatibility

No changes needed; Vercel will serve health.html, assets/health.json, and version.txt.
(Nginx-only /healthz will exist only in the Docker/K8s deployment, not on Vercel — that’s fine.)

Acceptance criteria

npm run build emits dist/assets/health.json and dist/version.txt.

health.html loads and displays build info.

Docker image exposes /healthz (returns 200 JSON), /health.html, /version.txt.

K8s Deployment has working readiness/liveness probes against /healthz.

README documents endpoints and curl snippets.

Commit plan

feat(health): add build-meta script and health dashboard

feat(nginx): add /healthz conf; wire Dockerfile

ci: pass build args (commit/tag/branch/image) to Docker

feat(k8s): add liveness/readiness probes

docs: README – health endpoints & checks
##############################

You are a senior frontend + DevSecOps engineer improving the FloodSight app.

Context:
- Repo: https://github.com/afaqbabar/floodsight
- It’s a Next.js + TypeScript project hosted on Vercel.
- We now have real Figma design tokens from the design team.
- We’ll make this repo design-system ready (tokens, Tailwind CSS vars), GDPR-compliant, and ready for CI/CD.

Tasks (phased):

--- PHASE 1 · Design Tokens Integration ---

1) Create a folder `/design/` in the root and add `figma-tokens.json` with these starter values:

{
  "color": {
    "primary": { "value": "#2563EB" },
    "secondary": { "value": "#64748B" },
    "accent": { "value": "#22C55E" },
    "warning": { "value": "#F59E0B" },
    "danger": { "value": "#EF4444" },
    "background": { "value": "#FFFFFF" },
    "foreground": { "value": "#0F172A" },
    "muted": { "value": "#F1F5F9" },
    "card": { "value": "#FFFFFF" },
    "border": { "value": "#E5E7EB" }
  },
  "radius": {
    "sm": { "value": "0.25rem" },
    "md": { "value": "0.5rem" },
    "lg": { "value": "0.75rem" },
    "xl": { "value": "1rem" }
  },
  "font": {
    "heading": { "value": "Inter, ui-sans-serif, system-ui" },
    "body": { "value": "Inter, ui-sans-serif, system-ui" },
    "mono": { "value": "ui-monospace, SFMono-Regular, Menlo, monospace" }
  },
  "fontSize": {
    "sm": { "value": "0.875rem" },
    "base": { "value": "1rem" },
    "lg": { "value": "1.125rem" },
    "xl": { "value": "1.25rem" },
    "2xl": { "value": "1.5rem" },
    "3xl": { "value": "1.875rem" }
  },
  "spacing": {
    "0": { "value": "0px" },
    "1": { "value": "4px" },
    "2": { "value": "8px" },
    "3": { "value": "12px" },
    "4": { "value": "16px" },
    "6": { "value": "24px" },
    "8": { "value": "32px" },
    "12": { "value": "48px" },
    "16": { "value": "64px" }
  },
  "shadow": {
    "sm": { "value": "0 1px 2px 0 rgb(0 0 0 / 0.05)" },
    "md": { "value": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)" }
  }
}

2) Create `/design/tokens.ts`:
   - Import figma-tokens.json and export it as a typed object.
   - Add an npm script `"tokens:apply"` to regenerate it later.

3) Update Tailwind config:
   - Map color, font, spacing, radius, shadow tokens to `theme.extend`.
   - Use CSS variables (`var(--color-primary)`) instead of hard-coded values.

4) In `/styles/globals.css`:
   - Define `:root` vars (colors, fonts, radii, spacing).
   - Add `.dark` overrides.
   - Ensure Tailwind’s base layer imports remain at top.

5) Verify `npm run dev` builds correctly.
   - The site should look identical but is now tokenized.

Commit: chore(design): add figma tokens and wire Tailwind CSS vars

--- PHASE 2 · Responsive Layout + Dashboard Structure ---

1) Create reusable components under `/components/site/`:
   - SiteHeader.tsx — FloodSight brand, nav (Dashboard, Alerts, About), CTA “Create Alert”.
   - SiteFooter.tsx — links: Impressum, Privacy, Cookies, “Change cookie settings”.

2) Create `/components/dashboard/`:
   - SidebarFilters.tsx — filters for Basin, Country, Lead Time, toggle groups for Forecast/Observations/Risk Zones.
   - MapPanel.tsx — placeholder map container.
   - RightPanel.tsx — placeholder forecast cards + CTA buttons.

3) Add pages:
   - `/dashboard` → responsive layout (lg: 3 columns [288px, 1fr, 320px], md: 2 columns, sm: stacked).
   - `/api/healthz` → returns JSON `{ok:true}`.

4) Use Tailwind utilities with your tokens (bg-primary, text-foreground, etc.).

Commit: feat(ui): scaffold responsive dashboard structure

--- PHASE 3 · GDPR + Legal Pages ---

1) Add pages:
   - `/impressum`
   - `/privacy`
   - `/cookies`
   Each with placeholder content, German + English sections.

2) Add `components/privacy/CookieBanner.tsx`:
   - Consent categories: Necessary (locked), Preferences, Analytics, Marketing.
   - Buttons: Accept all / Reject / Save preferences.
   - Store cookie `fs_consent=v1.{categories}`.
   - Gate analytics via helper in `/lib/consent.ts`.

3) Add a link in Footer to “Change cookie settings” (opens preferences modal).

4) Ensure compliance: no non-essential scripts before consent.

Commit: feat(gdpr): add cookie banner and legal pages

--- PHASE 4 · CI/CD and Deployment ---

1) Add `vercel.json`:
   - framework: nextjs
   - regions: eu
   - builds + rewrites (if needed).

2) Add `.env.example` with NEXT_PUBLIC_SITE_NAME, NEXT_PUBLIC_TAGLINE.

3) Add `.github/workflows/ci.yml`:
   - Steps: install, typecheck, lint, test, build, upload artifact.

4) Update README:
   - Add sections for design tokens, GDPR, and deployment (EU).

Commit: chore(ci+deploy): add vercel config and github actions workflow

--- PHASE 5 · (Optional Later) Container + GitOps ---

- Add Dockerfile, compose.yaml, and deploy/k8s/base.
- Add ArgoCD or FluxCD kustomization manifests.
- README: GHCR image push and overlay instructions.

Commit: feat(platform): add container + gitops manifests

--- QUALITY BAR ---
- Strict TypeScript, accessibility-first.
- Use shadcn/ui conventions.
- Respect prefers-reduced-motion.
- No breaking visual changes unless tokens specify.

At the end of each phase, show changed files and a short diff summary.

##############################################################################################################
###########################################################################################################
######################################################################################################

Project: 🌊 FloodSight — Backend API
Repository: https://github.com/afaqbabar/floodsight

Goal: Implement a full backend inside /backend with FastAPI, Postgres/PostGIS, Prefect (for scheduled data ingestion), and CI/CD.
The frontend (Next.js) already exists and is deployed on Vercel.

🧩 PHASE A — Backend Architecture & Setup

Create a new folder /backend and implement this structure:

backend/
  app/
    core/ (config, logging, security)
    db/ (session, base, models, migrations)
    api/v1/ (router, endpoints)
    services/ (glefas.py, geoutils.py, seed.py)
    workers/ (flows.py)
    main.py
  tests/
  Dockerfile
  docker-compose.yml
  pyproject.toml
  alembic.ini
  .env.example


Use FastAPI + SQLAlchemy (async) + Postgres/PostGIS.

Add models:

Station: id, code, name, lat, lon, river_basin

Forecast: station_id, ts, lead_hours, discharge_m3s

Alert: station_id, issued_at, level, probability, message

Add endpoints:

/v1/health → simple status

/v1/stations → list

/v1/forecasts → list + POST /ingest-dev

/v1/alerts → compute thresholds

Use alembic migrations; asyncpg driver.

Configure JWT-based auth via Supabase (stub OK in dev mode).

Add Docker Compose (FastAPI + PostGIS).

Add Prometheus /metrics endpoint.

Write README_backend.md with instructions to run locally:

docker compose up --build
alembic upgrade head
python -m app.services.seed
open http://localhost:8080/docs

⚙️ PHASE B — Data Flow & API Logic

Add services/seed.py to populate a few sample stations (Berlin-Spree, Elbe-Dresden, etc.).

Add services/glefas.py:

Create a stub function ingest_fake_forecast() that populates fake data for 72h lead time.

Later it will fetch ECMWF GloFAS GRIB files and parse via xarray + cfgrib.

Add /v1/forecasts/ingest-dev to call that function manually.

Add /v1/alerts to aggregate recent forecasts and output alert levels (info, warning, severe).

End-to-end test flow:

alembic upgrade head

seed stations

POST /v1/forecasts/ingest-dev

GET /v1/alerts

🕒 PHASE B2 — Prefect Integration (Automated ingestion)

Install prefect in dependencies.

Add a file backend/app/workers/flows.py implementing a Prefect flow:

from datetime import datetime, timezone
from prefect import flow, task
from app.db.session import AsyncSessionLocal
from app.services.glefas import ingest_fake_forecast
import asyncio

@task
async def fetch_and_store_forecasts():
    async with AsyncSessionLocal() as db:
        await ingest_fake_forecast(db)
        print(f"[{datetime.now(timezone.utc)}] Ingest completed.")

@flow(name="floodsight-forecast-ingest", retries=1, retry_delay_seconds=60)
def floodsight_ingest_flow():
    asyncio.run(fetch_and_store_forecasts())

if __name__ == "__main__":
    floodsight_ingest_flow()


Add this flow to docker-compose.yml as a worker service (optional).

Schedule it using Prefect Cloud/Server or via cron (@hourly) for now.

Ensure logs appear in console; in later steps, we’ll integrate Prefect Orion UI or Prefect Cloud dashboard.

🔐 PHASE C — DevSecOps Integration

Create .github/workflows/backend-ci.yml to:

Run Python install & lint

Build and push Docker image to GHCR

Add /deploy/k8s/base/api-deployment.yaml for K3s (Raspberry Pi) deployment:

Deployment, Service, and Ingress manifests

ReadinessProbe: /v1/health

Add .env.example including:

DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/floodsight
SUPABASE_JWKS_URL=https://<project>.supabase.co/auth/v1/keys
PREFECT_API_URL=http://prefect:4200


Add vercel.json rewrite:

{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api.floodsight.example.com/:path*" }
  ]
}


Configure container scanning (Trivy) and Dependabot.

Ensure CI logs print image tag and push status.

📦 Dependencies
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
alembic
pydantic-settings
httpx
PyJWT
prefect
python-multipart
prometheus-client

✅ Deliverables

All backend code committed under /backend

Working local environment: docker compose up

API available at http://localhost:8080/docs

Prefect flow runs manually (python -m app.workers.flows) and can be scheduled

README_backend.md explaining setup & architecture

CI pipeline building + pushing image to GHCR

Make everything clean, modular, async, and production-ready.
Use PEP8 formatting, type hints, and concise docstrings.
Include comments for where real ECMWF GloFAS ingestion will plug in later.

When done, print:

Summary of created/modified files

Next step recommendation (e.g. integrate real ECMWF data or deploy to K3s)
```
