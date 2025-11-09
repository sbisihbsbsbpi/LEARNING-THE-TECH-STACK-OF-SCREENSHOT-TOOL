#!/bin/bash

# Launch Chrome with Remote Debugging enabled for Active Tab Mode
# This allows the screenshot tool to connect to your existing Chrome browser

echo "🚀 Launching Chrome with Remote Debugging..."
echo ""

# Check if port 9222 is already in use
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Chrome is already running with remote debugging on port 9222!"
    echo ""
    echo "CDP Endpoint: http://localhost:9222"
    echo ""
    echo "You can now use Active Tab Mode in the screenshot tool."
    echo ""
    exit 0
fi

# Check if Chrome is already running (without debugging)
if pgrep -x "Google Chrome" > /dev/null; then
    echo "⚠️  Chrome is already running (without remote debugging)!"
    echo ""
    echo "To use your existing Chrome with all your logins and cookies:"
    echo ""
    echo "1. Close Chrome completely (Cmd+Q)"
    echo "2. Run this script again"
    echo "3. Chrome will reopen with your normal profile + remote debugging"
    echo ""
    exit 1
fi

# Use Chrome Debug profile (copy of your main profile with all logins)
CHROME_PROFILE="$HOME/Library/Application Support/Google/Chrome-Debug"

# Check if debug profile exists
if [ ! -d "$CHROME_PROFILE" ]; then
    echo "⚠️  Debug profile not found!"
    echo ""
    echo "You need to set up the debug profile first (one-time setup):"
    echo "  ./setup-chrome-profile.sh"
    echo ""
    echo "This will copy your main Chrome profile (with all logins) to a debug profile."
    echo ""
    exit 1
fi

echo "Launching Chrome with:"
echo "  ✅ Remote debugging on port 9222"
echo "  ✅ Debug profile (copy of your main profile with all logins)"
echo "  ✅ Visible window"
echo ""

# Launch Chrome with remote debugging using debug profile
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$CHROME_PROFILE" \
    > /dev/null 2>&1 &

# Wait a moment for Chrome to start
sleep 2

# Check if Chrome started successfully
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Chrome launched successfully with debug profile!"
    echo ""
    echo "CDP Endpoint: http://localhost:9222"
    echo ""
    echo "Now you can:"
    echo "  1. Open any tab you want in Chrome (or let it restore your tabs)"
    echo "  2. Enable 'Real Browser' mode in the screenshot tool"
    echo "  3. Enter your URLs and click 'Capture Screenshots'"
    echo "  4. Watch as URLs load in your active Chrome tab!"
    echo ""
    echo "💡 The tool will use whichever tab is currently active in Chrome"
    echo "💡 All your logins and cookies from your main profile are available!"
    echo ""
    echo "📝 Note: This is a copy of your main profile. To update logins, run:"
    echo "   ./setup-chrome-profile.sh"
    echo ""
else
    echo "❌ Failed to launch Chrome with remote debugging"
    echo ""
    echo "Please try manually:"
    echo "  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=\"$CHROME_PROFILE\""
    echo ""
    exit 1
fi

