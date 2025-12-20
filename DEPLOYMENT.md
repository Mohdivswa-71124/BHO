# 🚀 Deployment Guide for Resource Saver

## Part 1: Deploy Backend to Railway (Recommended - Free)

### Step 1: Create GitHub Repository
```bash
cd backend
git init
git add .
git commit -m "Initial backend commit"
```

Then create a new repo on GitHub and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/resource-saver-api.git
git push -u origin main
```

### Step 2: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `resource-saver-api` repository
5. Railway will auto-detect Python and deploy!

### Step 3: Add PostgreSQL (Optional but recommended for production)
1. In Railway dashboard, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will auto-configure the connection

### Step 4: Get Your Backend URL
After deployment, Railway gives you a URL like:
```
https://resource-saver-api-production.up.railway.app
```

---

## Part 2: Update Extension with Production URL

### Step 1: Edit `entrypoints/popup/config.ts`:
```typescript
// Comment out local, uncomment production:
// export const API_BASE_URL = 'http://localhost:8080';
export const API_BASE_URL = 'https://YOUR-RAILWAY-URL.railway.app';
```

### Step 2: Rebuild the extension:
```bash
npm run build
npm run zip
```

Your production-ready zip will be at:
```
.output/resource-saver-1.0.0-chrome.zip
```

---

## Part 3: Publish Extension

### Option A: Chrome Web Store (Public)

1. Go to [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole)
2. Pay one-time $5 developer fee
3. Click "New Item"
4. Upload `.output/resource-saver-1.0.0-chrome.zip`
5. Fill in:
   - Description
   - Screenshots (1280x800 or 640x400)
   - Icon (128x128)
   - Category: Productivity
6. Submit for review (1-3 days)

### Option B: Firefox Add-ons

```bash
npm run build:firefox
npm run zip:firefox
```

1. Go to [Firefox Add-on Developer Hub](https://addons.mozilla.org/developers/)
2. Click "Submit a New Add-on"
3. Upload `.output/resource-saver-1.0.0-firefox.zip`
4. Fill in details and submit

### Option C: Direct Install (Private/Testing)

Share the zip file directly:
1. User opens `chrome://extensions`
2. Enable "Developer mode"
3. Drag & drop the `.zip` file

---

## 📁 Files Ready for Deployment

### Backend (in `/backend/`):
- `main.py` - FastAPI server
- `requirements.txt` - Python dependencies
- `Procfile` - For Railway/Heroku
- `runtime.txt` - Python version

### Extension:
- `.output/resource-saver-1.0.0-chrome.zip` - Chrome extension (75 KB)

---

## 🔗 Quick Deploy Commands

### Railway CLI (if installed):
```bash
cd backend
railway login
railway init
railway up
```

### Render.com:
1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## ✅ Checklist Before Going Live

- [ ] Backend deployed and accessible
- [ ] Update `config.ts` with production URL
- [ ] Rebuild extension with `npm run zip`
- [ ] Test extension with production backend
- [ ] Create screenshots for store listing
- [ ] Write description for store
- [ ] Submit for review
