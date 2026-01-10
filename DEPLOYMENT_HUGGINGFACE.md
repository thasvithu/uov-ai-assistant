# UOV AI Assistant - Hugging Face Deployment Guide

## 🤗 Deploy to Hugging Face Spaces (100% Free)

### Why Hugging Face?
- ✅ **FREE forever** (no credit card)
- ✅ **No memory limits** (perfect for ML models)
- ✅ **No cold starts**
- ✅ **Built for AI applications**

---

## Step-by-Step Deployment

### Part 1: Setup Hugging Face Account

1. Go to https://huggingface.co
2. Click **"Sign Up"** (free)
3. Verify your email

---

### Part 2: Deploy Backend

#### 1. Create Backend Space

1. Click **"New" → "Space"**
2. Fill in:
   - **Space name:** `uov-assistant-backend`
   - **License:** MIT
   - **Select SDK:** **Docker**
   - **Visibility:** Public
3. Click **"Create Space"**

#### 2. Upload Files

In your Space, click **"Files" → "Add file" → "Upload files"**

Upload these files from your project:
- `Dockerfile`
- `requirements.txt`
- Entire `backend_api/` folder
- Entire `shared/` folder
- `.env` file (rename to `.env.example` first, then edit in HF)

#### 3. Add Environment Variables

1. Go to **"Settings"** tab
2. Scroll to **"Repository secrets"**
3. Add each variable:

```
SUPABASE_URL
SUPABASE_KEY
QDRANT_URL
QDRANT_API_KEY
QDRANT_COLLECTION_NAME
GROQ_API_KEY
GROQ_MODEL
EMBEDDING_MODEL
EMBEDDING_DIMENSION
TOP_K_RETRIEVAL
SIMILARITY_THRESHOLD
LLM_TEMPERATURE
LLM_MAX_TOKENS
LOG_LEVEL
```

#### 4. Wait for Build

- Building: 5-10 minutes
- Once done, you'll get a URL like:
  `https://your-username-uov-assistant-backend.hf.space`

#### 5. Test Backend

Visit: `https://your-username-uov-assistant-backend.hf.space/health`

Should see:
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "supabase_connected": true
}
```

---

### Part 3: Deploy Frontend

#### 1. Update API URL

Edit `streamlit_ui/app.py` line ~25:

```python
API_BASE_URL = "https://your-username-uov-assistant-backend.hf.space"
```

Commit and push to `prod` branch.

#### 2. Create Frontend Space

1. Click **"New" → "Space"**
2. Fill in:
   - **Space name:** `uov-assistant`
   - **License:** MIT
   - **Select SDK:** **Streamlit**
   - **Visibility:** Public
3. Click **"Create Space"**

#### 3. Upload Files

Upload:
- `streamlit_ui/app.py` → rename to `app.py` (root level)
- `.streamlit/` folder
- `requirements.txt`

#### 4. Configure Streamlit

Create `README.md` in the Space:

```markdown
---
title: UOV AI Assistant
emoji: 🎓
colorFrom: purple
colorTo: pink
sdk: streamlit
sdk_version: 1.52.0
app_file: app.py
pinned: false
---
```

#### 5. Deploy!

Space will auto-deploy. URL:
`https://huggingface.co/spaces/your-username/uov-assistant`

---

## ✅ Deployment Complete!

Your app is now live on Hugging Face Spaces!

**Backend:** `https://your-username-uov-assistant-backend.hf.space`
**Frontend:** `https://huggingface.co/spaces/your-username/uov-assistant`

---

## Benefits

- 🆓 **100% Free**
- 🚀 **No memory limits**
- ⚡ **No cold starts**
- 🔄 **Auto-deploy from Git**
- 📊 **Usage analytics**

---

## Troubleshooting

**Build fails:**
- Check Dockerfile syntax
- Verify all files uploaded
- Check logs in Space

**Frontend can't connect:**
- Verify backend URL in `app.py`
- Check CORS settings
- Ensure backend is running

---

## Updates

To update your app:
1. Make changes locally
2. Upload new files to Space
3. Auto-rebuilds!

Or connect to Git for auto-deploy.
