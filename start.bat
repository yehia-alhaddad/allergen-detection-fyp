@echo off
chcp 65001 >nul
cls
echo.
echo ============================================================
echo      🚀 ALLERGEN DETECTION - START ALL SERVICES
echo ============================================================
echo.

REM Run pre-flight checks
echo Running pre-flight checks...
".venv\Scripts\python.exe" preflight_check.py
if errorlevel 1 (
  echo.
  echo [WARN] Pre-flight checks found issues. Continue anyway? (Y/N)
  choice /C YN /N /M "Press Y to continue or N to abort: "
  if errorlevel 2 exit /b 1
)
echo.

REM Check if venv exists
if not exist ".venv\Scripts\python.exe" (
  echo [FAIL] Virtual environment not found!
  echo.
  echo Installing Python dependencies...
  python -m venv .venv
  .venv\Scripts\pip install -r requirements.txt
  if errorlevel 1 (
    echo [FAIL] Failed to install Python packages
    pause
    exit /b 1
  )
)

REM Check if npm packages installed
if not exist "webapp\node_modules" (
  echo [FAIL] npm packages not found!
  echo.
  echo Installing npm packages in webapp folder...
  cd webapp
  call npm install
  if errorlevel 1 (
    echo [FAIL] Failed to install npm packages
    cd ..
    pause
    exit /b 1
  )
  cd ..
  echo [OK] npm packages installed
)

REM Check and setup database
echo Checking database setup...
cd webapp
if not exist "prisma\dev.db" (
  echo Creating database...
  call npx prisma db push --accept-data-loss >nul 2>&1
  call npx prisma generate >nul 2>&1
  echo [OK] Database created
) else (
  REM Ensure Prisma client is generated
  call npx prisma generate >nul 2>&1
  echo [OK] Database ready
)
cd ..

echo [1/3] Starting ML API (port 8000)...
set "LOG_FILE=%TEMP%\allergen_ml_api.log"
start "ML API" /MIN cmd /c "".venv\Scripts\python.exe" -m src.api.allergen_api --host 127.0.0.1 --port 8000 2>&1 | tee "%LOG_FILE%""
echo    Waiting for API to initialize...
ping 127.0.0.1 -n 4 >nul

echo [2/3] Checking ML API health...
set API_HEALTHY=0
for /L %%i in (1,1,15) do (
  powershell -Command "(Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue).StatusCode" >nul 2>&1
  if not errorlevel 1 (
    echo [OK] ML API is healthy
    set API_HEALTHY=1
    goto api_ready
  )
  ping 127.0.0.1 -n 2 >nul
)

if "%API_HEALTHY%"=="0" (
  echo [FAIL] ML API failed to start! Check log: %LOG_FILE%
  echo.
  echo Common issues:
  echo   1. Port 8000 already in use
  echo   2. Missing Python dependencies
  echo   3. Model files not found
  echo.
  echo Continue without ML API? Website will use mock data. (Y/N)
  choice /C YN /N /M "Press Y to continue or N to abort: "
  if errorlevel 2 (
    taskkill /FI "WINDOWTITLE eq ML API" /F >nul 2>&1
    exit /b 1
  )
)

:api_ready
echo [3/3] Starting Next.js website (port 3000)...
cd webapp
start "Next.js Dev" /MIN npm run dev
cd ..

echo.
echo ============================================================
echo [OK] Services started!
echo.
echo   WEB:   http://localhost:3000
echo   API:   http://localhost:8000
echo   DOCS:  http://localhost:8000/docs
echo.
echo Browser should open automatically. If not, visit:
echo   http://localhost:3000
echo.
echo To stop services:
echo   - Close the "ML API" and "Next.js Dev" windows
echo   - Or press Ctrl+C in this window
echo ============================================================
echo.

REM Open browser
ping 127.0.0.1 -n 3 >nul
start http://localhost:3000

REM Keep window open and provide shutdown option
echo.
echo Services are running...
echo Press any key to stop all services and exit.
pause >nul

echo.
echo Stopping services...
taskkill /FI "WINDOWTITLE eq ML API" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Next.js Dev" /F >nul 2>&1
echo [OK] Services stopped
ping 127.0.0.1 -n 2 >nul
