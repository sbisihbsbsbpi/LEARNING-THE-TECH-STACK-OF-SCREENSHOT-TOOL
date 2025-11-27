#!/bin/bash

# 🦁 Brave Browser - Always Debug Mode Setup
# This script creates a "Brave Debug" app that ALWAYS launches with CDP enabled

echo "🦁 Brave Always-Debug Setup"
echo "============================"
echo ""

# Check if Brave is installed
BRAVE_PATH="/Applications/Brave Browser.app"
if [ ! -d "$BRAVE_PATH" ]; then
    echo "❌ Error: Brave Browser not found at: $BRAVE_PATH"
    echo ""
    echo "Please install Brave Browser from: https://brave.com/download/"
    exit 1
fi

echo "✅ Brave Browser found"
echo ""

# Show options
echo "Choose setup method:"
echo ""
echo "1) Create 'Brave Debug' app (Recommended)"
echo "   - Safe, doesn't modify original Brave"
echo "   - You'll have both regular Brave and Brave Debug"
echo "   - Can add Brave Debug to Dock"
echo ""
echo "2) Create shell alias (for terminal users)"
echo "   - Launch Brave from terminal with 'brave' command"
echo "   - Doesn't affect clicking Brave icon"
echo ""
echo "3) Create LaunchAgent (auto-start on login)"
echo "   - Brave with CDP starts automatically when you login"
echo "   - Always running in background"
echo ""
read -p "Enter choice (1, 2, or 3): " choice

if [ "$choice" = "1" ]; then
    # Method 1: Create Automator App
    echo ""
    echo "📱 Creating 'Brave Debug' application..."
    echo ""
    
    APP_PATH="$HOME/Applications/Brave Debug.app"
    
    # Create app bundle structure
    mkdir -p "$APP_PATH/Contents/MacOS"
    mkdir -p "$APP_PATH/Contents/Resources"
    
    # Create Info.plist
    cat > "$APP_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>brave-debug-launcher</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.brave.debug</string>
    <key>CFBundleName</key>
    <string>Brave Debug</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
</dict>
</plist>
EOF
    
    # Create launcher script
    cat > "$APP_PATH/Contents/MacOS/brave-debug-launcher" << 'EOF'
#!/bin/bash

# Kill any existing Brave instances
killall "Brave Browser" 2>/dev/null || true
sleep 2

# Launch Brave with CDP ALWAYS enabled
# Note: We don't background it (&) so the app stays running
exec /Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser \
  --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/BraveSoftware/Brave-Browser"
EOF
    
    # Make launcher executable
    chmod +x "$APP_PATH/Contents/MacOS/brave-debug-launcher"
    
    # Try to copy Brave's icon
    if [ -f "/Applications/Brave Browser.app/Contents/Resources/app.icns" ]; then
        cp "/Applications/Brave Browser.app/Contents/Resources/app.icns" \
           "$APP_PATH/Contents/Resources/AppIcon.icns"
    fi
    
    echo "✅ 'Brave Debug' app created at: $APP_PATH"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Open Finder → Applications"
    echo "   2. Find 'Brave Debug' app"
    echo "   3. Drag it to your Dock"
    echo "   4. Click it to launch Brave with CDP!"
    echo ""
    echo "🔗 Verify CDP: http://localhost:9222/json/version"
    echo ""
    
    # Ask if user wants to open Applications folder
    read -p "Open Applications folder now? (y/n): " open_apps
    if [ "$open_apps" = "y" ] || [ "$open_apps" = "Y" ]; then
        open "$HOME/Applications"
    fi

elif [ "$choice" = "2" ]; then
    # Method 2: Shell Alias
    echo ""
    echo "🐚 Creating shell alias..."
    echo ""
    
    # Detect shell
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
        SHELL_NAME="zsh"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bash_profile"
        SHELL_NAME="bash"
    else
        echo "⚠️  Could not detect shell type"
        echo "Please manually add this to your shell config:"
        echo ""
	        echo "alias brave='killall \"Brave Browser\" 2>/dev/null; /Applications/Brave\\ Browser.app/Contents/MacOS/Brave\\ Browser --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 --user-data-dir=\"\$HOME/Library/Application Support/BraveSoftware/Brave-Browser\" > /dev/null 2>&1 &'"
        exit 0
    fi
    
    # Check if alias already exists
    if grep -q "alias brave=" "$SHELL_RC" 2>/dev/null; then
        echo "⚠️  Alias 'brave' already exists in $SHELL_RC"
        echo ""
        read -p "Replace it? (y/n): " replace
        if [ "$replace" != "y" ] && [ "$replace" != "Y" ]; then
            echo "❌ Cancelled"
            exit 0
        fi
        # Remove old alias
        sed -i.bak '/alias brave=/d' "$SHELL_RC"
    fi
    
    # Add alias
    echo "" >> "$SHELL_RC"
	    echo "# Brave Browser with CDP (added by setup script)" >> "$SHELL_RC"
	    echo "alias brave='killall \"Brave Browser\" 2>/dev/null; /Applications/Brave\\ Browser.app/Contents/MacOS/Brave\\ Browser --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 --user-data-dir=\"\$HOME/Library/Application Support/BraveSoftware/Brave-Browser\" > /dev/null 2>&1 &'" >> "$SHELL_RC"
    
    echo "✅ Alias added to $SHELL_RC"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Reload your shell: source $SHELL_RC"
    echo "   2. Launch Brave from terminal: brave"
    echo ""
    echo "🔗 Verify CDP: curl http://localhost:9222/json/version"
    echo ""
    
    # Ask if user wants to reload shell
    read -p "Reload shell now? (y/n): " reload
    if [ "$reload" = "y" ] || [ "$reload" = "Y" ]; then
        source "$SHELL_RC"
        echo "✅ Shell reloaded"
        echo ""
        echo "You can now run: brave"
    fi

elif [ "$choice" = "3" ]; then
    # Method 3: LaunchAgent
    echo ""
    echo "🚀 Creating LaunchAgent..."
    echo ""
    
    PLIST_PATH="$HOME/Library/LaunchAgents/com.brave.debug.plist"
    
    # Check if LaunchAgent already exists
    if [ -f "$PLIST_PATH" ]; then
        echo "⚠️  LaunchAgent already exists at: $PLIST_PATH"
        echo ""
        read -p "Replace it? (y/n): " replace
        if [ "$replace" != "y" ] && [ "$replace" != "Y" ]; then
            echo "❌ Cancelled"
            exit 0
        fi
        # Unload existing
        launchctl unload "$PLIST_PATH" 2>/dev/null || true
    fi
    
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "$HOME/Library/LaunchAgents"
    
    # Get username for path
    USERNAME=$(whoami)
    
	    # Create plist
	    cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.brave.debug</string>
    
	    <key>ProgramArguments</key>
	    <array>
	        <string>/Applications/Brave Browser.app/Contents/MacOS/Brave Browser</string>
	        <string>--remote-debugging-address=127.0.0.1</string>
	        <string>--remote-debugging-port=9222</string>
	        <string>--user-data-dir=/Users/$USERNAME/Library/Application Support/BraveSoftware/Brave-Browser</string>
	    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <false/>
    
    <key>StandardOutPath</key>
    <string>/tmp/brave-debug.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/brave-debug-error.log</string>
</dict>
</plist>
EOF
    
    # Load LaunchAgent
    launchctl load "$PLIST_PATH"
    
    echo "✅ LaunchAgent created and loaded"
    echo ""
    echo "📋 Brave will now:"
    echo "   - Start automatically when you login"
    echo "   - Always run with CDP on port 9222"
    echo ""
    echo "🔗 Verify CDP: curl http://localhost:9222/json/version"
    echo ""
    echo "To disable auto-start:"
    echo "   launchctl unload $PLIST_PATH"
    echo ""
    
    # Ask if user wants to start now
    read -p "Start Brave now? (y/n): " start_now
    if [ "$start_now" = "y" ] || [ "$start_now" = "Y" ]; then
        launchctl start com.brave.debug
        sleep 2
        echo "✅ Brave started"
    fi

else
    echo "❌ Invalid choice"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Your screenshot tool can now connect to Brave at:"
echo "   http://localhost:9222"
echo ""

