# Vercel Deployment Fix Guide

## Problem
Vercel is deploying an old version of the application instead of the latest code.

## Root Causes Identified

1. **ESLint errors treated as CI failures** - Fixed in commit `622eb2f2`
2. **Build cache preventing fresh builds**
3. **CI=true causing warnings to fail builds**
4. **Vercel may be using cached dependencies**

## Complete Fix Checklist

### ✅ Step 1: Verify Git Status (DONE)

Latest commits confirmed pushed to GitHub:
```
622eb2f2 - fix: Resolve ESLint warnings causing Vercel build failure
6c5b9e13 - fix: Simplify Vercel config for frontend-only deployment
6287e496 - feat: Add auto-save, dynamic class support, and Vercel deployment config
```

Branch: `main`
Status: Up to date with `origin/main` ✅

### ✅ Step 2: Updated vercel.json Configuration

**Key Changes:**
- Set `CI=false` to prevent ESLint warnings from failing builds
- Use `npm ci` instead of `npm install` for clean dependency installation
- Added `GENERATE_SOURCEMAP=false` to reduce build size
- Specified `framework: "create-react-app"` for proper detection
- Disabled sourcemap generation for faster builds

**New vercel.json:**
```json
{
  "version": 2,
  "buildCommand": "cd annotation_tool/frontend && npm ci && npm run build",
  "outputDirectory": "annotation_tool/frontend/build",
  "installCommand": "cd annotation_tool/frontend && npm ci",
  "framework": "create-react-app",
  "env": {
    "CI": "false"
  },
  "build": {
    "env": {
      "CI": "false",
      "GENERATE_SOURCEMAP": "false"
    }
  }
}
```

### 🔧 Step 3: Clear Vercel Cache (DO THIS NOW)

#### Option A: Via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard:**
   - Visit: https://vercel.com/dashboard
   - Select your project: `train-yolo`

2. **Settings → General:**
   - Scroll to "Build & Development Settings"
   - Click **"Clear Cache"** button

3. **Trigger Redeploy:**
   - Go to **Deployments** tab
   - Click on the latest deployment
   - Click **"Redeploy"** button
   - Check **"Use existing Build Cache: NO"** ✅
   - Click **"Redeploy"**

#### Option B: Via Vercel CLI

```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Login
vercel login

# Link to your project
vercel link

# Redeploy with no cache
vercel --prod --force
```

### 🗑️ Step 4: Delete Local .vercel Folder (If Exists)

```bash
# Check if .vercel folder exists
ls -la .vercel 2>/dev/null && echo "Found .vercel folder" || echo "No .vercel folder"

# Delete it (forces fresh Vercel configuration)
rm -rf .vercel

# Commit the updated vercel.json
git add vercel.json
git commit -m "fix: Update vercel.json with cache-busting and CI=false settings"
git push origin main
```

### 📋 Step 5: Verify Deployment Settings in Vercel Dashboard

Go to: **Settings → General → Build & Development Settings**

**Verify these settings:**

| Setting | Value |
|---------|-------|
| Framework Preset | **Create React App** |
| Root Directory | `.` (or blank) |
| Build Command | `cd annotation_tool/frontend && npm ci && npm run build` |
| Output Directory | `annotation_tool/frontend/build` |
| Install Command | `cd annotation_tool/frontend && npm ci` |

**Environment Variables:**
- Add: `CI` = `false` (prevents ESLint warnings from failing)
- Add: `GENERATE_SOURCEMAP` = `false` (optional, faster builds)

### 🔍 Step 6: Monitor the New Deployment

1. **Go to Deployments tab** in Vercel
2. **Watch the build logs** in real-time
3. **Look for these success indicators:**
   ```
   ✓ Running "install" command...
   ✓ Installing dependencies...
   ✓ Running "build" command...
   ✓ Creating an optimized production build...
   ✓ Compiled successfully
   ✓ Build completed
   ```

4. **Verify the commit hash:**
   - Check deployment shows commit `622eb2f2` (latest)
   - Not an older commit

### ✅ Step 7: Test the Deployed App

Once deployed:

1. **Visit your Vercel URL** (e.g., `https://train-yolo.vercel.app`)
2. **Open browser console** (F12)
3. **Verify latest features are present:**
   - Auto-save functionality
   - Dynamic class support (classes beyond 0-3)
   - Label edit popup
   - All recent UI improvements

4. **Check for errors in console**
   - Should see: `Auto-saved label change for annotation X` (when editing)
   - No "unknown" labels for custom classes

### 🚨 Troubleshooting

#### If Build Still Fails:

**1. Check Build Logs for Errors:**
- Look for `Failed to compile` messages
- Check for missing dependencies
- Verify Node.js version compatibility

**2. Verify Branch:**
- Vercel Settings → Git
- Confirm Production Branch: `main`
- Confirm branch is not locked to old commit

**3. Check for .gitignore Issues:**
```bash
# Verify build folder is ignored (shouldn't be committed)
cat .gitignore | grep build
# Should show: build/ or annotation_tool/frontend/build
```

**4. Force Complete Rebuild:**
- Go to Vercel Settings
- **Danger Zone** → **Delete Project**
- Re-import from GitHub
- Reconfigure settings (use values from Step 5 above)

#### If Deployment Shows Old Code:

**1. Browser Cache:**
```
Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
Or open in Incognito/Private mode
```

**2. Verify Deployment Commit:**
```bash
# In Vercel dashboard, check deployment details
# Should show: "Deployed from commit: 622eb2f2"
```

**3. Check Vercel Region:**
```bash
# If accessing from different region, CDN cache may be stale
# Wait 5-10 minutes for CDN to update globally
```

### 📊 Success Indicators

✅ Build completes without errors
✅ Deployment shows latest commit hash (`622eb2f2`)
✅ App loads with all latest features
✅ Console shows auto-save logs
✅ Custom classes display correctly (not "unknown")
✅ No ESLint errors in build logs

## Quick Command Summary

```bash
# 1. Verify git status
git log --oneline -5
git status

# 2. Delete .vercel folder if exists
rm -rf .vercel

# 3. Commit updated vercel.json
git add vercel.json VERCEL_DEPLOYMENT_FIX.md
git commit -m "fix: Update vercel.json with cache-busting and CI=false settings"
git push origin main

# 4. Force redeploy via CLI (optional)
vercel --prod --force
```

## What Changed in vercel.json

| Setting | Old Value | New Value | Why |
|---------|-----------|-----------|-----|
| `installCommand` | `npm install` | `npm ci` | Clean install, no cache |
| `env.CI` | ❌ Not set | `"false"` | Prevent ESLint warnings from failing |
| `build.env.CI` | ❌ Not set | `"false"` | Same for build step |
| `build.env.GENERATE_SOURCEMAP` | ❌ Not set | `"false"` | Smaller build, faster deployment |
| `framework` | ❌ Not set | `"create-react-app"` | Proper framework detection |
| `version` | ❌ Not set | `2` | Use Vercel v2 platform |

## Next Steps After Successful Deployment

1. **Test all features** to ensure latest code is live
2. **Set up automatic deployments** (should be enabled by default)
3. **Configure custom domain** (optional) in Vercel Settings
4. **Deploy backend** separately (Railway/Render)
5. **Connect frontend to backend** via environment variables

---

**Need Help?**
- Check Vercel build logs for specific errors
- Review this guide step by step
- Ensure all git commits are pushed
- Try force redeploy with cache cleared
