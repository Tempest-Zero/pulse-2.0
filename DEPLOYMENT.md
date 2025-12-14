# Pulse 2.0 Deployment Guide

Deploy Pulse 2.0 entirely on Railway (backend + frontend) and Chrome (extension).

---

## 🚀 Quick Start

### Prerequisites
- GitHub account with repository access
- Railway account (https://railway.app)
- Chrome browser (for extension)

---

## 📦 Railway Deployment (Backend + Frontend)

Railway supports monorepos - you can deploy both services from one repo!

### Step 1: Create New Project
1. Go to [railway.app](https://railway.app) → "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `pulse-2.0` repository

### Step 2: Add PostgreSQL Database
1. In your project, click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway automatically provides `DATABASE_URL`

### Step 3: Deploy Backend Service
1. Click **"+ New"** → **"GitHub Repo"** → Select same repo
2. Click on the new service → **Settings**
3. Set **Root Directory**: `backend`
4. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Go to **Variables** tab, add:
   ```
   CORS_ORIGINS=https://<your-frontend>.up.railway.app,chrome-extension://*
   ```
6. **Generate Domain**: Settings → Networking → Generate Domain
7. Note your backend URL: `https://your-backend.up.railway.app`

### Step 4: Deploy Frontend Service
1. Click **"+ New"** → **"GitHub Repo"** → Select same repo
2. Click on the new service → **Settings**
3. Set **Root Directory**: `frontend`
4. Set **Build Command**: `npm run build`
5. Set **Start Command**: `npm start`
6. Go to **Variables** tab, add:
   ```
   NEXT_PUBLIC_API_URL=https://<your-backend>.up.railway.app
   ```
7. **Generate Domain**: Settings → Networking → Generate Domain

### Step 5: Update Backend CORS
Go back to Backend service → Variables → Update:
```
CORS_ORIGINS=https://<your-frontend>.up.railway.app,chrome-extension://*
```

### Step 6: Verify Deployment
```bash
# Backend health check
curl https://your-backend.up.railway.app/health

# Frontend
open https://your-frontend.up.railway.app
```

---

## 🧩 Browser Extension Installation

### Load Extension Locally (Development)
1. Open Chrome → `chrome://extensions`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select folder: `pulse-extension/`
5. Extension icon appears in toolbar!

### Configure Extension Backend URL
1. Right-click extension icon → Options
2. Or edit `pulse-extension/lib/sync-scheduler.js`:
   ```javascript
   API_ENDPOINT: 'https://your-backend.railway.app/api/v1/extension'
   ```

### Chrome Web Store (Production)
1. Create icons in PNG format (16, 32, 48, 128px)
2. Zip the `pulse-extension/` folder
3. Go to [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole)
4. Upload ZIP and fill in store listing
5. Submit for review (~1-3 days)

---

## 🔧 Post-Deployment Checklist

### Backend
- [ ] Health endpoint returns 200 OK
- [ ] Database migrations ran successfully
- [ ] API docs accessible at `/docs`
- [ ] CORS allows frontend and extension origins

### Frontend
- [ ] App loads without errors
- [ ] API calls reach backend
- [ ] Authentication flow works

### Extension
- [ ] Loads without errors in Chrome
- [ ] Popup shows consent prompt
- [ ] Options page accessible
- [ ] Sync with backend works

---

## 📊 Monitoring (Railway Dashboard)

- **Logs**: Click on any service → View build & runtime logs
- **Metrics**: CPU, Memory, Network usage
- **Alerts**: Settings → Notifications → Configure alerts
- **Domains**: Manage custom domains in Networking tab

---

## 🔒 Security Checklist

- [ ] `DATABASE_URL` is not committed to git
- [ ] CORS origins are explicitly listed
- [ ] Extension uses HTTPS for API calls
- [ ] No API keys in frontend code

---

## 🐛 Troubleshooting

### "Module not found: torch"
DQN features require PyTorch. Install with:
```bash
pip install torch
```
Or ignore - core features work without it.

### CORS Errors
Add your frontend domain to `CORS_ORIGINS`:
```
CORS_ORIGINS=https://your-frontend.up.railway.app,chrome-extension://*
```

### Database Connection Failed
- Check `DATABASE_URL` format: `postgresql://user:pass@host:port/db`
- Railway auto-provides this for PostgreSQL addon
- Link PostgreSQL to backend: Click PostgreSQL → Connect → Add Reference

### Extension Not Loading
- Check `manifest.json` for syntax errors
- Ensure all referenced files exist
- Check browser console for errors (F12 → Console)

### Build Fails on Railway
- Check build logs for missing dependencies
- Ensure `requirements.txt` (backend) and `package.json` (frontend) are complete

---

## 📝 Environment Variables Reference

| Variable | Service | Description |
|----------|---------|-------------|
| `DATABASE_URL` | Backend | PostgreSQL connection (auto-set) |
| `CORS_ORIGINS` | Backend | Allowed origins for API |
| `SQL_ECHO` | Backend | Enable SQL query logging |
| `NEXT_PUBLIC_API_URL` | Frontend | Backend API base URL |
| `PORT` | Both | Auto-set by Railway |

---

## 🏗️ Railway Project Structure

```
┌─────────────────────────────────────────┐
│           Railway Project               │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐       │
│  │  PostgreSQL │  │   Backend   │       │
│  │  (Database) │←─│  (FastAPI)  │       │
│  └─────────────┘  └──────┬──────┘       │
│                          │              │
│                          ↓              │
│                   ┌─────────────┐       │
│                   │  Frontend   │       │
│                   │  (Next.js)  │       │
│                   └─────────────┘       │
│                          ↑              │
│                   ┌─────────────┐       │
│                   │  Extension  │       │
│                   │  (Chrome)   │       │
│                   └─────────────┘       │
└─────────────────────────────────────────┘
```

---

## Next Steps

1. ✅ **Deploy backend + frontend on Railway**
2. ✅ **Add PostgreSQL database**
3. ✅ **Load extension in Chrome**
4. 🧪 **Test full flow**: Extension → Backend → Frontend
5. 🚀 **Submit extension to Chrome Web Store**

🎉 **Congratulations! Your Pulse 2.0 is live!**

