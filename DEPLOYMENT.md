# UOV AI Assistant - Free Deployment Guide (Render + Streamlit Cloud)

## 🎯 What You'll Deploy

- **Backend (FastAPI)** → Render.com (Free)
- **Frontend (Streamlit)** → Streamlit Cloud (Free)
- **Total Cost:** $0/month

---

## ⏱️ Time Required: 30-45 minutes

---

## 📋 Prerequisites

Before starting, make sure you have:

- [x] GitHub account
- [x] All code pushed to GitHub repository
- [x] Supabase project created (with URL and API key)
- [x] Qdrant Cloud cluster created (with URL and API key)
- [x] Groq API key

---

## 🚀 Step-by-Step Deployment

### **PART 1: Prepare Your Code (5 minutes)**

#### Step 1: Update CORS Settings

Open `backend_api/main.py` and find the CORS middleware section (around line 74):

**Change from:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Development only
    ...
)
```

**Change to:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.streamlit.app",  # Streamlit Cloud
        "http://localhost:8501"      # Local testing
    ],
    ...
)
```

#### Step 2: Create `.gitignore` (if not exists)

Create/update `.gitignore` in your project root:

```
.env
.venv/
venv/
__pycache__/
*.pyc
.DS_Store
data/processed_files.json
*.log
```

#### Step 3: Commit and Push

```bash
git add .
git commit -m "feat: prepare for production deployment"
git push origin main
```

---

### **PART 2: Deploy Backend to Render (15 minutes)**

#### Step 1: Sign Up for Render

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with **GitHub** (easiest)
4. Authorize Render to access your repositories

#### Step 2: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository:
   - Click **"Connect account"** if needed
   - Find your `uov-ai-assistant` repo
   - Click **"Connect"**

#### Step 3: Configure Service

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `uov-ai-assistant-backend` |
| **Region** | Choose closest to Sri Lanka (Singapore) |
| **Branch** | `main` |
| **Root Directory** | Leave empty |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend_api.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | **Free** |

#### Step 4: Add Environment Variables

Scroll down to **"Environment Variables"** section and add these one by one:

Click **"Add Environment Variable"** for each:

```
SUPABASE_URL = https://your-project.supabase.co
SUPABASE_KEY = your-supabase-anon-key

QDRANT_URL = https://your-cluster.qdrant.io:6333
QDRANT_API_KEY = your-qdrant-api-key
QDRANT_COLLECTION_NAME = uov_documents_v1

GROQ_API_KEY = your-groq-api-key
GROQ_MODEL = llama-3.1-8b-instant

EMBEDDING_MODEL = intfloat/multilingual-e5-base
EMBEDDING_DIMENSION = 768

TOP_K_RETRIEVAL = 10
SIMILARITY_THRESHOLD = 0.5

LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 1024

BACKEND_HOST = 0.0.0.0
BACKEND_PORT = 8000
LOG_LEVEL = INFO
```

#### Step 5: Deploy!

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Watch the logs - you should see:
   ```
   Starting UOV AI Assistant API...
   All services initialized successfully
   Application startup complete
   ```

#### Step 6: Get Your Backend URL

Once deployed, you'll see a URL like:
```
https://uov-ai-assistant-backend.onrender.com
```

**📝 Copy this URL - you'll need it for the frontend!**

#### Step 7: Test Backend

Open in browser:
```
https://uov-ai-assistant-backend.onrender.com/health
```

You should see:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "qdrant_connected": true,
  "supabase_connected": true
}
```

✅ **Backend deployed successfully!**

---

### **PART 3: Deploy Frontend to Streamlit Cloud (10 minutes)**

#### Step 1: Update API URL in Code

Open `streamlit_ui/app.py` and find line ~25:

**Change from:**
```python
API_BASE_URL = "http://localhost:8000"
```

**Change to:**
```python
API_BASE_URL = "https://uov-ai-assistant-backend.onrender.com"  # Your Render URL
```

#### Step 2: Commit and Push

```bash
git add streamlit_ui/app.py
git commit -m "feat: update API URL for production"
git push origin main
```

#### Step 3: Sign Up for Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click **"Sign up"**
3. Sign in with **GitHub**
4. Authorize Streamlit

#### Step 4: Deploy App

1. Click **"New app"**
2. Fill in:
   - **Repository:** `your-username/uov-ai-assistant`
   - **Branch:** `main`
   - **Main file path:** `streamlit_ui/app.py`
3. Click **"Deploy!"**

#### Step 5: Wait for Deployment

- Initial deployment: 2-3 minutes
- You'll see logs showing:
  ```
  Installing dependencies...
  Starting Streamlit...
  App is live!
  ```

#### Step 6: Get Your App URL

You'll get a URL like:
```
https://uov-ai-assistant.streamlit.app
```

✅ **Frontend deployed successfully!**

---

### **PART 4: Final Testing (5 minutes)**

#### Test the Complete System

1. Open your Streamlit app URL
2. Try these tests:

**Test 1: Identity Question**
- Ask: "who are you"
- Should respond instantly with introduction

**Test 2: Knowledge Base Question**
- Ask: "What is the vision of the faculty?"
- Should retrieve and answer correctly

**Test 3: Feedback**
- Click 👍 or 👎 on a response
- Should save to Supabase

**Test 4: Session History**
- Refresh the page
- Previous messages should load

---

## 🎉 Deployment Complete!

Your UOV AI Assistant is now live at:
- **Frontend:** `https://uov-ai-assistant.streamlit.app`
- **Backend:** `https://uov-ai-assistant-backend.onrender.com`

---

## ⚠️ Important Notes

### Cold Starts (Render Free Tier)

**What happens:**
- After 15 minutes of inactivity, Render spins down your backend
- First request after sleep: 30-60 second delay
- Subsequent requests: Normal speed

**Solution (Optional):**
Use a free uptime monitor to ping every 14 minutes:
1. Sign up at https://uptimerobot.com (free)
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://uov-ai-assistant-backend.onrender.com/health`
   - Interval: 14 minutes

### Rate Limits

**Groq Free Tier:**
- 100,000 tokens/day
- Your cache helps reduce usage!

**If you hit limits:**
- Wait for daily reset
- Or upgrade Groq plan ($)

---

## 🔧 Troubleshooting

### Backend Issues

**"Application failed to start"**
- Check Render logs for errors
- Verify all environment variables are set
- Check Python version (should be 3.11+)

**"Qdrant/Supabase connection failed"**
- Verify URLs and API keys
- Check if services are accessible

### Frontend Issues

**"API is not available"**
- Check if backend is running (visit `/health`)
- Verify `API_BASE_URL` in `streamlit_ui/app.py`
- Check CORS settings in backend

**"Slow responses"**
- First request after sleep: Normal (cold start)
- Consider uptime monitor to prevent sleep

---

## 📊 Monitoring

### View Logs

**Backend (Render):**
1. Go to Render dashboard
2. Click your service
3. Click "Logs" tab

**Frontend (Streamlit):**
1. Go to Streamlit Cloud dashboard
2. Click your app
3. Click "Logs"

---

## 🔄 Updates

### To Update Your App

```bash
# Make changes to code
git add .
git commit -m "your changes"
git push origin main
```

**Both Render and Streamlit will auto-deploy!**

---

## 🎓 Next Steps

1. Share the URL with your faculty
2. Monitor usage and feedback
3. Add more documents to knowledge base
4. Consider custom domain (optional)

---

## 📞 Support

If you encounter issues:
1. Check logs first
2. Review troubleshooting section
3. Verify all environment variables

**Your app is live! 🚀**
