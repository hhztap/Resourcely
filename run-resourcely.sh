#!/bin/bash

echo "========================================"
echo "    Resourcely Staffing Suggester"
echo "========================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    echo "Please install Docker from: https://www.docker.com/get-started"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not available"
    echo "Please install Docker Compose or use a newer version of Docker"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Docker found! Starting Resourcely application..."
echo

# Stop any existing container
docker-compose down > /dev/null 2>&1

# Build and start the application
echo "Building Docker image (this may take a few minutes on first run)..."

# Use docker compose if available, otherwise fall back to docker-compose
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD up --build -d

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start the application"
    echo "Please check the error messages above"
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "========================================"
echo "    SUCCESS! Application is starting..."
echo "========================================"
echo
echo "The Resourcely Staffing Suggester is now running!"
echo
echo "Open your web browser and go to:"
echo "    http://localhost:8501"
echo
echo "To stop the application, run: $COMPOSE_CMD down"
echo "Or run the stop-resourcely.sh script"
echo

# Wait a moment for the container to start
echo "Waiting for application to start..."
sleep 5

# Try to open the browser (works on most Linux distributions and macOS)
if command -v xdg-open &> /dev/null; then
    echo "Opening application in your default browser..."
    xdg-open http://localhost:8501 &> /dev/null &
elif command -v open &> /dev/null; then
    echo "Opening application in your default browser..."
    open http://localhost:8501 &> /dev/null &
else
    echo "Please manually open http://localhost:8501 in your browser"
fi

echo
echo "Application is running in the background."
echo "Press Ctrl+C to stop monitoring, or close this terminal when done."
echo

# Keep the script running and show logs
echo "=== Application Logs ==="
$COMPOSE_CMD logs -f