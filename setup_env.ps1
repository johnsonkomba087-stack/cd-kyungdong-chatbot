# ============================================================
# KYUNGDONG CHATBOT - ENVIRONMENT SETUP SCRIPT
# ============================================================

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🔧 Environment Setup - Kyungdong University Chatbot  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ============================================================
# STEP 1: Get Current Directory
# ============================================================

$currentPath = Get-Location
Write-Host "📍 Current Directory: $currentPath`n" -ForegroundColor Yellow

# Fix if in wrong directory
if ($currentPath -like "*\app.py*") {
    Write-Host "⚠️  Wrong directory detected. Moving up..." -ForegroundColor Red
    $currentPath = (Get-Item $currentPath).Parent.FullName
    Set-Location $currentPath
    Write-Host "✅ Moved to: $currentPath`n" -ForegroundColor Green
}

# ============================================================
# STEP 2: Verify Project Structure
# ============================================================

Write-Host "📂 Verifying project structure..." -ForegroundColor Yellow

$requiredFiles = @("app.py", "requirements.txt", ".env")
$requiredFolders = @("src", ".streamlit")

$allGood = $true

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Missing: $file" -ForegroundColor Red
        $allGood = $false
    }
}

foreach ($folder in $requiredFolders) {
    if (Test-Path $folder) {
        Write-Host "   ✅ $folder/" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Missing: $folder/" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host "`n"

if (-not $allGood) {
    Write-Host "❌ Some files are missing! Check your project structure.`n" -ForegroundColor Red
    exit 1
}

# ============================================================
# STEP 3: Get Groq API Key from User
# ============================================================

Write-Host "🔑 GROQ API KEY SETUP" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "Do you have a Groq API Key?" -ForegroundColor Yellow
Write-Host "  - If NO: Visit https://console.groq.com (2 minutes, free)" -ForegroundColor Gray
Write-Host "  - If YES: Continue below`n" -ForegroundColor Gray

$hasKey = Read-Host "Do you have your API key? (yes/no)"

if ($hasKey.ToLower() -ne "yes" -and $hasKey.ToLower() -ne "y") {
    Write-Host "`n❌ Please get your free API key first:" -ForegroundColor Red
    Write-Host "   🔗 https://console.groq.com`n" -ForegroundColor Cyan
    exit 1
}

# Get API key from user
Write-Host "📝 Enter your Groq API Key (starts with 'gsk_'):" -ForegroundColor Yellow
$apiKey = Read-Host "API Key"

if (-not $apiKey.StartsWith("gsk_")) {
    Write-Host "`n❌ Invalid API key format! Must start with 'gsk_'`n" -ForegroundColor Red
    exit 1
}

Write-Host "✅ API Key received`n" -ForegroundColor Green

# ============================================================
# STEP 4: Save API Key to Files
# ============================================================

Write-Host "💾 Saving API Key to configuration files..." -ForegroundColor Yellow

# Update .env file
Write-Host "   📝 Updating .env..." -ForegroundColor Gray
$envContent = "GROQ_API_KEY=$apiKey"
Set-Content -Path ".env" -Value $envContent
Write-Host "   ✅ .env updated" -ForegroundColor Green

# Update .streamlit/secrets.toml
Write-Host "   📝 Updating .streamlit/secrets.toml..." -ForegroundColor Gray
$secretsContent = "GROQ_API_KEY = `"$apiKey`""
Set-Content -Path ".streamlit/secrets.toml" -Value $secretsContent
Write-Host "   ✅ .streamlit/secrets.toml updated" -ForegroundColor Green

Write-Host "`n"

# ============================================================
# STEP 5: Set Environment Variable
# ============================================================

Write-Host "🌍 Setting environment variables..." -ForegroundColor Yellow

$env:GROQ_API_KEY = $apiKey
Write-Host "   ✅ GROQ_API_KEY set for current session" -ForegroundColor Green

# Try to set permanently
try {
    [Environment]::SetEnvironmentVariable("GROQ_API_KEY", $apiKey, "User")
    Write-Host "   ✅ GROQ_API_KEY saved permanently for your user" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Could not set permanent environment variable (needs admin)" -ForegroundColor Yellow
    Write-Host "      But it's set for this session!" -ForegroundColor Gray
}

Write-Host "`n"

# ============================================================
# STEP 6: Create Virtual Environment
# ============================================================

Write-Host "🐍 Creating Python Virtual Environment..." -ForegroundColor Yellow

# Remove old venv
if (Test-Path "venv") {
    Write-Host "   🗑️  Removing old virtual environment..." -ForegroundColor Gray
    Remove-Item -Recurse -Force "venv" -ErrorAction SilentlyContinue
}

# Create new venv
python -m venv venv
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "`n"

# ============================================================
# STEP 7: Fix PowerShell Execution Policy
# ============================================================

Write-Host "🔐 Configuring PowerShell Security..." -ForegroundColor Yellow

try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force -ErrorAction SilentlyContinue
    Write-Host "   ✅ Execution policy configured" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Could not set execution policy (might need admin)" -ForegroundColor Yellow
}

Write-Host "`n"

# ============================================================
# STEP 8: Activate Virtual Environment
# ============================================================

Write-Host "🎯 Activating Virtual Environment..." -ForegroundColor Yellow

& .\venv\Scripts\Activate.ps1

if ($?) {
    Write-Host "   ✅ Virtual environment activated" -ForegroundColor Green
    Write-Host "   📌 You should see (venv) at the start of your terminal" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Failed to activate" -ForegroundColor Red
    Write-Host "   Try manually: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n"

# ============================================================
# STEP 9: Install Dependencies
# ============================================================

Write-Host "📥 Installing Python Packages..." -ForegroundColor Yellow
Write-Host "   ⏳ This may take 3-5 minutes on first run..." -ForegroundColor Cyan

$packages = @(
    "streamlit==1.28.1",
    "groq==0.9.0",
    "sentence-transformers==2.2.2",
    "chromadb==0.4.24",
    "python-dotenv==1.0.0"
)

pip install $packages

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ All packages installed successfully" -ForegroundColor Green
} else {
    Write-Host "   ❌ Installation failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n"

# ============================================================
# STEP 10: Verify Installation
# ============================================================

Write-Host "✅ Verifying Installation..." -ForegroundColor Yellow

$testPackages = @("streamlit", "groq", "sentence_transformers", "chromadb", "dotenv")
$allInstalled = $true

foreach ($pkg in $testPackages) {
    python -c "import $pkg" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $pkg" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $pkg" -ForegroundColor Red
        $allInstalled = $false
    }
}

Write-Host "`n"

if (-not $allInstalled) {
    Write-Host "❌ Some packages failed to install" -ForegroundColor Red
    exit 1
}

# ============================================================
# STEP 11: Verify API Key
# ============================================================

Write-Host "🔐 Verifying API Key..." -ForegroundColor Yellow

if ([string]::IsNullOrEmpty($env:GROQ_API_KEY)) {
    Write-Host "   ❌ GROQ_API_KEY not set in environment" -ForegroundColor Red
} else {
    $keyPreview = $env:GROQ_API_KEY.Substring(0, 10) + "..."
    Write-Host "   ✅ GROQ_API_KEY set: $keyPreview" -ForegroundColor Green
}

Write-Host "`n"

# ============================================================
# FINAL SUMMARY
# ============================================================

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         ✅ ENVIRONMENT SETUP COMPLETE!               ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📋 Configuration Summary:" -ForegroundColor Cyan
Write-Host "   • Project Directory: $(Get-Location)" -ForegroundColor Gray
Write-Host "   • Virtual Environment: Activated ✅" -ForegroundColor Gray
Write-Host "   • Python Packages: Installed ✅" -ForegroundColor Gray
Write-Host "   • Groq API Key: Configured ✅" -ForegroundColor Gray

Write-Host "`n🚀 Next Step: Run the Chatbot" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════`n" -ForegroundColor Green

Write-Host "Run this command:" -ForegroundColor Yellow
Write-Host "`n   streamlit run app.py`n" -ForegroundColor Cyan

Write-Host "Then open in browser:" -ForegroundColor Yellow
Write-Host "`n   http://localhost:8501`n" -ForegroundColor Cyan

Write-Host "⏹️  Press Ctrl+C to stop the server" -ForegroundColor Yellow

# Ask if user wants to run now
Write-Host "`n"
$runNow = Read-Host "Run the chatbot now? (yes/no)"

if ($runNow.ToLower() -eq "yes" -or $runNow.ToLower() -eq "y") {
    Write-Host "`n🚀 Starting Streamlit App...\n" -ForegroundColor Green
    streamlit run app.py
} else {
    Write-Host "`n✅ Setup complete! Run 'streamlit run app.py' when ready." -ForegroundColor Green
    Write-Host "`n"
}