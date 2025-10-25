# Railway Backend Deployment Guide

## Quick Deploy to Railway

Follow these steps to deploy the Flask backend to Railway and connect it to your Vercel frontend.

---

## Step 1: Deploy Backend to Railway

### A. Sign Up / Login to Railway

1. Go to: https://railway.app
2. Click **"Login with GitHub"**
3. Authorize Railway to access your GitHub account

### B. Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose repository: `shelly5353/train_yolo`
4. Railway will scan the repository

### C. Configure Backend Service

1. **Select Root Directory:**
   - Click on **"Settings"**
   - Under **"Service Settings"**
   - Set **Root Directory**: `annotation_tool/backend`
   - Click **"Update"**

2. **Environment Variables:**
   - Go to **"Variables"** tab
   - Add these variables:

   | Variable | Value |
   |----------|-------|
   | `PORT` | `5002` (or leave blank for Railway default) |
   | `FLASK_ENV` | `production` |
   | `PYTHONUNBUFFERED` | `1` |

3. **Deploy:**
   - Railway will automatically detect `requirements.txt`
   - It will install dependencies and start the app
   - Wait 2-3 minutes for deployment

### D. Get Your Backend URL

1. Go to **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. You'll get a URL like: `https://train-yolo-production.up.railway.app`
5. **Copy this URL** - you'll need it for Vercel!

---

## Step 2: Update Vercel Environment Variables

Now connect your Vercel frontend to the Railway backend:

### A. Go to Vercel Dashboard

1. Visit: https://vercel.com/dashboard
2. Click on your **"train-yolo"** project
3. Go to **Settings** tab

### B. Add Environment Variable

1. Click **"Environment Variables"**
2. Add new variable:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://your-railway-app.up.railway.app/api`
     - Replace with YOUR Railway domain
     - Make sure to add `/api` at the end
   - **Environment**: Select **ALL** (Production, Preview, Development)
3. Click **"Save"**

### C. Redeploy Frontend

1. Go to **"Deployments"** tab
2. Click on the latest deployment
3. Click **"Redeploy"** button
4. **IMPORTANT**: Check **"Use existing Build Cache: NO"** ✅
5. Click **"Redeploy"**
6. Wait 2-3 minutes for redeployment

---

## Step 3: Test the Full Stack

### A. Test Backend (Railway)

Open your Railway URL in browser:
```
https://your-railway-app.up.railway.app/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "classes_file": null,
  "data_dir": null,
  "images_dir": null,
  "labels_dir": null
}
```

✅ If you see this, backend is running!

### B. Test Frontend (Vercel)

1. Open: https://train-yolo.vercel.app
2. Open browser console (F12)
3. Should NOT see CORS or localhost errors
4. Try selecting a directory
5. Should connect to backend successfully

---

## Troubleshooting

### Issue: CORS Errors

If you see CORS errors in console:

**Solution**: Update backend CORS configuration

The backend already has CORS enabled for all origins:
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

If still having issues, check Railway logs:
1. Railway Dashboard → Your Project
2. Click **"Deployments"** tab
3. Click latest deployment
4. View **"Logs"** tab

### Issue: 404 Not Found

**Check:**
1. Backend URL is correct in Vercel environment variables
2. URL ends with `/api` (e.g., `https://xxx.railway.app/api`)
3. Backend is actually running (check Railway deployment status)

### Issue: Backend Not Starting

**Check Railway Logs for errors:**
1. Missing dependencies → Check `requirements.txt`
2. Port errors → Set `PORT` environment variable
3. Python version → Specified in `runtime.txt` (Python 3.11)

### Issue: "Load failed" in Frontend

This means backend is not accessible. Check:
1. Railway deployment status (should be green/running)
2. Railway domain is generated and active
3. Backend health endpoint returns 200 OK
4. Vercel environment variable is set correctly
5. Frontend was redeployed after adding environment variable

---

## Configuration Files Created

### Backend Files (already in repo):

**`annotation_tool/backend/Procfile`:**
```
web: python app.py
```

**`annotation_tool/backend/runtime.txt`:**
```
python-3.11.0
```

**`annotation_tool/backend/railway.json`:**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**`annotation_tool/backend/requirements.txt`:**
```
Flask>=2.0.0
Flask-CORS>=4.0.0
Pillow>=9.0.0
opencv-python>=4.5.0
numpy>=1.21.0
PyMuPDF>=1.23.0
```

### Frontend Files (already updated):

**`annotation_tool/frontend/src/services/api.ts`:**
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5002/api';
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────┐
│                   USER                       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Vercel (Frontend)  │
         │  React Static Site  │
         │  train-yolo.app     │
         └──────────┬──────────┘
                    │
                    │ HTTPS API Calls
                    │ REACT_APP_API_URL
                    ▼
         ┌─────────────────────┐
         │ Railway (Backend)   │
         │  Flask API Server   │
         │  .railway.app       │
         └─────────────────────┘
```

---

## Environment Variables Summary

### Vercel (Frontend):
| Variable | Value | Purpose |
|----------|-------|---------|
| `REACT_APP_API_URL` | `https://xxx.railway.app/api` | Backend API endpoint |
| `CI` | `false` | Prevent ESLint warnings from failing builds |
| `GENERATE_SOURCEMAP` | `false` | Faster builds |

### Railway (Backend):
| Variable | Value | Purpose |
|----------|-------|---------|
| `PORT` | `5002` or auto | Server port |
| `FLASK_ENV` | `production` | Disable debug mode |
| `PYTHONUNBUFFERED` | `1` | Show logs in real-time |

---

## Success Checklist

- ✅ Railway deployment status: **Running** (green)
- ✅ Railway domain generated and accessible
- ✅ Backend health endpoint returns 200 OK
- ✅ Vercel environment variable `REACT_APP_API_URL` is set
- ✅ Vercel redeployed after adding environment variable
- ✅ Frontend loads without console errors
- ✅ Can select directory and see images
- ✅ Can create/edit/delete annotations
- ✅ Auto-save works (check console logs)

---

## Cost

### Railway:
- **Free Tier**: $5 credit per month
- **Hobby Plan**: $5/month (better limits)
- Your backend should fit in free tier for development

### Vercel:
- **Free Tier**: Unlimited for personal projects
- Your frontend deployment is FREE ✅

**Total Cost for Full Stack:** $0 - $5/month

---

## Alternative: Run Backend Locally

If you prefer not to deploy backend:

1. **Start backend locally:**
   ```bash
   cd annotation_tool/backend
   python app.py
   ```

2. **Use ngrok for public URL:**
   ```bash
   ngrok http 5002
   ```

3. **Update Vercel environment variable:**
   - `REACT_APP_API_URL` = ngrok URL + `/api`
   - Example: `https://abc123.ngrok.io/api`

4. **Redeploy Vercel**

**Note:** ngrok URLs change on restart, Railway is more stable for production.

---

## Next Steps

After successful deployment:

1. **Test all features** on live site
2. **Share the link** with team/portfolio
3. **Monitor Railway logs** for any errors
4. **Set up custom domain** (optional) in Vercel
5. **Add authentication** if needed (future enhancement)

---

## Support

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **This Guide**: RAILWAY_DEPLOYMENT_GUIDE.md
- **Deployment Fix**: VERCEL_DEPLOYMENT_FIX.md

---

**Need Help?**
Check Railway deployment logs for specific errors or review Vercel build logs if frontend redeploy fails.
