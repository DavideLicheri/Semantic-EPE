#!/bin/bash

# EURING Code Recognition System Setup Script

echo "Setting up EURING Code Recognition System..."

# Backend setup
echo "Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend

# Check if Node.js is available
if command -v npm &> /dev/null; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Warning: npm not found. Please install Node.js to set up the frontend."
fi

cd ..

echo "Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "To start the frontend:"
echo "  cd frontend" 
echo "  npm run dev"