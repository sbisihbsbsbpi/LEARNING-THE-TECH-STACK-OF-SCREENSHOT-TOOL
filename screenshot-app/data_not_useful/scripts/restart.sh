#!/bin/bash

echo "🔄 Restarting Screenshot App..."
echo ""

# Kill existing processes
echo "🛑 Stopping existing processes..."
pkill -f "python.*main.py" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Start backend
echo "🚀 Starting backend..."
cd backend
python3 main.py &
BACKEND_PID=$!
echo "   ✅ Backend started (PID: $BACKEND_PID)"
cd ..

# Wait a bit for backend to start
sleep 2

# Start frontend
echo "🚀 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "   ✅ Frontend started (PID: $FRONTEND_PID)"
cd ..

echo ""
echo "✅ App restarted successfully!"
echo ""
echo "📍 Frontend: http://localhost:1420"
echo "📍 Backend:  http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Wait for user to stop
wait

