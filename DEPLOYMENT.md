# Deployment Guide - YOLO Annotation Tool

## Vercel Deployment

This project is configured for deployment on Vercel with both frontend (React) and backend (Flask) components.

### Prerequisites

1. GitHub account with this repository
2. Vercel account (free tier works)
3. Vercel CLI installed (optional): `npm i -g vercel`

### Deployment Steps

#### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Connect Repository**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import this GitHub repository
   - Vercel will auto-detect the configuration from `vercel.json`

2. **Configure Project**
   - Framework Preset: **Other**
   - Root Directory: **/** (leave as root)
   - Build Command: (auto-detected from `vercel.json`)
   - Output Directory: `annotation_tool/frontend/build`

3. **Environment Variables** (if needed)
   - Add any required environment variables in Vercel dashboard
   - Example: `FLASK_ENV=production`

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy both frontend and backend
   - You'll get a live URL like: `https://your-project.vercel.app`

#### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Project Structure

```
train_yolo/
├── vercel.json              # Vercel configuration
├── .vercelignore           # Files to exclude from deployment
├── annotation_tool/
│   ├── frontend/           # React app
│   │   ├── package.json    # Frontend dependencies
│   │   ├── src/            # React source code
│   │   └── build/          # Production build (generated)
│   └── backend/            # Flask API
│       ├── app.py          # Main Flask application
│       └── requirements.txt # Python dependencies
```

### Configuration Files

#### `vercel.json`
- Defines build settings for both frontend and backend
- Routes API calls to `/api/*` to Flask backend
- Serves frontend static files

#### `.vercelignore`
- Excludes large files (model weights, data directories)
- Excludes development files (venv, node_modules)
- Keeps deployment size minimal

### Important Notes

⚠️ **Large Files Excluded**
- Model weights (`best.pt`) are NOT deployed (too large for Vercel)
- Training data directories are excluded
- PDF cache is not deployed

⚠️ **Backend Limitations on Vercel**
- Serverless functions have 50MB limit (including dependencies)
- Execution timeout: 10 seconds (Hobby), 60 seconds (Pro)
- No persistent file storage (use external storage for images/labels)

### Recommended Setup for Production

For production use with large datasets and model inference:

1. **Frontend**: Deploy on Vercel (fast, free)
2. **Backend**: Deploy on a server with:
   - Persistent storage for images/labels
   - GPU support for YOLO inference
   - Options: DigitalOcean, AWS EC2, Google Cloud Run

### Alternative: Full Stack Deployment

Deploy the entire stack on a single platform:

- **Railway**: `railway up` (supports both Python and Node.js)
- **Render**: Create Web Service with Docker
- **DigitalOcean App Platform**: Push to deploy
- **Heroku**: `git push heroku main`

### Environment-Specific Configuration

#### Development
```bash
cd annotation_tool
./start.sh  # Starts both frontend and backend locally
```

#### Production (Vercel)
- Frontend: Served as static files from `/annotation_tool/frontend/build`
- Backend: Runs as serverless function at `/api/*`

### Troubleshooting

**Build Fails**
- Check `vercel.json` configuration
- Verify `package.json` has correct build script
- Check build logs in Vercel dashboard

**Backend Errors**
- Verify `requirements.txt` has all dependencies
- Check Python version compatibility (Vercel uses Python 3.9)
- Review function logs in Vercel dashboard

**Frontend Not Loading**
- Ensure build completed successfully
- Check browser console for errors
- Verify API endpoint URLs match production

### Post-Deployment

After deployment, you can:
- View live site at your Vercel URL
- Monitor function logs in Vercel dashboard
- Set up custom domain (Vercel > Settings > Domains)
- Enable automatic deployments from GitHub (default)

### Continuous Deployment

Vercel automatically deploys when you push to GitHub:
- Push to `main` → Production deployment
- Push to other branches → Preview deployment
- Pull requests → Preview deployment with unique URL

---

**Need Help?**
- Vercel Docs: https://vercel.com/docs
- This Project README: [README.md](README.md)
- Flask Deployment: https://flask.palletsprojects.com/en/2.3.x/deploying/
