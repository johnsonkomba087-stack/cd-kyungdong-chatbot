@echo off
setlocal
cls
color 0A

cd /d "%~dp0"
set "REPO_PYTHON=%~dp0..\.venv312\Scripts\python.exe"

echo.
echo ========================================================
echo         KDU CHATBOT - ONLINE READY START SCRIPT
echo ========================================================
echo.

if exist "%REPO_PYTHON%" (
    set "PYTHON_EXE=%REPO_PYTHON%"
) else (
    set "PYTHON_EXE=python"
)

echo [1/4] Checking Python...
"%PYTHON_EXE%" --version
if errorlevel 1 (
    echo ERROR: Python is not available.
    pause
    exit /b 1
)
echo.

echo [2/4] Checking API key file...
if not exist ".streamlit\secrets.toml" (
    if exist ".streamlit\secrets.toml.example" (
        echo INFO: Copy .streamlit\secrets.toml.example to .streamlit\secrets.toml and add your Groq key.
    ) else (
        echo INFO: Create .streamlit\secrets.toml with GROQ_API_KEY.
    )
)
echo.

echo [3/4] Installing requirements...
"%PYTHON_EXE%" -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements.
    pause
    exit /b 1
)
echo.

echo [4/4] Starting Streamlit app...
echo.
echo App URL: http://localhost:8501
echo Press Ctrl+C to stop the app.
echo.

"%PYTHON_EXE%" -m streamlit run app.py