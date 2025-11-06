@echo off
echo ========================================
echo    Resourcely Staffing Suggester
echo    Python Version (Backup Option)
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found! Setting up Resourcely application...
echo.

REM Install required packages
echo Installing required Python packages...
pip install pandas streamlit

if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Starting Application...
echo ========================================
echo.

REM Start the application
echo Starting Resourcely Staffing Suggester...
echo The application will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the application when you're done.
echo.

streamlit run app.py --server.port 8501 --server.address localhost

echo.
echo Application has been stopped.
pause