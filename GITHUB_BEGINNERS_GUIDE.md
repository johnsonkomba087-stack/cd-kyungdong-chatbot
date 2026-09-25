# 🚀 Push to GitHub - Complete Beginner Guide

**Don't worry! I'll walk you through EVERY step. Just copy-paste the commands!**

---

## STEP 1: Create GitHub Account (5 minutes)

### 1.1 Go to GitHub Sign Up
1. Open your browser
2. Go to: **https://github.com/join**
3. Enter an **email address**
4. Enter a **password** (make it strong)
5. Enter a **username** (this will be your GitHub username)
   - Example: `johnkomba087` or `kdu-chatbot-admin`
6. Choose NO for emails from GitHub
7. Click  "Create account"
8. **Verify your email** - GitHub will send you an email, click the link

**✅ GitHub account created!**

---

## STEP 2: Create a GitHub Repository

### 2.1 Create New Repository
1. After login, click the **+** icon (top right)
2. Click **"New repository"**
3. Fill in:
   - **Repository name:** `kdu-chatbot` (use this name)
   - **Description:** "Kyungdong University RAG Chatbot"
   - **Visibility:** Select **PUBLIC** (so Streamlit Cloud can see it)
   - Leave everything else as default
4. Click **"Create repository"**

**✅ GitHub repository created!**

---

## STEP 3: Push Code to GitHub

### 3.1 Open PowerShell

1. Press **Windows Key + R**
2. Type: `powershell`
3. Press **Enter**

A black window will open.

### 3.2 Go to Your App Folder

Copy and paste this command:
```powershell
cd "d:\KDU GLOBAL CHATBOT\app.py"
```

Press **Enter**

You should see:
```
PS D:\KDU GLOBAL CHATBOT\app.py>
```

### 3.3 Initialize Git (One-time setup)

Copy and paste this command:
```powershell
git config --global user.name "Your Name"
```

Replace `"Your Name"` with your actual name. Example:
```powershell
git config --global user.name "John Komba"
```

Press **Enter**

Then copy and paste:
```powershell
git config --global user.email "your.email@example.com"
```

Replace with your actual email. Example:
```powershell
git config --global user.email "john@example.com"
```

Press **Enter**

### 3.4 Initialize Your Local Repository

Copy and paste:
```powershell
git init
```

Press **Enter**

You should see:
```
Initialized empty Git repository in D:\KDU GLOBAL CHATBOT\app.py\.git
```

### 3.5 Add All Files

Copy and paste:
```powershell
git add .
```

Press **Enter**

(No output means it worked)

### 3.6 Create First Commit

Copy and paste:
```powershell
git commit -m "Initial commit: KDU chatbot with dual retrieval system"
```

Press **Enter**

You should see something like:
```
[main (root-commit) abc1234] Initial commit: KDU chatbot with dual retrieval system
 15 files changed, 2000 insertions(+)
 create mode 100644 app.py
 create mode 100644 requirements.txt
 ...
```

### 3.7 Connect to Your GitHub Repository

Now you need to link your local folder to GitHub.

Go back to GitHub in your browser. You should be on your new repository page.

**Look for this section on the page:**
```
…or push an existing repository from the command line
```

You'll see a command like:
```
git remote add origin https://github.com/YOUR_USERNAME/kdu-chatbot.git
git branch -M main
git push -u origin main
```

**Copy each line and paste in PowerShell:**

First, copy and paste this (replace with YOUR_USERNAME):
```powershell
git remote add origin https://github.com/YOUR_USERNAME/kdu-chatbot.git
```

For example, if your username is `johnkomba087`:
```powershell
git remote add origin https://github.com/johnkomba087/kdu-chatbot.git
```

Press **Enter**

Then copy and paste:
```powershell
git branch -M main
```

Press **Enter**

### 3.8 Push to GitHub

Copy and paste:
```powershell
git push -u origin main
```

Press **Enter**

**A browser window will pop up asking you to authorize with GitHub - click "Authorize git Credentials Manager" or sign in**

You should see:
```
Enumerating objects: 15, done.
Counting objects: 100% (15/15), done.
Delta compression using up to 8 threads
Compressing objects: 100% (12/12), done.
Writing objects: 100% (15/15), 2.5 MiB | 1.2 MiB/s, done.
Total 15 (delta 1), reused 0 (delta 0)
remote: Validating objects: 100% (15/15), done.
To https://github.com/YOUR_USERNAME/kdu-chatbot.git
 * [new branch]      main -> main
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

**✅ Your code is now on GitHub!**

---

## STEP 4: Verify Your Code on GitHub

1. Go to **https://github.com/YOUR_USERNAME/kdu-chatbot**
   - Replace `YOUR_USERNAME` with your actual username
2. You should see all your files:
   - ✅ app.py
   - ✅ requirements.txt
   - ✅ .streamlit folder
   - ✅ src folder
   - ✅ Data folder
   - etc.

**If you see all files → SUCCESS! 🎉**

---

## STEP 5: Deploy on Streamlit Cloud

Now that your code is on GitHub, deploying is easy!

### 5.1 Go to Streamlit Cloud
1. Open: **https://streamlit.io/cloud**
2. Click **"Start free"** or **"Sign in"** (if you already have account)
3. Click **"Authorize streamlit"** and authorize with GitHub
4. You'll see your GitHub repositories

### 5.2 Deploy Your App
1. Look for **`kdu-chatbot`** in your repos
2. Click on it
3. **Main file path:** Type `app.py` 
4. Click **"Deploy"**
5. **Wait 2-5 minutes** for deployment
6. You'll see a "Running" status when done

### 5.3 Add Your Groq API Key
1. On the Streamlit Cloud dashboard, find your app
2. Click **⚙️ Settings** (top right of app preview)
3. Click **"Secrets"** tab
4. Paste this:
```toml
GROQ_API_KEY = "your_actual_groq_api_key_here"
```

Replace with your actual Groq API key (you already have this)

5. Click **"Save"**

**✅ Your app is now live on the internet!**

Your URL will be:
```
https://YOUR_USERNAME-kdu-chatbot.streamlit.app
```

**Example:**
```
https://johnkomba087-kdu-chatbot.streamlit.app
```

---

## Complete Command List (Copy-Paste Ready)

If you want to just run all commands at once:

```powershell
# Go to app folder
cd "d:\KDU GLOBAL CHATBOT\app.py"

# Setup Git user (one time)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Initialize repository
git init

# Add all files
git add .

# Create commit
git commit -m "Initial commit: KDU chatbot"

# Add remote (REPLACE YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/kdu-chatbot.git

# Set branch
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## Troubleshooting

### "Command not found: git"
- Git is not installed
- Download from: https://git-scm.com/download/win
- Install it, then restart PowerShell

### "fatal: could not read Username"
- When you run `git push`, a browser window should open
- Click "Authorize" in the browser
- If it doesn't open automatically:
  - You may need to use a personal access token
  - Go to https://github.com/settings/tokens
  - Create new token with "repo" permission
  - Use that token as password

### "fatal: remote origin already exists"
- You already set up the remote
- That's OK! Just skip that step and run `git push -u origin main`

### "Authentication failed"
- Make sure you typed your GitHub username correctly in the remote URL
- Check your password
- Try: `git push -u origin main` again

### "Nothing happens after `git push`"
- It's uploading - be patient! (can take 30 seconds to 2 minutes)
- Don't close PowerShell
- Once done, you'll see the success message

---

## After Pushing: Making Updates

When you make changes to your code later:

```powershell
cd "d:\KDU GLOBAL CHATBOT\app.py"

git add .
git commit -m "Description of changes"
git push origin main
```

Streamlit Cloud will **automatically redeploy**! ✨

---

## You're All Set! 🎉

1. ✅ Pushed code to GitHub
2. ✅ Deployed on Streamlit Cloud
3. ✅ Added Groq API key
4. ✅ App is live on internet!

Now everyone can use your chatbot at:
```
https://YOUR_USERNAME-kdu-chatbot.streamlit.app
```

---

**Need help? Ask me any questions!** 💬
