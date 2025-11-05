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

- **Python 3** (for local dev server)
- **Node.js 18+** (for tooling: linting, testing, lighthouse)

### Local Development

```bash
# Clone repository
git clone https://github.com/afaqbabar/floodsight.git
cd floodsight

# Install dependencies
npm install

# Start development server
npm run dev
# Opens at http://localhost:8000
```

### Project Structure

```
floodsight/
├── index.html              # Main landing page
├── impressum.html          # Legal imprint (DE)
├── privacy.html            # Privacy policy (EN/DE)
├── terms.html              # Terms of service
├── security.html           # Security disclosure
├── thanks.html             # Form success page
├── 404.html                # Custom 404 page
├── assets/
│   ├── css/
│   │   └── floodsight.css  # Styles
│   └── js/
│       ├── main.js         # Entry point (ES module)
│       ├── nav.js          # Navigation logic
│       ├── forms.js        # Form validation
│       ├── utils.js        # Utilities
│       └── dom.js          # DOM helpers
├── scripts/
│   └── lighthouse.js       # Lighthouse CI runner
├── tests/
│   └── smoke.spec.js       # Playwright tests
├── vercel.json             # Vercel config (routes, headers)
├── sitemap.xml             # SEO sitemap
├── robots.txt              # Crawler directives
└── package.json            # Dependencies & scripts
```

---

## 🛠️ Development Scripts

```bash
# Development
npm run dev              # Start local server (port 8000)

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

