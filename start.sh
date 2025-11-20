#!/bin/bash

# Legal Risk Analysis - Start Script
# This script starts both the backend and frontend servers

echo "=================================="
echo "Legal Risk Analysis System"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the LegalRiskAnalysis directory"
    exit 1
fi

# Start backend
echo "Starting Backend Server..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting Frontend Server..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=================================="
echo "Servers Started!"
echo "=================================="
echo ""
echo "Backend API:  http://localhost:8000"
echo "API Docs:     http://localhost:8000/api/docs"
echo "Frontend:     http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

# Wait for processes
wait
