@echo off
REM Set environment variables to reduce warnings
set TF_CPP_MIN_LOG_LEVEL=2
set HF_HUB_DISABLE_TELEMETRY=1
set HF_HUB_DISABLE_IMPLICIT_TOKEN=1
set TOKENIZERS_PARALLELISM=false
set PYTHONWARNINGS=ignore

REM Run the Streamlit app
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0..\.venv312\Scripts\python.exe"
echo.
echo ===================================
echo   KDU Chatbot is starting...
echo ===================================
echo.
if exist "%PYTHON_EXE%" (
	"%PYTHON_EXE%" -m streamlit run app.py --client.showErrorDetails=true
) else (
	streamlit run app.py --client.showErrorDetails=true
)
