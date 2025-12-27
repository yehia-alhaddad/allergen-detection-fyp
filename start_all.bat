@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo    🚀 ALLERGEN DETECTION SYSTEM - COMPLETE STARTUP
echo ============================================================
echo.

set PYTHONPATH=%CD%
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_LOGGER_LEVEL=error
set STREAMLIT_CLIENT_TOOLBARMODE=minimal

echo [1/3] Starting FastAPI Server...
start "FastAPI Server" ".venv\Scripts\python.exe" src\api\allergen_api.py
echo ✓ API process started (PID in new window)

echo [2/3] Waiting for API to initialize... (5 seconds)
timeout /t 5 /nobreak

echo [3/3] Starting Streamlit UI...
".venv\Scripts\python.exe" -m streamlit run "app\streamlit_app.py"

echo.
echo ============================================================
echo System shutdown
echo ============================================================
pause
