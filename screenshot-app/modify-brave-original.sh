#!/bin/bash

# 🦁 Modify Original Brave to ALWAYS Launch in Debug Mode
# This script modifies /Applications/Brave Browser.app to always use CDP

echo "🦁 Modify Original Brave Browser"
echo "================================="
echo ""
echo "⚠️  WARNING: This will modify the original Brave Browser app!"
echo ""
echo "What this does:"
echo "  - Renames the original Brave executable to 'Brave Browser.original'"
echo "  - Creates a wrapper script that adds --remote-debugging-port=9222"
echo "  - Brave will ALWAYS launch with CDP enabled"
echo ""
echo "Backup:"
echo "  - Original executable will be saved as 'Brave Browser.original'"
echo "  - You can restore it anytime"
echo ""
read -p "Continue? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ Cancelled"
    exit 0
fi

# Check if Brave is installed
BRAVE_APP="/Applications/Brave Browser.app"
BRAVE_EXEC="$BRAVE_APP/Contents/MacOS/Brave Browser"
BRAVE_ORIGINAL="$BRAVE_APP/Contents/MacOS/Brave Browser.original"

if [ ! -d "$BRAVE_APP" ]; then
    echo ""
    echo "❌ Error: Brave Browser not found at: $BRAVE_APP"
    exit 1
fi

if [ ! -f "$BRAVE_EXEC" ]; then
    echo ""
    echo "❌ Error: Brave executable not found at: $BRAVE_EXEC"
    exit 1
fi

# Check if already modified
if [ -f "$BRAVE_ORIGINAL" ]; then
    echo ""
    echo "⚠️  Brave appears to be already modified!"
    echo "   Found: $BRAVE_ORIGINAL"
    echo ""
    read -p "Re-apply modification? (y/n): " reapply
    if [ "$reapply" != "y" ] && [ "$reapply" != "Y" ]; then
        echo "❌ Cancelled"
        exit 0
    fi
    # Restore original first
    echo "🔄 Restoring original executable..."
    sudo mv "$BRAVE_ORIGINAL" "$BRAVE_EXEC"
fi

# Kill any running Brave instances
echo ""
echo "🔄 Closing all Brave instances..."
killall "Brave Browser" 2>/dev/null || true
sleep 2

# Rename original executable
echo "📝 Renaming original executable..."
sudo mv "$BRAVE_EXEC" "$BRAVE_ORIGINAL"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to rename original executable"
    echo "   You may need to run with sudo"
    exit 1
fi

# Create wrapper script
echo "📝 Creating wrapper script..."
sudo tee "$BRAVE_EXEC" > /dev/null << 'EOF'
#!/bin/bash

# Brave Browser Debug Mode Wrapper
# This script launches Brave with CDP always enabled

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Launch the original Brave executable with debug flags
exec "$DIR/Brave Browser.original" \
	  --remote-debugging-address=127.0.0.1 \
	  --remote-debugging-port=9222 \
	  --user-data-dir="$HOME/Library/Application Support/BraveSoftware/Brave-Browser" \
	  "$@"
EOF

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to create wrapper script"
    echo "   Restoring original..."
    sudo mv "$BRAVE_ORIGINAL" "$BRAVE_EXEC"
    exit 1
fi

# Make wrapper executable
echo "🔧 Making wrapper executable..."
sudo chmod +x "$BRAVE_EXEC"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to make wrapper executable"
    echo "   Restoring original..."
    sudo rm "$BRAVE_EXEC"
    sudo mv "$BRAVE_ORIGINAL" "$BRAVE_EXEC"
    exit 1
fi

echo ""
echo "✅ SUCCESS! Original Brave Browser is now in debug mode!"
echo ""
echo "📋 What changed:"
echo "   Original: $BRAVE_ORIGINAL"
echo "   Wrapper:  $BRAVE_EXEC"
echo ""
echo "🎯 From now on:"
echo "   - Clicking Brave Browser ALWAYS launches with CDP"
echo "   - Port 9222 will always be available"
echo "   - No need to run scripts or remember flags"
echo ""
echo "🔗 Verify CDP: http://localhost:9222/json/version"
echo ""
echo "To restore original Brave:"
echo "   sudo mv \"$BRAVE_ORIGINAL\" \"$BRAVE_EXEC\""
echo ""

# Ask if user wants to launch Brave now
read -p "Launch Brave now to test? (y/n): " launch

if [ "$launch" = "y" ] || [ "$launch" = "Y" ]; then
    echo ""
    echo "🚀 Launching Brave..."
    open "$BRAVE_APP"
    
    echo "⏳ Waiting for Brave to start..."
    sleep 5
    
    echo "🔍 Verifying CDP..."
    if curl -s http://localhost:9222/json/version > /dev/null 2>&1; then
        echo ""
        echo "✅ CDP is working!"
        echo ""
        curl -s http://localhost:9222/json/version | python3 -m json.tool 2>/dev/null || curl -s http://localhost:9222/json/version
    else
        echo ""
        echo "⚠️  CDP not responding yet. Wait a few more seconds and try:"
        echo "   curl http://localhost:9222/json/version"
    fi
fi

echo ""
echo "🎉 Setup complete!"

