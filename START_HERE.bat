@echo off
REM Kyungdong Chatbot - Complete Automated Setup & Run
REM Just double-click this file!

setlocal enabledelayedexpansion

cls
color 0A
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  🎓 Kyungdong University RAG Chatbot - Auto Setup     ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM STEP 1: Check if Python is installed
REM ============================================================

echo [1/8] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found: %PYTHON_VERSION%
echo.

REM ============================================================
REM STEP 2: Check if in correct directory
REM ============================================================

echo [2/8] Checking project structure...
if not exist "app.py" (
    echo ERROR: app.py not found!
    echo Make sure you're in the correct directory
    pause
    exit /b 1
)
echo ✅ app.py found
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found!
    pause
    exit /b 1
)
echo ✅ requirements.txt found
if not exist "src" (
    echo ERROR: src folder not found!
    pause
    exit /b 1
)
echo ✅ src folder found
if not exist ".streamlit" (
    echo ERROR: .streamlit folder not found!
    pause
    exit /b 1
)
echo ✅ .streamlit folder found
echo.

REM ============================================================
REM STEP 3: Get Groq API Key from user
REM ============================================================

echo [3/8] Getting Groq API Key...
echo.
echo Do you have a Groq API Key?
echo If NO: Visit https://console.groq.com (takes 2 minutes, free)
echo.
set /p API_KEY="Enter your Groq API Key (starts with gsk_): "

if "!API_KEY!"=="" (
    echo ERROR: API Key is required!
    pause
    exit /b 1
)

if not "!API_KEY:~0,4!"=="gsk_" (
    echo ERROR: Invalid API key format! Must start with 'gsk_'
    pause
    exit /b 1
)

echo ✅ API Key received
echo.

REM ============================================================
REM STEP 4: Save API Key to configuration files
REM ============================================================

echo [4/8] Saving API Key to configuration...
(
    echo GROQ_API_KEY=%API_KEY%
) > .env
echo ✅ .env updated

(
    echo GROQ_API_KEY = "%API_KEY%"
) > .streamlit\secrets.toml
echo ✅ .streamlit/secrets.toml updated
echo.

REM ============================================================
REM STEP 5: Set environment variable
REM ============================================================

echo [5/8] Setting environment variables...
setx GROQ_API_KEY "%API_KEY%" >nul
set GROQ_API_KEY=%API_KEY%
echo ✅ GROQ_API_KEY set
echo.

REM ============================================================
REM STEP 6: Create virtual environment
REM ============================================================

echo [6/8] Creating virtual environment...
if exist "venv" (
    echo Removing old venv...
    rmdir /s /q venv >nul 2>&1
)
python -m venv venv
if not exist "venv" (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created
echo.

REM ============================================================
REM STEP 7: Install packages
REM ============================================================

echo [7/8] Installing Python packages...
echo ⏳ This may take 3-5 minutes...
echo.

call venv\Scripts\activate.bat
pip install -q streamlit groq sentence-transformers chromadb python-dotenv

if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo ✅ All packages installed
echo.

REM ============================================================
REM STEP 8: Run the chatbot
REM ============================================================

echo [8/8] Starting Streamlit App...
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║         ✅ SETUP COMPLETE - LAUNCHING APP            ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Your browser will open at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
timeout /t 3

call venv\Scripts\activate.bat
streamlit run app.py

pause