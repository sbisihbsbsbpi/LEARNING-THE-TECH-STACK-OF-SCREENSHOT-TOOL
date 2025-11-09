#!/bin/bash

# Screenshot Tool - Web App Launcher
# Click this to open the app in your browser!

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Launching Screenshot Tool...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Check if backend is already running
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend already running${NC}"
else
    echo -e "${BLUE}📦 Starting backend...${NC}"
    cd backend
    python3 main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend
    echo -e "${YELLOW}⏳ Waiting for backend...${NC}"
    for i in {1..10}; do
        if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend started${NC}"
            break
        fi
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ Backend failed to start${NC}"
            exit 1
        fi
        sleep 1
    done
fi

# Check if frontend is already running
if curl -s http://localhost:1420 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend already running${NC}"
else
    echo -e "${BLUE}🎨 Starting frontend...${NC}"
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..

    # Wait for frontend
    echo -e "${YELLOW}⏳ Waiting for frontend...${NC}"
    for i in {1..15}; do
        if curl -s http://localhost:1420 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend started${NC}"
            break
        fi
        if [ $i -eq 15 ]; then
            echo -e "${RED}❌ Frontend failed to start${NC}"
            echo -e "${YELLOW}💡 Check frontend.log for errors${NC}"
            tail -n 20 frontend.log 2>/dev/null || echo "No log file found"
            exit 1
        fi
        sleep 1
    done
fi

# Open in browser
echo ""
echo -e "${GREEN}🌐 Opening in browser...${NC}"
sleep 1

# Detect OS and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - try Chrome first, then default browser
    if [ -d "/Applications/Google Chrome.app" ]; then
        open -a "Google Chrome" http://localhost:1420
    else
        open http://localhost:1420
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - try Chrome/Chromium first
    if command -v google-chrome &> /dev/null; then
        google-chrome http://localhost:1420 &
    elif command -v chromium-browser &> /dev/null; then
        chromium-browser http://localhost:1420 &
    else
        xdg-open http://localhost:1420 &
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    start chrome http://localhost:1420 || start http://localhost:1420
fi

echo ""
echo -e "${GREEN}✅ App is running!${NC}"
echo -e "${BLUE}📍 URL: http://localhost:1420${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the app${NC}"
echo ""

# Keep script running
wait

