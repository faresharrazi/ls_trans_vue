#!/bin/bash

echo "🚀 Starting Transcription App..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

# Start backend in background
echo "🔧 Starting Flask backend..."
cd ..
python api.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Vue frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ App is starting up!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait

# Cleanup
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo "👋 App stopped" 