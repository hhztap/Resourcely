@echo off
echo ========================================
echo    Stopping Resourcely Application
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo.
    pause
    exit /b 1
)

echo Stopping Resourcely application...
docker-compose down

if %errorlevel% neq 0 (
    echo WARNING: Failed to stop with docker-compose, trying alternative method...
    docker stop resourcely-resourcely-app-1 >nul 2>&1
    docker rm resourcely-resourcely-app-1 >nul 2>&1
)

echo.
echo ========================================
echo    Application Stopped Successfully
echo ========================================
echo.
echo The Resourcely Staffing Suggester has been stopped.
echo You can restart it anytime by running run-resourcely.bat
echo.
pause