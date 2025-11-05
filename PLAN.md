# FloodSight Improvement Plan

## 🎯 Goals
1. Fix routing, SEO, and deployment issues for Vercel
2. Improve performance, mobile UX, and accessibility
3. Add quality tooling (linting, formatting, testing)
4. Modularize JavaScript for maintainability
5. Ensure all legal pages and links work correctly

---

## 🔧 Changes by Category

### 1. **Routing & Links**
- ✅ Already clean: `vercel.json` rewrites work for `/impressum`, `/privacy`, `/terms`, `/security`
- 🔧 Fix footer links: remove `.html` extensions in legal pages (impressum, privacy, terms, security)
- 🆕 Add 404.html page with helpful navigation back to home
- 🔧 Update all internal links to use clean routes (no `.html`)

### 2. **SEO**
- 🔧 Update `sitemap.xml`: change all `floodsight.netlify.app` → `floodsight.vercel.app`
- 🔧 Update `robots.txt`: confirm sitemap URL
- 🔧 Fix canonical URLs in `index.html`: remove commented-out line, keep vercel.app
- 🔧 Add `<title>` + `<meta description>` to `thanks.html`
- 🔧 Add structured data (JSON-LD) to legal pages where appropriate
- 🆕 Add `sitemap.xml` entry for `404.html`

### 3. **Performance**
- 🆕 Add lazy-loading to images: `loading="lazy"` for hero/trust logos
- 🆕 Add `width` + `height` to images (prevent CLS)
- 🔧 Defer non-critical JS: already has `defer` ✅
- 🆕 Add minimal CSS inlining for above-the-fold critical styles (optional, test first)
- 🔧 Optimize CSS: remove unused rules, minify for production
- 🆕 Compress assets: add `public` folder structure if needed

### 4. **Mobile & Accessibility**
- 🔧 Fix mobile nav toggle: extract into module, improve ARIA states
- 🔧 Test responsive grid breakpoints (hero, features, steps)
- 🔧 Add `:focus-visible` styles for keyboard nav
- 🔧 Ensure form labels are properly associated
- 🔧 Add landmarks: `<nav>`, `<main>`, `<footer>` already present ✅
- 🔧 Test with Lighthouse for a11y score ≥85

### 5. **Forms**
- ✅ Form already uses Formspree (no backend needed) ✅
- 🔧 Update legal pages to reflect "Formspree" not "Netlify Forms"
- 🆕 Add fallback `mailto:` option behind config flag (env var or data attribute)
- 🔧 Improve client-side validation messages (ARIA live region)

### 6. **I18n (Optional - Not Implemented Yet)**
- ⚠️ Prompt mentions DE/EN toggle, but codebase doesn't have one
- 🆕 Add minimal i18n: language switcher in header (persist in localStorage)
- 🆕 Create `i18n.js` module with DE/EN strings
- 🆕 Add `lang` attribute toggle for SEO
- ⏩ **Decision**: Skip for now (requires full translation of content). Mark as future enhancement.

### 7. **Legal Pages**
- ✅ Impressum, Privacy, Terms, Security already exist
- 🔧 Fix footer nav links to be consistent
- 🔧 Update hosting references: "Netlify" → "Vercel" in Impressum
- 🔧 Add proper semantic structure: `<article>`, headings
- 🔧 Fix breadcrumbs/navigation in headers of legal pages

### 8. **JavaScript Refactoring**
- 🔧 Split `floodsight.js` into ES modules:
  - `dom.js` – DOM helpers (qs, qsa)
  - `nav.js` – Navigation toggle, smooth scroll, active link
  - `forms.js` – Form validation, submission
  - `utils.js` – Clipboard, year update
- 🔧 Use ES6 modules with `type="module"` in HTML
- 🔧 Remove global scope leaks (already uses IIFE ✅)

### 9. **Build & Deploy**
- 🆕 Add `package.json` with:
  - `npm run format` – Prettier
  - `npm run lint` – ESLint
  - `npm run lint:html` – html-validate
  - `npm run test` – Playwright smoke tests
  - `npm run lighthouse` – Local Lighthouse CI
- 🆕 Add `.prettierrc`, `.eslintrc.json`, `.html-validaterc.json`
- 🔧 Update `vercel.json`: add `trailingSlash: false`, confirm redirects
- 🆕 Add `.env.example` for future analytics/tracking flags

### 10. **Quality & Testing**
- 🆕 Add Prettier config (2 spaces, single quotes, trailing commas)
- 🆕 Add ESLint (eslint:recommended + browser globals)
- 🆕 Add `html-validate` for HTML validation
- 🆕 Add Playwright test:
  - Visit `/`
  - Click nav links (features, pricing, contact)
  - Visit legal pages (impressum, privacy, terms)
  - Check 404 handling
- 🆕 Add Lighthouse checklist (run `npm run lighthouse`, target: P≥90, A≥85, SEO≥90)

---

## 📦 Deliverables

1. **PLAN.md** (this file) ✅
2. **TESTING.md** – How to run dev server, build, tests, Lighthouse
3. **README.md** – Quick setup, deploy to Vercel, project overview
4. **Updated files**:
   - `index.html`, legal pages (routing, SEO, images)
   - `assets/js/` – Modularized (dom.js, nav.js, forms.js, utils.js)
   - `assets/css/floodsight.css` – Cleanup, optimizations
   - `vercel.json` – Tweaks
   - `sitemap.xml`, `robots.txt` – Domain updates
   - `404.html` – New
5. **Tooling files**:
   - `package.json`, `.prettierrc`, `.eslintrc.json`, `.html-validaterc.json`
   - `playwright.config.js`, `tests/smoke.spec.js`
   - `.env.example`
6. **DIFF.md** – Summary of all changes (generated after implementation)
7. **Lighthouse report** – Markdown with scores

---

## ✅ Acceptance Criteria

- [ ] All links work on Vercel (no 404s for `/impressum`, `/privacy`, etc.)
- [ ] Lighthouse: Performance ≥90, Best Practices ≥90, SEO ≥90, Accessibility ≥85
- [ ] `npm run format` and `npm run lint` pass with no errors
- [ ] `npm run lint:html` validates all HTML files
- [ ] `npm run test` (Playwright) passes smoke tests
- [ ] Legal pages present, accessible, and correctly linked
- [ ] No i18n toggle (future enhancement)
- [ ] Forms submit to Formspree (already configured)
- [ ] README shows clear steps for local dev + Vercel deploy
- [ ] No tracking/analytics by default (already true ✅)

---

## 🚀 Implementation Order

1. Setup tooling (package.json, linters, formatters)
2. Fix SEO/routing (sitemap, links, 404)
3. Refactor JavaScript into modules
4. Optimize performance (images, lazy-loading)
5. Update legal pages (hosting references, links)
6. Add Playwright tests
7. Run Lighthouse, document results
8. Write README.md + TESTING.md + DIFF.md

---

**Estimated time**: 2-3 hours
**Complexity**: Medium (modularization + tooling setup)
**Risk**: Low (static site, no backend changes)

