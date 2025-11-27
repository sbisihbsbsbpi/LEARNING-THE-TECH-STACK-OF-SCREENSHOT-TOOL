#!/bin/bash

# Launch Chrome with Remote Debugging using COOKIES-ONLY profile (absolute bare minimum)

echo "🚀 Launching Chrome with Remote Debugging (Debug Profile)..."
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
    echo "Please close Chrome completely (Cmd+Q) and run this script again."
    echo ""
    exit 1
fi

# Use Chrome Debug Cookies-Only profile
CHROME_PROFILE="$HOME/Library/Application Support/Google/Chrome-Debug"

# Check if debug debug profile exists
if [ ! -d "$CHROME_PROFILE" ]; then
    echo "⚠️  Debug debug profile not found!"
    echo ""
    echo "You need to set up the debug debug profile first (one-time setup):"
    echo "  ./setup-chrome-profile-debug.sh"
    echo ""
    echo "This will create a minimal profile (~2-10 MB) with only cookies."
    echo ""
    exit 1
fi

echo "Launching Chrome with:"
echo "  ✅ Remote debugging on port 9222"
echo "  ✅ Debug debug profile (absolute bare minimum: cookies ONLY)"
echo "  ✅ Red startup page (so you know it's debug mode)"
echo ""

# Launch Chrome with remote debugging using debug debug profile
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
	    --remote-debugging-address=127.0.0.1 \
	    --remote-debugging-port=9222 \
	    --user-data-dir="$CHROME_PROFILE" \
	    --new-window \
    "data:text/html,<html><head><title>🍪 COOKIES-ONLY CHROME - Screenshot Tool</title><style>body{margin:0;padding:40px;font-family:system-ui;background:linear-gradient(135deg,%20%23dc2626%200%25,%20%23991b1b%20100%25);color:white;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center;}h1{font-size:48px;margin:0%200%2020px;}p{font-size:24px;opacity:0.9;margin:10px%200;}.badge{background:rgba(255,255,255,0.2);padding:10px%2020px;border-radius:8px;display:inline-block;margin:20px%200;font-weight:bold;}</style></head><body><div><h1>🍪 COOKIES-ONLY CHROME</h1><div class='badge'>Absolute Bare Minimum - Screenshot Tool Mode</div><p>✅ Remote Debugging: Enabled</p><p>✅ Cookies: Available</p><p>❌ Passwords: NOT Available</p><p>💾 Profile Size: ~2-10 MB (absolute minimum!)</p><br><p style='font-size:18px;opacity:0.7;'>This is your debug debug Chrome instance.<br>Only cookies, nothing else.<br>Manual login required if sessions expire.</p></div></body></html>" \
    > /dev/null 2>&1 &

# Wait a moment for Chrome to start
sleep 2

# Check if Chrome started successfully
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Chrome launched successfully with debug debug profile!"
    echo ""
    echo "🔴 LOOK FOR THE RED PAGE - That's your debug debug Chrome!"
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
    echo "💡 Your login cookies are available (sessions will work if not expired)"
    echo ""
    echo "⚠️  If sessions expire, you'll need to login manually (no saved passwords)"
    echo ""
    echo "🔍 How to tell which Chrome is which:"
    echo "   🔴 Red startup page = Cookies-Only Debug Chrome (2-10 MB, absolute minimum)"
    echo "   🟠 Orange startup page = Skeleton Debug Chrome (3-11 MB, cookies + passwords)"
    echo "   🟢 Green/cyan startup page = Clean Debug Chrome (100-500 MB)"
    echo "   🟣 Purple startup page = Old Debug Chrome (20 GB version)"
    echo "   ⚪ Normal pages = Regular Chrome (for browsing)"
    echo ""
    echo "📝 Note: This is debug. To update cookies, run:"
    echo "   ./setup-chrome-profile-debug.sh"
    echo ""
else
    echo "❌ Failed to launch Chrome with remote debugging"
    echo ""
    echo "Please try manually:"
	    echo "  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 --user-data-dir=\"$CHROME_PROFILE\""
    echo ""
    exit 1
fi

