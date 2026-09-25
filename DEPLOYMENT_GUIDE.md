# 🚀 Deployment Guide - GitHub + Streamlit Cloud

## Overview
This guide will help you deploy the Kyungdong University RAG Chatbot to the public internet using GitHub and Streamlit Cloud.

## Prerequisites
- GitHub account (free at https://github.com)
- Git installed on your computer
- Groq API key (you already have this)
- Streamlit Community Cloud account (free at https://streamlit.io)

---

## Step 1: Setup GitHub Repository

### 1.1 Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `kdu-chatbot` (or any name you prefer)
3. Description: "Kyungdong University RAG Chatbot"
4. **Public** (so Streamlit Cloud can access it)
5. Click **Create repository**

### 1.2 Initialize Local Git & Push Code

Open PowerShell in `d:\KDU GLOBAL CHATBOT\app.py` and run:

```powershell
# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: KDU chatbot with dual retrieval system"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/kdu-chatbot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example:**
```powershell
git remote add origin https://github.com/johnkomba087/kdu-chatbot.git
```

---

## Step 2: Prepare for Streamlit Cloud

### 2.1 Update Requirements File
Your `requirements.txt` should be in root or in the app directory:

**File:** `requirements.txt`
```
streamlit==1.28.1
groq==0.9.0
sentence-transformers==2.2.2
chromadb==0.4.24
python-dotenv==1.0.0
```

✅ **You already have this!**

### 2.2 Create `streamlit_app.py` in repository root

Streamlit Cloud looks for either:
- `streamlit_app.py` (preferred)
- `app.py` (in root)

Since your app is in a subfolder, create a wrapper:

**File:** `streamlit_app.py` (at root level, not in subdirectory)
```python
import subprocess
import sys
import os

# Change to app directory
os.chdir(os.path.join(os.path.dirname(__file__), 'app.py'))

# Run the actual app
subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
```

OR better: **Restructure the repository:**

```
kdu-chatbot/
├── app.py                          (moved from app.py/app.py)
├── requirements.txt
├── .streamlit/
│   ├── config.toml
│   ├── secrets.toml (DO NOT PUSH)
│   └── secrets.toml.example
├── src/
│   ├── __init__.py
│   ├── chatbot_rag.py
│   └── knowledge_base.py
├── Data/
│   ├── admission.txt
│   ├── programs.txt
│   ├── etc...
└── README.md
```

### 2.3 Verify .gitignore includes secrets
Your `.gitignore` should contain:
```
.streamlit/secrets.toml
chroma_db/
__pycache__/
```

✅ **This is already done!**

---

## Step 3: Deploy on Streamlit Cloud

### 3.1 Sign Up for Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Click **"Start free"**
3. Sign in with GitHub account
4. Click **Authorize streamlit**

### 3.2 Deploy Your App
1. After login on Streamlit Cloud dashboard, click **"New app"**
2. **Repository:** Select `kdu-chatbot`
3. **Branch:** `main`
4. **Main file path:** `app.py` (or `streamlit_app.py` if you created the wrapper)
5. Click **"Deploy!"**

Streamlit Cloud will:
- ✅ Clone your repo
- ✅ Install dependencies from requirements.txt
- ✅ Start your app

---

## Step 4: Add Secrets on Streamlit Cloud

### 4.1 Configure Groq API Key
1. Go to your app on Streamlit Cloud dashboard
2. Click **⚙️ Settings** (top right)
3. Click **"Secrets"** tab
4. Paste this in the secret editor:

```toml
GROQ_API_KEY = "your_actual_groq_api_key_here"
```

5. Click **"Save"**

⚠️ **NEVER commit secrets to GitHub!**

### 4.2 How App Gets Secrets
Your code uses:
```python
import streamlit as st
groq_api_key = st.secrets["GROQ_API_KEY"]
```

Streamlit Cloud automatically provides these from the Secrets panel.

---

## Step 5: Update Code for Deployment

### 5.1 Fix Path References
In `app.py` and `chatbot_rag.py`, make paths relative:

**Current (may not work):**
```python
from src.chatbot_rag import KyungdongRAGChatbot
from src.knowledge_base import load_knowledge_base
chroma_path = "./chroma_db"
```

**Better for deployment:**
```python
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.chatbot_rag import KyungdongRAGChatbot
from src.knowledge_base import load_knowledge_base
chroma_path = os.path.join(os.path.dirname(__file__), "chroma_db")
```

### 5.2 Handle Missing API Key Gracefully
```python
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("⚠️ Groq API key not found. Please add it to Streamlit Cloud secrets.")
    st.stop()
```

---

## Step 6: Monitor Deployment

### 6.1 View Deployment Status
- Streamlit Cloud dashboard shows **"Deployed"** when ready
- App URL will be: `https://[username]-kdu-chatbot.streamlit.app`

### 6.2 View Logs
- Click your app on dashboard
- Click **"Manage app"** → **"View logs"**
- Check for any errors (usually missing dependencies or secrets)

### 6.3 Common Deployment Issues

**❌ Module not found: `src.chatbot_rag`**
- Solution: Add to top of app.py:
```python
sys.path.insert(0, os.path.dirname(__file__))
```

**❌ KeyError: `GROQ_API_KEY` not found**
- Solution: Add key in Streamlit Cloud **Secrets** panel

**❌ Timeout during startup**
- Solution: Embedding model takes time to download
  - Add this to `.streamlit/config.toml`:
  ```toml
  [client]
  showErrorDetails = false
  
  [server]
  maxUploadSize = 200
  runOnSave = false
  ```

---

## Step 7: Make Future Updates

After deployment, to update your chatbot:

```powershell
# Make changes locally
# Test on http://localhost:8501

# Commit changes
git add .
git commit -m "Update: [describe changes]"

# Push to GitHub
git push origin main
```

Streamlit Cloud automatically redeploys when you push to GitHub! ✨

---

## Deployment Checklist

- [ ] GitHub account created
- [ ] Git initialized locally
- [ ] Repository pushed to GitHub
- [ ] `.gitignore` includes `secrets.toml` and `chroma_db/`
- [ ] `requirements.txt` in root directory
- [ ] Streamlit Cloud account created
- [ ] App deployed on Streamlit Cloud
- [ ] Groq API key added in Streamlit Cloud Secrets
- [ ] App accessible at public URL
- [ ] Test app with sample query

---

## Your Deployment URL Pattern
```
https://[your-username]-kdu-chatbot.streamlit.app
```

**Example:**
```
https://johnkomba087-kdu-chatbot.streamlit.app
```

---

## Support & Troubleshooting

**Deployment fails?**
1. Check Streamlit Cloud logs
2. Verify `requirements.txt` exists
3. Ensure `.gitignore` doesn't exclude important files
4. Check Groq API key is valid

**App running slow?**
1. First load downloads embedding model (takes 30-60 seconds)
2. Subsequent loads are faster
3. Chroma DB builds on first use

**Need help?**
- Streamlit docs: https://docs.streamlit.io
- Streamlit Cloud docs: https://docs.streamlit.io/streamlit-cloud
- Groq API docs: https://console.groq.com/docs

---

## Success! 🎉

Your chatbot is now live on the internet and accessible worldwide!

Share your app URL: `https://[username]-kdu-chatbot.streamlit.app`

Users can now:
- ✅ Ask questions about Kyungdong University
- ✅ Get instant AI-powered responses
- ✅ See source documents
- ✅ Have conversations stored in session

