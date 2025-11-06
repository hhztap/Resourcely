@echo off
echo ========================================
echo    Resourcely Staffing Suggester
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo Docker found! Starting Resourcely application...
echo.

REM Stop any existing container
docker-compose down >nul 2>&1

REM Build and start the application
echo Building Docker image (this may take a few minutes on first run)...
docker-compose up --build -d

if %errorlevel% neq 0 (
    echo ERROR: Failed to start the application
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo    SUCCESS! Application is starting...
echo ========================================
echo.
echo The Resourcely Staffing Suggester is now running!
echo.
echo Open your web browser and go to:
echo    http://localhost:8501
echo.
echo To stop the application, run: docker-compose down
echo Or close this window and run stop-resourcely.bat
echo.
echo Press any key to open the application in your default browser...
pause >nul

REM Try to open the browser
start http://localhost:8501

echo.
echo Application is running in the background.
echo Close this window when you're done using the application.
echo.
pause