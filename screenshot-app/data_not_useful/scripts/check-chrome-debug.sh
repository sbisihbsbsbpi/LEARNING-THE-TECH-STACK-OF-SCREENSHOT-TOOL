#!/bin/bash

# Check if Chrome is running with remote debugging enabled

echo "🔍 Checking Chrome Remote Debugging Status..."
echo ""

# Check if port 9222 is listening
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Chrome is running with remote debugging on port 9222"
    echo ""
    
    # Try to get the CDP endpoint info
    if command -v curl >/dev/null 2>&1; then
        echo "📡 CDP Endpoint Info:"
        curl -s http://localhost:9222/json/version | python3 -m json.tool 2>/dev/null || echo "http://localhost:9222"
        echo ""
    fi
    
    echo "✅ Active Tab Mode is ready to use!"
    echo ""
    echo "Next steps:"
    echo "  1. Open the screenshot tool"
    echo "  2. Enable 'Real Browser' mode in Settings"
    echo "  3. Enter URLs and click 'Capture Screenshots'"
    echo ""
    exit 0
else
    echo "❌ Chrome is NOT running with remote debugging"
    echo ""
    echo "To fix this, run:"
    echo "  ./launch-chrome-debug.sh"
    echo ""
    exit 1
fi

