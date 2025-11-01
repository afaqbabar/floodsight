# Testing Guide

This document explains how to run tests, validate code quality, and audit performance for FloodSight.

---

## 🧪 Test Suite Overview

FloodSight uses:
- **Playwright** for end-to-end browser tests
- **ESLint** for JavaScript linting
- **Prettier** for code formatting
- **html-validate** for HTML validation
- **Lighthouse** for performance audits

---

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run all checks
npm run format:check    # Check formatting
npm run lint            # Lint JavaScript
npm run lint:html       # Validate HTML
npm test                # Run Playwright tests
```

---

## 📋 Test Categories

### 1. Unit Tests (N/A)

Currently no unit tests (static site with minimal JS). If adding complex logic, consider:
- Vitest or Jest for JavaScript unit tests
- Test DOM helpers, form validation, etc.

### 2. End-to-End Tests (Playwright)

**Run tests**:
```bash
npm test                # Headless mode
npm run test:ui         # Interactive UI mode
```

**Test coverage**:
- ✅ Homepage loads with correct title
- ✅ Navigation links work (smooth scroll)
- ✅ Signup form validation
- ✅ Legal pages load (impressum, privacy, terms, security)
- ✅ Footer links navigate correctly
- ✅ 404 page handling
- ✅ Mobile responsiveness
- ✅ Accessibility (landmarks, alt text, labels)

**Test files**: `tests/smoke.spec.js`

**Browsers tested**:
- Chromium (desktop)
- Firefox (desktop)
- Mobile Safari (iPhone 13 simulation)

### 3. Code Quality

#### JavaScript Linting (ESLint)

```bash
npm run lint
```

**Rules**:
- ESLint recommended rules
- Browser globals enabled
- ES2021+ syntax
- Warns on unused vars (except `_` prefix)

**Config**: `.eslintrc.json`

#### Code Formatting (Prettier)

```bash
npm run format:check    # Check only
npm run format          # Fix issues
```

**Style**:
- 2 spaces indentation
- Single quotes
- Trailing commas (ES5)
- 100 character line width

**Config**: `.prettierrc`

#### HTML Validation (html-validate)

```bash
npm run lint:html
```

**Checks**:
- Valid HTML5 structure
- Proper nesting
- Required attributes
- Semantic elements

**Config**: `.html-validaterc.json`

---

## 🔍 Manual Testing Checklist

### Desktop (Chrome/Firefox/Safari)

- [ ] Homepage loads without errors
- [ ] All sections visible (hero, features, pricing, etc.)
- [ ] Smooth scroll navigation works
- [ ] Header shadow appears on scroll
- [ ] Active nav link highlights on scroll
- [ ] Signup form validation works
- [ ] Form submits to Formspree (check network tab)
- [ ] Code sample "Copy" button works
- [ ] Footer links navigate correctly
- [ ] Legal pages load and are readable

### Mobile (Chrome DevTools / Real Device)

- [ ] Responsive layout (no horizontal scroll)
- [ ] Mobile nav toggle appears
- [ ] Nav menu opens/closes correctly
- [ ] Touch targets are at least 44x44px
- [ ] Text is readable (min 16px)
- [ ] Forms are usable (proper zoom behavior)
- [ ] Footer is not cut off

### Accessibility

- [ ] Tab navigation works (logical order)
- [ ] Skip link appears on Tab
- [ ] All interactive elements keyboard-accessible
- [ ] Form labels properly associated
- [ ] Images have alt text
- [ ] Headings are hierarchical (h1 → h2 → h3)
- [ ] ARIA landmarks present (banner, main, contentinfo)
- [ ] Color contrast ≥4.5:1 (use browser DevTools)
- [ ] Focus indicators visible

### SEO

- [ ] `<title>` present on all pages
- [ ] Meta description present
- [ ] Open Graph tags present
- [ ] Twitter card tags present
- [ ] Canonical URL set correctly
- [ ] `robots.txt` accessible
- [ ] `sitemap.xml` accessible and valid
- [ ] Structured data (JSON-LD) valid

---

## 📊 Performance Testing (Lighthouse)

### Running Lighthouse

**Option 1: CLI (Recommended)**

```bash
# Start dev server
npm run dev &

# Wait 2 seconds, then run Lighthouse
sleep 2
npm run lighthouse
```

**Option 2: Chrome DevTools**

1. Open site in Chrome
2. DevTools → Lighthouse tab
3. Select categories: Performance, Accessibility, Best Practices, SEO
4. Click "Analyze page load"

### Interpreting Results

**Target Scores**:
- Performance: ≥90
- Accessibility: ≥85
- Best Practices: ≥90
- SEO: ≥90

**Key Metrics**:
- **FCP (First Contentful Paint)**: <1.8s (good)
- **LCP (Largest Contentful Paint)**: <2.5s (good)
- **TBT (Total Blocking Time)**: <200ms (good)
- **CLS (Cumulative Layout Shift)**: <0.1 (good)
- **Speed Index**: <3.4s (good)

### Common Issues & Fixes

**Low Performance**:
- ❌ Large images → ✅ Optimize with ImageOptim, use WebP
- ❌ Render-blocking JS → ✅ Use `defer` or `type="module"`
- ❌ Unused CSS → ✅ Remove or split into critical/deferred

**Low Accessibility**:
- ❌ Missing alt text → ✅ Add descriptive alt to all images
- ❌ Low contrast → ✅ Use color contrast checker
- ❌ Missing labels → ✅ Associate `<label for="id">` with inputs

**Low SEO**:
- ❌ Missing meta description → ✅ Add unique description per page
- ❌ Non-crawlable links → ✅ Use `<a href="...">` not `<div onclick>`

---

## 🐛 Debugging Failed Tests

### Playwright Test Fails

1. **View trace**:
   ```bash
   npm run test:ui
   ```
   Click on failed test, view trace timeline.

2. **Check screenshot**:
   - Screenshots saved to `test-results/`

3. **Increase timeout** (if test is slow):
   ```js
   test('slow test', async ({ page }) => {
     test.setTimeout(10000); // 10 seconds
     // ...
   });
   ```

### Linting Errors

**ESLint**:
```bash
npm run lint
```
Fix manually or use `eslint --fix` (not recommended for auto-fixing).

**Prettier**:
```bash
npm run format
```
Auto-fixes formatting issues.

**html-validate**:
- Read error message (e.g., "unclosed tag")
- Fix HTML manually
- Re-run `npm run lint:html`

---

## 🔄 Continuous Integration (Future)

When ready for CI/CD, add GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm install
      - run: npm run format:check
      - run: npm run lint
      - run: npm run lint:html
      - run: npx playwright install --with-deps
      - run: npm test
      - run: npm run lighthouse
```

---

## 📚 Resources

- **Playwright Docs**: [playwright.dev](https://playwright.dev/)
- **Lighthouse Docs**: [developers.google.com/web/tools/lighthouse](https://developers.google.com/web/tools/lighthouse)
- **ESLint Rules**: [eslint.org/docs/rules](https://eslint.org/docs/rules/)
- **Prettier Options**: [prettier.io/docs/en/options.html](https://prettier.io/docs/en/options.html)
- **html-validate**: [html-validate.org](https://html-validate.org/)

---

## ✅ Pre-Deploy Checklist

Before deploying to production:

- [ ] All tests pass (`npm test`)
- [ ] Code is formatted (`npm run format:check`)
- [ ] No linting errors (`npm run lint`, `npm run lint:html`)
- [ ] Lighthouse scores meet targets
- [ ] Manual testing complete (desktop + mobile)
- [ ] Legal pages reviewed and up-to-date
- [ ] Forms submit correctly
- [ ] 404 page works
- [ ] All links work (no 404s)
- [ ] Meta tags updated (canonical URL, OG image)
- [ ] Sitemap reflects current pages

---

**Questions?** Open an issue or contact [hello@floodsight.com](mailto:hello@floodsight.com).

