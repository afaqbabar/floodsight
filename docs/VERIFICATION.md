# Post-Deployment Verification Checklist

Use this checklist after pushing to verify all assets load correctly on Vercel.

---

## 🔍 Browser Console Check (Critical)

### Step 1: Open Your Deployed Site

```
https://floodsight.vercel.app/
```

### Step 2: Open Browser DevTools

- **Chrome/Edge**: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Option+I` (Mac)
- **Firefox**: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Option+I` (Mac)

### Step 3: Check Console Tab

Look for any **red error messages** that say:

```
Failed to load resource: the server responded with a status of 404 (Not Found)
```

---

## ✅ Asset Verification Checklist

### SVG Assets (Must Load with 200 OK)

Visit your site and check the Console. You should see **NO errors** for these files:

**Hero Section:**

- [ ] `/hero-map-placeholder.svg` - Status: 200 OK
  - Should display map with river stations and chart

**Partner Logos:**

- [ ] `/logos/citylab.svg` - Status: 200 OK
- [ ] `/logos/insurtech.svg` - Status: 200 OK
- [ ] `/logos/university.svg` - Status: 200 OK
- [ ] `/logos/iot.svg` - Status: 200 OK
  - All should display in the "Trusted by" section

---

## 🖼️ Visual Verification

### Hero Section

- [ ] Map preview graphic visible (shows river stations, alerts, chart)
- [ ] No broken image icon
- [ ] Colors match theme (dark blue background, aqua accents)

### Trust Section (Partner Logos)

- [ ] 4 logos visible in a row
- [ ] All logos are grayscale with text labels
- [ ] No broken image icons
- [ ] Logos are properly aligned

### Overall Page

- [ ] No layout shifts or jumps
- [ ] All sections load smoothly
- [ ] No console errors at all

---

## 🧪 Network Tab Check (Detailed)

1. Open DevTools → **Network** tab
2. Refresh the page (`F5` or `Cmd+R`)
3. Filter by **Img** or **All**
4. Look for the following requests:

| File                       | Status | Size    | Notes       |
| -------------------------- | ------ | ------- | ----------- |
| `hero-map-placeholder.svg` | 200    | ~2.2 KB | Should load |
| `logos/citylab.svg`        | 200    | ~473 B  | Should load |
| `logos/insurtech.svg`      | 200    | ~567 B  | Should load |
| `logos/university.svg`     | 200    | ~632 B  | Should load |
| `logos/iot.svg`            | 200    | ~692 B  | Should load |

**All should show green status (200)**, not red (404).

---

## 🚨 If You Still See 404 Errors

### Common Issues & Fixes

#### Issue 1: Vercel hasn't deployed yet

**Symptom**: Old version of site still showing  
**Fix**:

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Check deployment status
3. Wait for deployment to complete (usually 1-2 minutes)
4. Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

#### Issue 2: Browser cache

**Symptom**: Old 404 errors cached  
**Fix**:

1. Hard refresh: `Ctrl+Shift+R` or `Cmd+Shift+R`
2. Or open in incognito/private window
3. Or clear browser cache

#### Issue 3: Wrong file paths in HTML

**Symptom**: 404 for assets in wrong location  
**Fix**:

1. Check `index.html` paths match actual file locations
2. Should be `/hero-map-placeholder.svg` (root)
3. Should be `/logos/citylab.svg` (in logos folder)

#### Issue 4: Files not in git repo

**Symptom**: Files not on Vercel  
**Fix**:

```bash
# Check files are tracked
git ls-files | grep -E "(hero-map|logos)"

# Should show:
# hero-map-placeholder.svg
# logos/citylab.svg
# logos/insurtech.svg
# logos/iot.svg
# logos/university.svg

# If missing, ensure you pushed:
git push origin main
```

---

## 📸 Screenshot Test (Optional)

Take screenshots of:

1. Browser console (should be empty of errors)
2. Hero section (map should be visible)
3. Trust section (4 logos should be visible)

Save these as proof that everything loads correctly.

---

## ✅ Success Criteria

**Your deployment is successful when:**

✅ No red errors in browser console  
✅ No 404 (Not Found) errors  
✅ Hero map graphic displays correctly  
✅ All 4 partner logos display correctly  
✅ Page loads smoothly without layout shifts  
✅ Network tab shows all SVGs with 200 status

---

## 📋 Quick Verification Command

For a quick check, run this in your browser console:

```javascript
// Check if images loaded successfully
const images = document.querySelectorAll('img');
const failed = Array.from(images).filter((img) => !img.complete || img.naturalHeight === 0);
if (failed.length === 0) {
  console.log('✅ All images loaded successfully!');
} else {
  console.error(
    '❌ Failed images:',
    failed.map((img) => img.src)
  );
}
```

---

## 🎉 Expected Result

After running all checks, you should see:

- ✅ **Console**: No errors
- ✅ **Network**: All assets 200 OK
- ✅ **Visual**: All images display correctly
- ✅ **Script**: "All images loaded successfully!"

---

## 📧 Report Issue

If you still see 404 errors after following all steps:

1. Take a screenshot of:
   - Browser console
   - Network tab (filtered to show the 404s)
   - The deployment status on Vercel

2. Check:
   - Which files are 404ing
   - Are they in your git repo?
   - Did the push succeed?
   - Has Vercel finished deploying?

3. Contact: hello@floodsight.com

---

**Last Updated**: 2025-11-01  
**Related Files**: `hero-map-placeholder.svg`, `logos/*.svg`  
**Deployment**: Vercel auto-deploy from main branch
