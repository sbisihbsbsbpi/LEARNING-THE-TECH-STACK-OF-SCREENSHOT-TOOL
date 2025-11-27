#!/bin/bash

# 🦁 Brave Browser CDP Launch Script
# Launches Brave with Chrome DevTools Protocol enabled on port 9222

echo "🦁 Brave CDP Launcher"
echo "===================="
echo ""

# Check if Brave is installed
BRAVE_PATH="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
if [ ! -f "$BRAVE_PATH" ]; then
    echo "❌ Error: Brave Browser not found at: $BRAVE_PATH"
    echo ""
    echo "Please install Brave Browser from: https://brave.com/download/"
    exit 1
fi

# Ask user which profile to use
echo "Which profile do you want to use?"
echo ""
echo "1) Temporary profile (safe, fresh start)"
echo "2) Real profile (keep your sessions, logins, cookies)"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "2" ]; then
    # Real profile
    USER_DATA_DIR="$HOME/Library/Application Support/BraveSoftware/Brave-Browser"
    
    echo ""
    echo "⚠️  WARNING: Using real profile"
    echo "   This will close all existing Brave windows!"
    echo ""
    read -p "Continue? (y/n): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "❌ Cancelled"
        exit 0
    fi
    
    echo ""
    echo "🔄 Closing existing Brave instances..."
    killall "Brave Browser" 2>/dev/null || true
    sleep 2
else
    # Temporary profile
    USER_DATA_DIR="/tmp/brave-debug-profile"
    echo ""
    echo "✅ Using temporary profile: $USER_DATA_DIR"
fi

# Check if port 9222 is already in use
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo ""
    echo "⚠️  WARNING: Port 9222 is already in use!"
    echo ""
    echo "Processes using port 9222:"
    lsof -i :9222
    echo ""
    read -p "Kill these processes and continue? (y/n): " kill_confirm
    
    if [ "$kill_confirm" = "y" ] || [ "$kill_confirm" = "Y" ]; then
        echo "🔪 Killing processes on port 9222..."
        lsof -ti :9222 | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        echo "❌ Cancelled"
        exit 0
    fi
fi

# Launch Brave with CDP
echo ""
echo "🚀 Launching Brave with CDP..."
echo "   Port: 9222"
echo "   Profile: $USER_DATA_DIR"
echo ""

"$BRAVE_PATH" \
	  --remote-debugging-address=127.0.0.1 \
	  --remote-debugging-port=9222 \
	  --user-data-dir="$USER_DATA_DIR" \
	  > /dev/null 2>&1 &

BRAVE_PID=$!

# Wait a moment for Brave to start
sleep 3

# Verify CDP is working
echo "🔍 Verifying CDP connection..."
if curl -s http://localhost:9222/json/version > /dev/null 2>&1; then
    echo ""
    echo "✅ SUCCESS! Brave is running with CDP enabled"
    echo ""
    echo "📊 CDP Information:"
    echo "   Endpoint: http://localhost:9222"
    echo "   Process ID: $BRAVE_PID"
    echo ""
    echo "🔗 Verify in browser: http://localhost:9222/json/version"
    echo ""
    echo "📸 Next Steps:"
    echo "   1. Open your screenshot tool"
    echo "   2. Go to Settings"
    echo "   3. Enable '🌐 Real Browser Mode (CDP Mode)'"
    echo "   4. Start capturing screenshots!"
    echo ""
    echo "🛑 To stop: Close Brave or run: kill $BRAVE_PID"
else
    echo ""
    echo "❌ ERROR: CDP connection failed"
    echo ""
    echo "Troubleshooting:"
    echo "   1. Check if Brave is running: ps aux | grep Brave"
    echo "   2. Check port 9222: lsof -i :9222"
    echo "   3. Try manually: curl http://localhost:9222/json/version"
    echo ""
    echo "🛑 Killing Brave process..."
    kill $BRAVE_PID 2>/dev/null || true
    exit 1
fi

