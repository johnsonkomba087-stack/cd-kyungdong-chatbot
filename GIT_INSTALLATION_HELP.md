# Manual Git Installation

**Git is not automatically installing. Here are your options:**

---

## Option A: Manual Download & Install (5 minutes)

### Step 1: Download Git
1. Open your browser
2. Go to: **https://git-scm.com/download/win**
3. The download should start automatically
4. Wait for `Git-2.xx.0-64-bit.exe` to download

### Step 2: Install Git
1. Find the downloaded file in your Downloads folder
2. Double-click `Git-2.xx.0-64-bit.exe`
3. Click "Next" through all the screens
4. Accept the default options
5. Click "Install"
6. Click "Finish"

### Step 3: Restart PowerShell
1. Close your PowerShell window
2. Press Windows Key + R
3. Type: `powershell`
4. Press Enter

### Step 4: Verify Git is Installed
Paste this in PowerShell:
```powershell
git --version
```

You should see: `git version 2.xx.0.windows.1` or similar

**Then proceed to "GitHub Push Steps" below**

---

## Option B: Use Web Browser (Alternative Method)

If Git installation is giving you trouble, use GitHub's web interface:

### Step 1: Create GitHub Account
1. Go to: https://github.com/join
2. Sign up with email, password, username
3. Verify your email

### Step 2: Create Repository
1. Go to: https://github.com/new
2. Repository name: `kdu-chatbot`
3. Select **PUBLIC**
4. Click "Create repository"

### Step 3: Upload Files via Web (Drag & Drop)
1. On your new repository page
2. Click "Add file" → "Upload files"
3. Drag and drop files from your folder:
   - `d:\KDU GLOBAL CHATBOT\app.py\app.py`
   - `d:\KDU GLOBAL CHATBOT\app.py\requirements.txt`
   - `d:\KDU GLOBAL CHATBOT\app.py\.streamlit` folder
   - `d:\KDU GLOBAL CHATBOT\app.py\src` folder
   - `d:\KDU GLOBAL CHATBOT\app.py\Data` folder
4. Click "Commit changes"

**Your code is now on GitHub!**

### Step 4: Deploy on Streamlit Cloud
1. Go to: https://streamlit.io/cloud
2. Click "New app"
3. Select `kdu-chatbot` repo
4. Main file: `app.py`
5. Click "Deploy"
6. Add Groq API key in Secrets

**✅ Done!**

---

## GitHub Push Steps (After Git is Installed)

Once Git is installed, go back to your app folder and run:

```powershell
cd "d:\KDU GLOBAL CHATBOT\app.py"

# First time setup
git config --global user.name "Your Name"
git config --global user.email "your.email@gmail.com"

# Initialize repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: KDU chatbot"

# Add remote (REPLACE YOUR_USERNAME with your GitHub username!)
git remote add origin https://github.com/YOUR_USERNAME/kdu-chatbot.git
git branch -M main

# Push to GitHub (a browser will pop up to authenticate)
git push -u origin main
```

---

## Which Option Should You Use?

**Choose Option A (Manual Install) if:**
- You prefer command-line tools
- You plan to make code updates frequently
- You want to learn Git

**Choose Option B (Web Upload) if:**
- You want quickest deployment (no installation)
- You don't plan to update code often
- You're not comfortable with command line

---

**Try Option A first. If it gives errors, use Option B instead!**
