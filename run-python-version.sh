#!/bin/bash

echo "========================================"
echo "    Resourcely Staffing Suggester"
echo "    Python Version (Backup Option)"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python from: https://www.python.org/downloads/"
    echo "Or use your system package manager:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo "Python found! Setting up Resourcely application..."
echo

# Install required packages
echo "Installing required Python packages..."
$PIP_CMD install pandas streamlit

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install required packages"
    echo "Please check your internet connection and try again"
    echo "You may need to run: sudo $PIP_CMD install pandas streamlit"
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "========================================"
echo "    Starting Application..."
echo "========================================"
echo

# Start the application
echo "Starting Resourcely Staffing Suggester..."
echo "The application will open in your browser at http://localhost:8501"
echo
echo "Press Ctrl+C to stop the application when you're done."
echo

# Try to open the browser after a short delay
(sleep 3 && if command -v xdg-open &> /dev/null; then xdg-open http://localhost:8501; elif command -v open &> /dev/null; then open http://localhost:8501; fi) &

streamlit run app.py --server.port 8501 --server.address localhost

echo
echo "Application has been stopped."