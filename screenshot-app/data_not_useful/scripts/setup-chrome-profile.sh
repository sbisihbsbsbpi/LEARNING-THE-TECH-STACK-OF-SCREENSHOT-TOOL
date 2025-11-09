#!/bin/bash

# Setup Chrome Debug Profile with your logins and cookies
# This is a ONE-TIME setup that copies your main Chrome profile

echo "🔧 Chrome Debug Profile Setup"
echo ""

MAIN_PROFILE="$HOME/Library/Application Support/Google/Chrome"
DEBUG_PROFILE="$HOME/Library/Application Support/Google/Chrome-Debug"

# Check if main profile exists
if [ ! -d "$MAIN_PROFILE" ]; then
    echo "❌ Main Chrome profile not found at:"
    echo "   $MAIN_PROFILE"
    echo ""
    echo "Please make sure Chrome is installed and you've used it at least once."
    exit 1
fi

# Check if debug profile already exists
if [ -d "$DEBUG_PROFILE" ]; then
    echo "⚠️  Debug profile already exists at:"
    echo "   $DEBUG_PROFILE"
    echo ""
    read -p "Do you want to update it with your current logins? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing debug profile."
        exit 0
    fi
    echo ""
    echo "Updating debug profile..."
    rm -rf "$DEBUG_PROFILE"
fi

# Check if Chrome is running
if pgrep -x "Google Chrome" > /dev/null; then
    echo "⚠️  Chrome is currently running!"
    echo ""
    echo "Please close Chrome completely (Cmd+Q) before running this setup."
    echo "This ensures all your data is properly saved and copied."
    echo ""
    exit 1
fi

echo "📋 Copying your Chrome profile to debug profile..."
echo "   This includes all your logins, cookies, and extensions"
echo "   (This may take a minute...)"
echo ""

# Copy the profile (exclude lock files and sockets)
rsync -a --exclude='SingletonLock' --exclude='SingletonSocket' --exclude='SingletonCookie' --exclude='RunningChromeVersion' "$MAIN_PROFILE/" "$DEBUG_PROFILE/"

if [ $? -eq 0 ]; then
    echo "✅ Debug profile created successfully!"
    echo ""
    echo "📁 Location: $DEBUG_PROFILE"
    echo ""
    echo "Now you can use Active Tab Mode with all your logins!"
    echo ""
    echo "Next steps:"
    echo "  1. Run: ./launch-chrome-debug.sh"
    echo "  2. Chrome will open with all your logins"
    echo "  3. Use the screenshot tool with 'Real Browser' mode"
    echo ""
else
    echo "❌ Failed to copy profile"
    exit 1
fi

