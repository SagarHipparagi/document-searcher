# 🚀 Deploy to Render

Follow these steps to deploy your Document Search Engine to Render:

## 📋 Prerequisites

1. A [Render account](https://render.com) (sign up with GitHub)
2. Groq API Key ([Get one free](https://console.groq.com))

## 🔧 Deployment Steps

### 1. **Push Your Code to GitHub** ✅
You've already done this! Your code is at:
```
https://github.com/SagarHipparagi/document-searcher
```

### 2. **Go to Render Dashboard**
- Visit [https://dashboard.render.com](https://dashboard.render.com)
- Sign in with your GitHub account

### 3. **Create a New Web Service**
- Click **"New +"** button (top right)
- Select **"Web Service"**

### 4. **Connect Your Repository**
- Choose **"Build and deploy from a Git repository"**
- Click **"Connect account"** if not already connected
- Find and select: `SagarHipparagi/document-searcher`
- Click **"Connect"**

### 5. **Configure the Service**

Fill in the following settings:

**Basic Settings:**
- **Name**: `document-searcher` (or your preferred name)
- **Region**: Choose the closest to you
- **Branch**: `main`
- **Root Directory**: `Document-Search-Engine-main`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Instance Type:**
- Select **"Free"** (or upgrade if needed)

### 6. **Add Environment Variables**

Click **"Advanced"** → **"Add Environment Variable"**

Add this variable:
- **Key**: `GROQ_API_KEY`
- **Value**: `your_groq_api_key_here` (paste your actual API key)

### 7. **Deploy!**
- Click **"Create Web Service"**
- Render will start building and deploying
- Wait 5-10 minutes for the first deployment

### 8. **Access Your App**
Once deployed, your app will be live at:
```
https://document-searcher.onrender.com
```
(or the URL Render provides)

---

## ⚠️ Important Notes

### Free Tier Limitations
- The free tier server **spins down after 15 minutes of inactivity**
- First request after inactivity may take 30-60 seconds to wake up
- This is normal behavior for Render's free tier

### File Uploads
- Uploaded files are stored in **temporary storage**
- Files will be lost when the server restarts
- For persistent storage, consider upgrading to a paid plan

### Large Files
- The app loads embeddings models (~500MB)
- First deployment may take longer due to model downloads

---

## 🔄 Updating Your Deployment

After making code changes:

```bash
cd "C:\Users\sagar\Documents\AI\Projects\Document-Search-Engine-main (1)\Document-Search-Engine-main"
git add .
git commit -m "Update: description of changes"
git push origin main
```

Render will **automatically redeploy** when you push to GitHub!

---

## 🐛 Troubleshooting

### Build Fails
- Check the build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### App Crashes
- Check application logs in Render dashboard
- Verify `GROQ_API_KEY` is set correctly
- Check for any missing environment variables

### Slow Response
- Free tier servers spin down when idle
- First request after idle takes time to wake up
- Consider upgrading for always-on instances

---

## 📊 Monitor Your App

In Render Dashboard:
- **Logs**: View real-time application logs
- **Metrics**: See CPU, memory usage
- **Events**: Track deployments and errors

---

**🎉 Your app will be live on the internet!**

Share the URL with anyone to let them search your documents! 🚀
