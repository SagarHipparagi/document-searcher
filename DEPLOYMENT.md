# Deployment Guide for Document Search Engine

This guide helps you deploy your Document Search Engine to the cloud.

## Quick Deploy to Render (Recommended)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/document-search-engine.git
git push -u origin main
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository

### Step 3: Configure Service
Render will auto-detect Python and use `render.yaml`. Just add:

**Environment Variables:**
1. In Render dashboard, go to "Environment"
2. Add: `GROQ_API_KEY` = `your_groq_api_key_here`
3. Save (will auto-deploy)

### Step 4: Test
- Your app will be at: `https://your-app-name.onrender.com`
- Try uploading a PDF and querying it

---

## Deploy to Heroku

### Step 1: Install Heroku CLI
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
heroku --version
```

### Step 2: Create App
```bash
heroku login
heroku create your-app-name
```

### Step 3: Set Environment Variables
```bash
heroku config:set GROQ_API_KEY="your_groq_api_key_here"
heroku config:set TF_ENABLE_ONEDNN_OPTS="0"
```

### Step 4: Deploy
```bash
git push heroku main
heroku open
```

---

## Important Notes

### ⚠️ File Upload Persistence
- **Render/Heroku use ephemeral filesystems** - uploaded files are deleted on restart
- For production, consider:
  - **Render Disks** (paid): Persistent storage
  - **AWS S3**: Cloud storage (best for production)
  - **Accept temporary storage**: OK for demos/testing

### 📦 File Size Limits
- **Render**: 100MB request body (OK for most documents)
- **Heroku**: 30MB limit (may need workaround for large PDFs)

### 🔐 Environment Variables Required
```
GROQ_API_KEY=your_key_here  # Get from https://console.groq.com/keys
TF_ENABLE_ONEDNN_OPTS=0     # Suppress TensorFlow warnings
```

### 🐛 Common Issues

**Upload fails with JSON error:**
→ Missing `GROQ_API_KEY` environment variable

**Files disappear after restart:**
→ Expected behavior on free tier (ephemeral filesystem)

**Large PDF upload fails:**
→ File exceeds platform limits (compress PDF or upgrade plan)

---

## Testing Deployment

### 1. Check Status Endpoint
```bash
curl https://your-app.onrender.com/api/status
# Should return: {"initialized": false, ...}
```

### 2. Upload Test File
- Upload a small PDF (<5MB)
- Check deployment logs for errors
- Try querying the document

### 3. Monitor Logs
**Render:**
- Dashboard → Your Service → Logs

**Heroku:**
```bash
heroku logs --tail
```

---

## Getting Your API Key

1. Go to https://console.groq.com/keys
2. Sign up (free tier available)
3. Create new API key
4. Copy and add to deployment environment variables

---

## Local Development

For local testing:
```bash
# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

# Run locally
python app.py

# Visit http://localhost:5000
```

---

## Next Steps

After successful deployment:
1. ✅ Test file upload with small PDF
2. ✅ Test query functionality
3. ✅ Monitor logs for errors
4. 🚀 Consider adding persistent storage for production use

For production deployment with persistent storage, see `deployment_fixes.md` for advanced configuration.
