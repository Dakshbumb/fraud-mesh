#!/bin/bash

# FraudMesh Startup Script
# Starts both backend and frontend servers

echo "🔐 Starting FraudMesh..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY before continuing."
    exit 1
fi

# Start backend in background
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Start frontend in background
echo "🚀 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ FraudMesh is running!"
echo "📊 Dashboard: http://localhost:5173"
echo "🔌 Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Handle Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Wait for processes
wait
