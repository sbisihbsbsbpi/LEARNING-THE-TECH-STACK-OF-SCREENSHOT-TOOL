#!/bin/bash

# Create macOS App Bundle for Screenshot Tool
# This creates a clickable .app that opens the tool in Chrome

echo "🚀 Creating macOS App Bundle..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# App name
APP_NAME="Screenshot Tool"
APP_DIR="$SCRIPT_DIR/${APP_NAME}.app"

# Remove old app if exists
if [ -d "$APP_DIR" ]; then
    echo "🗑️  Removing old app..."
    rm -rf "$APP_DIR"
fi

# Create app bundle structure
echo "📦 Creating app structure..."
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Create the launcher script
echo "📝 Creating launcher script..."
cat > "$APP_DIR/Contents/MacOS/launch" << 'EOF'
#!/bin/bash

# Get the app directory
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd ../.. && pwd )"
PROJECT_DIR="$(dirname "$APP_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Run the launch script
bash launch-app.sh
EOF

# Make launcher executable
chmod +x "$APP_DIR/Contents/MacOS/launch"

# Create Info.plist
echo "📝 Creating Info.plist..."
cat > "$APP_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleIdentifier</key>
    <string>com.tlreddy.screenshot-tool</string>
    <key>CFBundleName</key>
    <string>Screenshot Tool</string>
    <key>CFBundleDisplayName</key>
    <string>Screenshot Tool</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Copy icon if exists
if [ -f "frontend/src-tauri/icons/icon.icns" ]; then
    echo "🎨 Copying icon..."
    cp "frontend/src-tauri/icons/icon.icns" "$APP_DIR/Contents/Resources/icon.icns"
else
    echo "⚠️  No icon found, app will use default icon"
fi

echo ""
echo "✅ macOS App created successfully!"
echo ""
echo "📍 Location: $APP_DIR"
echo ""
echo "🎯 To use:"
echo "   1. Double-click 'Screenshot Tool.app'"
echo "   2. App will open in Chrome browser"
echo "   3. Close the terminal window to stop the app"
echo ""
echo "💡 Tip: Drag 'Screenshot Tool.app' to your Applications folder or Dock!"
echo ""

