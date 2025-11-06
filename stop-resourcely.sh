#!/bin/bash

echo "========================================"
echo "    Stopping Resourcely Application"
echo "========================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Stopping Resourcely application..."

# Use docker compose if available, otherwise fall back to docker-compose
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD down

if [ $? -ne 0 ]; then
    echo "WARNING: Failed to stop with $COMPOSE_CMD, trying alternative method..."
    docker stop resourcely-resourcely-app-1 > /dev/null 2>&1
    docker rm resourcely-resourcely-app-1 > /dev/null 2>&1
fi

echo
echo "========================================"
echo "    Application Stopped Successfully"
echo "========================================"
echo
echo "The Resourcely Staffing Suggester has been stopped."
echo "You can restart it anytime by running ./run-resourcely.sh"
echo