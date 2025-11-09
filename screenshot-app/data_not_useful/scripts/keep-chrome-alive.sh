#!/bin/bash

# Keep Chrome running with remote debugging
# This script monitors Chrome and restarts it if it closes

echo "🔄 Chrome Keep-Alive Monitor"
echo "This will keep Chrome running with remote debugging enabled"
echo "Press Ctrl+C to stop"
echo ""

# Function to launch Chrome
launch_chrome() {
    echo "🚀 Launching Chrome with remote debugging..."
    # Use your main Chrome profile (preserves logins, cookies, etc.)
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
        --remote-debugging-port=9222 \
        --user-data-dir="$HOME/Library/Application Support/Google/Chrome" \
        > /dev/null 2>&1 &

    sleep 2

    if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ Chrome is running on port 9222 with your normal profile"
    else
        echo "❌ Failed to start Chrome"
        return 1
    fi
}

# Initial launch
if ! lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
    # Kill any existing Chrome processes first
    pkill -9 -f "Google Chrome" 2>/dev/null
    sleep 2
    launch_chrome
else
    echo "✅ Chrome is already running on port 9222"
fi

# Monitor loop
while true; do
    if ! lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo ""
        echo "⚠️  Chrome stopped! Restarting..."
        sleep 1
        launch_chrome
    fi
    sleep 5
done

