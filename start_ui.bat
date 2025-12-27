@echo off
echo.
echo ============================================================
echo Starting Allergen Detection Web App...
echo ============================================================
echo.
set PYTHONPATH=%CD%
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_LOGGER_LEVEL=error
set STREAMLIT_CLIENT_TOOLBARMODE=minimal

REM Start the Streamlit app
echo [1/2] Launching Streamlit...
".venv\Scripts\python.exe" -m streamlit run "app\streamlit_app.py"

REM If we get here, Streamlit exited
echo.
echo ============================================================
echo ERROR: Streamlit exited unexpectedly
echo ============================================================
pause
