#!/bin/bash

# Check if Chrome is running with remote debugging enabled

echo "🔍 Checking Chrome Remote Debugging Status..."
echo ""

# Check if port 9222 is in use
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Chrome is running with remote debugging ENABLED!"
    echo ""
    echo "🟢 Status: READY for screenshot tool"
    echo "📡 CDP Endpoint: http://localhost:9222"
    echo ""
    
    # Try to get Chrome version info from CDP
    echo "🔗 Testing connection to Chrome..."
    if command -v curl &> /dev/null; then
        RESPONSE=$(curl -s http://localhost:9222/json/version 2>/dev/null)
        if [ ! -z "$RESPONSE" ]; then
            echo "✅ Connection successful!"
            echo ""
            echo "Chrome Info:"
            echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
            echo ""
        else
            echo "⚠️  Port 9222 is open but couldn't get Chrome info"
            echo ""
        fi
    fi
    
    echo "✅ You can now use the screenshot tool!"
    echo ""
    echo "Next steps:"
    echo "  1. Make sure 'Real Browser' mode is enabled in Settings"
    echo "  2. Enter your URLs and click 'Capture Screenshots'"
    echo ""
    
else
    echo "❌ Chrome is NOT running with remote debugging"
    echo ""
    echo "🔴 Status: NOT READY for screenshot tool"
    echo ""
    
    # Check if Chrome is running at all
    if pgrep -x "Google Chrome" > /dev/null; then
        echo "⚠️  Chrome is running, but WITHOUT remote debugging"
        echo ""
        echo "To fix this:"
        echo "  1. Close Chrome completely (Cmd+Q)"
        echo "  2. Run: cd screenshot-app && ./launch-chrome-debug.sh"
        echo ""
    else
        echo "ℹ️  Chrome is not running at all"
        echo ""
        echo "To start Chrome with remote debugging:"
        echo "  cd screenshot-app && ./launch-chrome-debug.sh"
        echo ""
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Quick Reference:"
echo ""
echo "Check status:        ./check-chrome-debug.sh"
echo "Launch debug Chrome: ./launch-chrome-debug.sh"
echo "Update profile:      ./setup-chrome-profile.sh"
echo ""

