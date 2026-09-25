# ============================================================
# Kyungdong University RAG Chatbot - COMPLETE RUN SCRIPT
# ============================================================

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🎓 Kyungdong University RAG Chatbot - SETUP & RUN    ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

# ============================================================
# STEP 1: Fix Directory Structure
# ============================================================

Write-Host "📁 Step 1: Fixing project directory structure..." -ForegroundColor Yellow

# Current location
$currentPath = Get-Location
Write-Host "   Current path: $currentPath" -ForegroundColor Gray

# Check if we're in the wrong directory
if ($currentPath -like "*\app.py\*" -or $currentPath -like "*\app.py") {
    Write-Host "   ⚠️  You're in the wrong directory (app.py folder)" -ForegroundColor Red
    $parentPath = (Get-Item $currentPath).Parent.FullName
    Write-Host "   📍 Moving to parent directory: $parentPath" -ForegroundColor Yellow
    cd $parentPath
}

Write-Host "   ✅ Directory fixed" -ForegroundColor Green
Write-Host "`n"

# ============================================================
# STEP 2: Verify Python & Create Virtual Environment
# ============================================================

Write-Host "🐍 Step 2: Verifying Python installation..." -ForegroundColor Yellow

$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python not found! Install from https://www.python.org" -ForegroundColor Red
    exit 1
}

# Remove old venv if exists
if (Test-Path venv) {
    Write-Host "   🗑️  Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

Write-Host "   📦 Creating new virtual environment..." -ForegroundColor Yellow
python -m venv venv

if (Test-Path venv) {
    Write-Host "   ✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "`n"

# ============================================================
# STEP 3: Fix PowerShell Execution Policy
# ============================================================

Write-Host "🔐 Step 3: Configuring PowerShell security..." -ForegroundColor Yellow

try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force -ErrorAction SilentlyContinue
    Write-Host "   ✅ Execution policy updated" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Could not update execution policy (might need admin)" -ForegroundColor Yellow
}

Write-Host "`n"

# ============================================================
# STEP 4: Activate Virtual Environment
# ============================================================

Write-Host "🎯 Step 4: Activating virtual environment..." -ForegroundColor Yellow

& .\venv\Scripts\Activate.ps1

if ($?) {
    Write-Host "   ✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "`n"

# ============================================================
# STEP 5: Install Dependencies
# ============================================================

Write-Host "📥 Step 5: Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "   ⏳ This may take 3-5 minutes (first time only)..." -ForegroundColor Cyan

$packages = @(
    "streamlit==1.28.1",
    "groq==0.9.0",
    "sentence-transformers==2.2.2",
    "chromadb==0.4.24",
    "python-dotenv==1.0.0"
)

pip install $packages -q

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ All dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ❌ Installation failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n"

# ============================================================
# STEP 6: Verify Installation
# ============================================================

Write-Host "✅ Step 6: Verifying installation..." -ForegroundColor Yellow

$packages | ForEach-Object {
    $packageName = ($_ -split "==")[0]
    python -c "import $packageName" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $packageName" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $packageName" -ForegroundColor Red
    }
}

Write-Host "`n"

# ============================================================
# STEP 7: Check API Key
# ============================================================

Write-Host "🔑 Step 7: Checking Groq API Key..." -ForegroundColor Yellow

$apiKey = $env:GROQ_API_KEY

if ([string]::IsNullOrEmpty($apiKey)) {
    Write-Host "   ⚠️  GROQ_API_KEY environment variable not set" -ForegroundColor Yellow

    # Check if it's in .streamlit/secrets.toml
    if (Test-Path ".streamlit/secrets.toml") {
        $secretsContent = Get-Content ".streamlit/secrets.toml" -Raw
        if ($secretsContent -like "*gsk_*") {
            Write-Host "   ✅ API key found in .streamlit/secrets.toml" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  No API key in .streamlit/secrets.toml" -ForegroundColor Yellow
            Write-Host "   📝 Edit .streamlit/secrets.toml and add:" -ForegroundColor Cyan
            Write-Host "      GROQ_API_KEY = `"gsk_your_key_here`"" -ForegroundColor Yellow
            Write-Host "   🔗 Get free key: https://console.groq.com" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "   ✅ GROQ_API_KEY is set" -ForegroundColor Green
}

Write-Host "`n"

# ============================================================
# STEP 8: Launch Streamlit App
# ============================================================

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         🚀 LAUNCHING STREAMLIT APP...                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host "`n"

Write-Host "📍 Your app will open at: http://localhost:8501" -ForegroundColor Cyan
Write-Host "⏹️  Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

# Run Streamlit
$repoPython = Join-Path $PSScriptRoot "..\.venv312\Scripts\python.exe"
if (Test-Path $repoPython) {
    & $repoPython -m streamlit run app.py
} else {
    streamlit run app.py
}
