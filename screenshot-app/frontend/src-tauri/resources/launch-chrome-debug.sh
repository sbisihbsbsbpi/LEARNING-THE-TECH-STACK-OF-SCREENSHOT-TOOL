#!/bin/bash

# Launch Chrome with Remote Debugging for Screenshot Tool
# This script is bundled with the app and launched automatically when user enables Real Browser Mode

echo "🚀 Launching Chrome with Remote Debugging..."
echo ""

# Check if port 9222 is already in use
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Chrome is already running with remote debugging on port 9222!"
    echo ""
    echo "CDP Endpoint: http://localhost:9222"
    echo ""
    exit 0
fi

# Check if Chrome is already running (without debugging)
if pgrep -x "Google Chrome" > /dev/null; then
    echo "⚠️  Chrome is already running (without remote debugging)!"
    echo ""
    echo "Please close Chrome completely (Cmd+Q) and try again."
    echo ""
    exit 1
fi

# Chrome profile directory for the app
CHROME_PROFILE="$HOME/Library/Application Support/ScreenshotTool-Chrome"

# Create profile directory if it doesn't exist
if [ ! -d "$CHROME_PROFILE" ]; then
    echo "📁 Creating Chrome profile directory..."
    mkdir -p "$CHROME_PROFILE/Default"
    
    # Create minimal preferences file
    cat > "$CHROME_PROFILE/Default/Preferences" << 'EOF'
{
  "browser": {
    "check_default_browser": false,
    "show_home_button": false
  },
  "profile": {
    "name": "Screenshot Tool Profile"
  },
  "first_run_tabs": []
}
EOF
    
    echo "✅ Profile created at: $CHROME_PROFILE"
fi

echo "Launching Chrome with:"
echo "  ✅ Remote debugging on port 9222"
echo "  ✅ Screenshot Tool profile"
echo ""

# Launch Chrome with remote debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$CHROME_PROFILE" \
    --new-window \
    "data:text/html,<html><head><title>Screenshot Tool - Chrome Ready</title><style>body{margin:0;padding:40px;font-family:system-ui;background:linear-gradient(135deg,%20%234f46e5%200%25,%20%232563eb%20100%25);color:white;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center;}h1{font-size:48px;margin:0%200%2020px;}p{font-size:24px;opacity:0.9;margin:10px%200;}.badge{background:rgba(255,255,255,0.2);padding:10px%2020px;border-radius:8px;display:inline-block;margin:20px%200;font-weight:bold;}</style></head><body><div><h1>🎯 Screenshot Tool</h1><div class='badge'>Chrome Ready for Capture</div><p>✅ Remote Debugging: Enabled</p><p>✅ CDP Port: 9222</p><br><p style='font-size:18px;opacity:0.7;'>You can now use Real Browser Mode<br>in the Screenshot Tool app.</p></div></body></html>" \
    > /dev/null 2>&1 &

# Wait a moment for Chrome to start
sleep 2

# Check if Chrome started successfully
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Chrome launched successfully!"
    echo ""
    echo "CDP Endpoint: http://localhost:9222"
    echo ""
    echo "You can now use Real Browser Mode in the Screenshot Tool."
    echo ""
else
    echo "❌ Failed to launch Chrome with remote debugging"
    echo ""
    exit 1
fi

