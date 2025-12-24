#!/bin/bash

# EURING Code Recognition System - Startup Script

echo "🚀 Starting EURING Code Recognition System..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python3 --version

# Install dependencies if needed
echo "📦 Checking dependencies..."
cd backend
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Try to import FastAPI to check if dependencies are installed
python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    python3 -m pip install fastapi uvicorn pydantic
fi

echo ""
echo "✅ System ready!"
echo ""
echo "🌐 Starting server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/api/euring/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
PYTHONPATH=. python3 main.py