# Pre-Flight Checklist

This document provides step-by-step instructions to complete the FloodSight setup and run final validation.

---

## 📋 Setup Requirements

### 1. Install Node.js and npm

The project requires Node.js 18+ for development tooling.

**On Raspberry Pi OS / Debian / Ubuntu:**

```bash
# Install Node.js 18.x (LTS)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version   # Should show v18.x or higher
npm --version    # Should show 9.x or higher
```

**Alternative (using nvm):**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

---

## 🚀 First-Time Setup

```bash
# Navigate to project directory
cd /home/lenovo/scrimba/floodsight/floodsight

# Install dependencies
npm install

# This installs:
# - Playwright (browser testing)
# - ESLint (JS linting)
# - Prettier (code formatting)
# - html-validate (HTML validation)
# - Lighthouse (performance auditing)
```

---

## ✅ Validation Steps

### Step 1: Code Quality Checks

```bash
# Format code
npm run format

# Check formatting (should pass)
npm run format:check

# Lint JavaScript
npm run lint

# Validate HTML
npm run lint:html
```

**Expected**: All checks should pass with no errors.

---

### Step 2: Run Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install --with-deps

# Run tests
npm test
```

**Expected**: 15+ tests should pass covering:

- Navigation and smooth scroll
- Form validation
- Legal pages loading
- Mobile responsiveness
- Accessibility checks

---

### Step 3: Run Lighthouse Audit

```bash
# Terminal 1: Start dev server
npm run dev

# Terminal 2: Run Lighthouse
npm run lighthouse
```

**Expected Results**:

- Performance: ≥90
- Accessibility: ≥85
- Best Practices: ≥90
- SEO: ≥90

**Report Location**: `lighthouse-report/report.html` and `lighthouse-report/LIGHTHOUSE.md`

---

### Step 4: Manual Testing

#### Desktop Testing (Chrome/Firefox)

1. Open http://localhost:8000
2. Check:
   - [ ] Hero section loads
   - [ ] Navigation smooth scrolls
   - [ ] Active link highlights on scroll
   - [ ] Header shadow appears on scroll
   - [ ] Form validation works
   - [ ] Code sample copy button works
   - [ ] Footer links navigate to legal pages

#### Mobile Testing (Chrome DevTools)

1. Open DevTools → Toggle device toolbar (Ctrl+Shift+M)
2. Select "iPhone 13" or similar
3. Check:
   - [ ] Mobile nav toggle appears
   - [ ] Nav menu opens/closes
   - [ ] All text is readable
   - [ ] No horizontal scroll
   - [ ] Touch targets are large enough

#### Keyboard/Accessibility Testing

1. Tab through page
2. Check:
   - [ ] Skip link appears on first Tab
   - [ ] All interactive elements are keyboard-accessible
   - [ ] Focus indicators are visible
   - [ ] Form can be completed with keyboard only

---

## 🌐 Deploy to Vercel

### Option 1: Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Follow prompts:
# - Link to existing project or create new
# - Confirm settings
# - Deploy
```

### Option 2: GitHub Integration

1. Push code to GitHub:

   ```bash
   git add .
   git commit -m "Complete FloodSight improvements"
   git push origin main
   ```

2. Go to [vercel.com](https://vercel.com)
3. Click "Import Project"
4. Select your GitHub repository
5. Vercel auto-detects settings
6. Click "Deploy"

**Post-Deploy**:

- ✅ Test preview URL (Vercel provides)
- ✅ Verify all routes work: `/`, `/impressum`, `/privacy`, `/terms`, `/security`
- ✅ Test 404 page: visit non-existent route
- ✅ Test form submission
- ✅ Run Lighthouse on live URL

---

## 🔧 Troubleshooting

### "npm: command not found"

→ Node.js not installed. See "Install Node.js" section above.

### "playwright: command not found"

→ Run `npx playwright install --with-deps`

### Lighthouse fails with "ECONNREFUSED"

→ Ensure dev server is running (`npm run dev`) before running Lighthouse

### Tests fail with timeout

→ Increase timeout in `playwright.config.js` or check if dev server is running

### ESLint errors in new code

→ Run `npm run format` first, then fix remaining issues manually

---

## 📊 Performance Optimization Tips

If Lighthouse scores are below target:

### Performance < 90

- Optimize images (use WebP, compress)
- Minify CSS/JS
- Enable compression on Vercel (automatic)
- Reduce third-party scripts (already none ✓)

### Accessibility < 85

- Check color contrast (use DevTools)
- Add missing alt text
- Ensure proper heading hierarchy
- Test with screen reader

### Best Practices < 90

- Review console for errors
- Check HTTPS usage (Vercel handles ✓)
- Verify no mixed content

### SEO < 90

- Add meta descriptions to all pages
- Ensure proper title tags
- Verify sitemap is accessible
- Check robots.txt

---

## 🎉 Success Criteria

✅ **Code Quality**:

- All linting passes
- Code is formatted consistently

✅ **Functionality**:

- All tests pass
- Manual testing complete
- Forms work

✅ **Performance**:

- Lighthouse scores meet targets
- No console errors

✅ **Deployment**:

- Deployed to Vercel
- All routes work
- Legal pages accessible

---

## 📧 Support

If you encounter issues:

1. Check `TESTING.md` for detailed testing guidance
2. Review `README.md` for project overview
3. Open an issue on GitHub
4. Contact: [hello@floodsight.com](mailto:hello@floodsight.com)

---

**Next Steps After This Checklist**:

1. Complete Node.js installation
2. Run all validation steps above
3. Deploy to Vercel
4. Test production deployment
5. Archive `PREFLIGHT.md` (optional - for reference only)

Good luck! 🚀
