#!/bin/bash
set -e

echo "🚀 Starting Photo Album Java Application with PostgreSQL"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker Compose is available"

# Start the services
echo "🔄 Starting services with Docker Compose..."
echo "   - PostgreSQL 15 Database"
echo "   - Photo Album Java Application"
echo ""

docker-compose up --build

echo ""
echo "🛑 Services stopped. To clean up completely, run:"
echo "   docker-compose down -v"