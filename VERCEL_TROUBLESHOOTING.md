# Vercel Frontend Not Updating - Troubleshooting Guide

## 🎯 Your Backend URL

```
https://shoe-mere-livestock-mild.trycloudflare.com
```

**Status**: ✅ Working and accessible

---

## 🔍 Common Issues & Solutions

### Issue 1: Environment Variable Not Applied ⭐ Most Common

**Problem**: You added the environment variable but didn't redeploy.

**Solution**:

1. Go to: https://vercel.com/YOUR_PROJECT/deployments
2. Find your latest deployment
3. Click the **three dots (...)** on the right
4. Click **"Redeploy"**
5. **DO NOT** just click "Promote to Production" - you must **"Redeploy"**
6. Wait for build to complete (shows as "Ready")

**Why**: Environment variables are only applied at **build time**, not runtime.

---

### Issue 2: Wrong Environment Selected

**Problem**: Variable added to wrong environment (Preview/Development instead of Production).

**Solution**:

1. Go to: https://vercel.com/YOUR_PROJECT/settings/environment-variables
2. Check which environment has the variable
3. Make sure **"Production"** is checked ✓
4. If not, edit the variable and check "Production"
5. Redeploy

---

### Issue 3: Browser Cache

**Problem**: Your browser is showing the old cached version.

**Solution**:

- **Hard Refresh**:
  - Windows/Linux: `Ctrl + Shift + R`
  - Mac: `Cmd + Shift + R`
- **Or**: Open in Incognito/Private window
- **Or**: Clear browser cache and reload

---

### Issue 4: Wrong Variable Name

**Problem**: Using wrong environment variable name in code.

**Check your frontend code**:

```javascript
// For Vite (React/Vue/Svelte)
const API_URL = import.meta.env.VITE_API_URL; // ✅ Correct for Vite
console.log('API URL:', API_URL);

// For Next.js
const API_URL = process.env.NEXT_PUBLIC_API_URL; // ✅ Correct for Next.js

// For Create React App
const API_URL = process.env.REACT_APP_API_URL; // ✅ Correct for CRA
```

**In Vercel**, the variable name must be:

- `VITE_API_URL` for Vite projects
- `NEXT_PUBLIC_API_URL` for Next.js projects
- `REACT_APP_API_URL` for Create React App projects

---

### Issue 5: Code Not Using Environment Variable

**Problem**: Frontend code is hardcoded or not reading the env variable.

**Check your code**:

```javascript
// ❌ BAD - Hardcoded
const API_URL = 'http://localhost:8080';

// ✅ GOOD - Uses environment variable with fallback
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Use it
fetch(`${API_URL}/v1/stations`)
  .then((r) => r.json())
  .then(console.log);
```

---

### Issue 6: Build Failed

**Problem**: Deployment failed but you didn't notice.

**Solution**:

1. Go to: https://vercel.com/YOUR_PROJECT/deployments
2. Check if latest deployment shows:
   - ✅ "Ready" (good)
   - ❌ "Error" or "Failed" (problem)
3. If failed, click on it and check "Build Logs"
4. Fix any errors and push/redeploy

---

### Issue 7: Deployment Still Building

**Problem**: You redeployed but it's still building.

**Solution**:

- Wait for "Building" → "Ready" status (usually 1-3 minutes)
- Refresh Vercel deployments page to see current status
- Don't check your app until it shows "Ready"

---

### Issue 8: Wrong Deployment URL

**Problem**: Checking old deployment URL instead of new one.

**Solution**:

- Each deployment has its own URL
- Check the URL of the LATEST deployment
- Or use your production URL (e.g., `your-project.vercel.app`)

---

## 🧪 Step-by-Step Verification

### Step 1: Verify Environment Variable

In Vercel:

1. Go to: **Settings** → **Environment Variables**
2. Confirm you see:
   ```
   Name:  VITE_API_URL
   Value: https://shoe-mere-livestock-mild.trycloudflare.com
   Environment: ✓ Production
   ```

### Step 2: Force Redeploy

1. Go to: **Deployments**
2. Click **"..."** on latest deployment
3. Click **"Redeploy"**
4. ⚠️ **Important**: Click **"Redeploy"** in the popup (not "Cancel")

### Step 3: Wait for Build

- Watch the status change from "Building" to "Ready"
- This usually takes 1-3 minutes
- You'll see a green checkmark when done

### Step 4: Hard Refresh Browser

- `Ctrl + Shift + R` (or `Cmd + Shift + R` on Mac)
- Or open in Incognito mode

### Step 5: Check Browser Console

Press `F12` and run:

```javascript
// Check if API URL is set
console.log('API URL:', import.meta.env.VITE_API_URL);

// Test backend directly
fetch('https://shoe-mere-livestock-mild.trycloudflare.com/v1/health')
  .then((r) => r.json())
  .then((data) => console.log('✅ Backend:', data))
  .catch((err) => console.error('❌ Error:', err));
```

**Expected output**:

```
API URL: https://shoe-mere-livestock-mild.trycloudflare.com
✅ Backend: {status: "ok", app: "FloodSight Backend API", ...}
```

---

## 🔧 Quick Fixes

### Fix 1: Add Debug Logging

Add this to your frontend code temporarily:

```javascript
// At the top of your main file
console.log('=== FloodSight Debug ===');
console.log('Environment:', import.meta.env.MODE);
console.log('API URL:', import.meta.env.VITE_API_URL);
console.log('All env vars:', import.meta.env);

// Test API connection
if (import.meta.env.VITE_API_URL) {
  fetch(`${import.meta.env.VITE_API_URL}/v1/health`)
    .then((r) => r.json())
    .then((data) => console.log('✅ Backend connected:', data))
    .catch((err) => console.error('❌ Backend error:', err));
} else {
  console.error('❌ VITE_API_URL not set!');
}
```

Commit and push this, then check browser console.

### Fix 2: Use vercel.json for API Proxy

If environment variables aren't working, you can proxy through Vercel:

Create `vercel.json` in your project root:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://shoe-mere-livestock-mild.trycloudflare.com/:path*"
    }
  ]
}
```

Then in your code:

```javascript
// Use relative path instead of env variable
const API_URL = '/api/v1';

fetch(`${API_URL}/stations`); // Goes to /api/v1/stations → proxied to Cloudflare
```

### Fix 3: Disable Preview Deployments

If preview deployments are confusing:

1. Go to: **Settings** → **Git**
2. Scroll to **"Ignored Build Step"**
3. Set to only build on `main` branch

---

## 📋 Checklist Before Asking for Help

- [ ] Environment variable added to **Production**
- [ ] Variable name matches code (`VITE_API_URL`)
- [ ] **Redeployed** (not just "Promoted")
- [ ] Build shows **"Ready"** status
- [ ] Tried **hard refresh** (Ctrl+Shift+R)
- [ ] Checked **browser console** for errors
- [ ] Verified backend is accessible (it is!)
- [ ] Using correct deployment URL

---

## 🆘 Still Not Working?

### What to Check:

1. **Deployment URL**: Make sure you're checking the right URL
   - Production: `your-project.vercel.app`
   - Or: Use the URL from the latest "Ready" deployment

2. **Build Logs**: Check for any errors
   - Go to deployment → "Build Logs" tab
   - Look for errors or warnings

3. **Runtime Logs**: Check for runtime errors
   - Go to deployment → "Functions" tab
   - Check for any errors

4. **Network Tab**: Check API calls
   - F12 → Network tab
   - Filter by "Fetch/XHR"
   - See if any API calls are being made
   - Check their URLs and status codes

---

## 💡 Pro Tips

1. **Always redeploy after changing environment variables**
2. **Use incognito mode** to avoid cache issues
3. **Check build logs** for the API URL during build
4. **Add debug logging** temporarily to see what's happening
5. **Use vercel.json proxy** as a reliable alternative

---

## 🎯 Your Correct Configuration

**Environment Variable**:

```
VITE_API_URL=https://shoe-mere-livestock-mild.trycloudflare.com
```

**Frontend Code**:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Use it
async function loadData() {
  const response = await fetch(`${API_URL}/v1/stations`);
  const data = await response.json();
  return data;
}
```

**Test URL**: https://shoe-mere-livestock-mild.trycloudflare.com/v1/health

---

Your backend is working perfectly! The issue is just getting Vercel to use the new URL. Follow the steps above and it should work! 🚀
