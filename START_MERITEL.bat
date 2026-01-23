@echo off
echo ========================================
echo   Starting MeriTel Meeting Assistant
echo ========================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from nodejs.org
    pause
    exit /b 1
)

echo [1/4] Checking backend dependencies...
cd backend
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1

echo [2/4] Starting Backend Server...
start "MeriTel Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate.bat && python app.py"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo [3/4] Checking frontend dependencies...
cd ..\frontend
if not exist "node_modules" (
    echo Installing frontend dependencies (this may take a few minutes)...
    call npm install
)

echo [4/4] Starting Frontend Server...
start "MeriTel Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo ========================================
echo   MeriTel is starting up!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Two command windows will open:
echo   - MeriTel Backend (Python/Flask)
echo   - MeriTel Frontend (React)
echo.
echo Your browser will open automatically in 30 seconds...
echo.
echo To stop MeriTel, close both command windows
echo or run STOP_MERITEL.bat
echo.
echo ========================================

REM Wait for frontend to compile and start
timeout /t 30 /nobreak >nul

REM Open browser
start http://localhost:3000

pause
