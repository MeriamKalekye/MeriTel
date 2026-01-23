@echo off
echo ========================================
echo   Stopping MeriTel Meeting Assistant
echo ========================================
echo.

echo Stopping Backend Server (Python)...
taskkill /FI "WindowTitle eq MeriTel Backend*" /T /F >nul 2>&1

echo Stopping Frontend Server (Node.js)...
taskkill /FI "WindowTitle eq MeriTel Frontend*" /T /F >nul 2>&1

REM Kill any remaining Python and Node processes related to MeriTel
for /f "tokens=2" %%i in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /PID %%i /F >nul 2>&1
)

for /f "tokens=2" %%i in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /PID %%i /F >nul 2>&1
)

echo.
echo ========================================
echo   MeriTel has been stopped
echo ========================================
echo.
pause
