#!/bin/bash

# Screenshot Tool Startup Script
# This script starts both the backend and frontend in sync

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Screenshot Tool...${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Stopped backend${NC}"
    fi
    exit 0
}

# Trap Ctrl+C and other exit signals
trap cleanup SIGINT SIGTERM EXIT

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.12+${NC}"
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 22+${NC}"
    exit 1
fi

# Check if Rust is installed (for Tauri)
if ! command -v rustc &> /dev/null; then
    echo -e "${RED}❌ Rust is not installed. Please install Rust 1.91+${NC}"
    echo -e "${YELLOW}💡 Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites installed${NC}"
echo ""

# Check if backend dependencies are installed
if [ ! -d "backend/__pycache__" ] && [ ! -f "backend/.venv/bin/activate" ]; then
    echo -e "${YELLOW}⚠️  Backend dependencies may not be installed${NC}"
    echo -e "${YELLOW}💡 Run: cd backend && pip install -r requirements.txt${NC}"
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not installed${NC}"
    echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    echo ""
fi

# Start backend in background
echo -e "${BLUE}📦 Starting backend (FastAPI)...${NC}"
cd backend
python3 main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
for i in {1..10}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend started successfully at http://127.0.0.1:8000${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Backend failed to start after 10 seconds${NC}"
        echo -e "${YELLOW}💡 Check backend.log for errors${NC}"
        tail -n 20 backend.log
        exit 1
    fi
    sleep 1
done

echo ""
echo -e "${BLUE}🎨 Starting frontend (Tauri Desktop App)...${NC}"
echo -e "${YELLOW}💡 This will open the desktop application window${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop both frontend and backend${NC}"
echo ""

cd frontend
npm run tauri dev

# Cleanup happens automatically via trap

