#!/bin/bash

# Setup ALL Chrome Profiles with Essential Data Only
# Copies: Cookies, Login Data, Bookmarks, Visited Links from ALL profiles

echo "🔧 Setting up ALL Chrome Profiles with Essential Data..."
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

# Check if Chrome is running
if pgrep -x "Google Chrome" > /dev/null; then
    echo "⚠️  Chrome is currently running!"
    echo ""
    echo "Please close Chrome completely (Cmd+Q) before running this script."
    echo "This ensures all data is saved properly."
    echo ""
    exit 1
fi

# Check if debug profile already exists
if [ -d "$DEBUG_PROFILE" ]; then
    echo "⚠️  Debug profile already exists!"
    echo ""
    read -p "Do you want to delete it and create a fresh copy? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Deleting old debug profile..."
        rm -rf "$DEBUG_PROFILE"
        echo "✅ Deleted!"
        echo ""
    else
        echo "❌ Cancelled. Keeping existing profile."
        exit 0
    fi
fi

echo "📋 What will be copied from ALL profiles:"
echo "   ✅ Cookies (login sessions)"
echo "   ✅ Login Data (saved passwords)"
echo "   ✅ Bookmarks"
echo "   ✅ Visited Links"
echo ""
echo "📋 What will NOT be copied:"
echo "   ❌ History"
echo "   ❌ Extensions"
echo "   ❌ Cache (5+ GB)"
echo "   ❌ Service Workers"
echo "   ❌ WebStorage"
echo "   ❌ Everything else"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled."
    exit 0
fi

echo ""
echo "🚀 Creating debug profile with ALL profiles..."
echo ""

# Create the debug profile directory
mkdir -p "$DEBUG_PROFILE"

# Find all profiles
PROFILES=()
if [ -d "$MAIN_PROFILE/Default" ]; then
    PROFILES+=("Default")
fi
for i in {1..20}; do
    if [ -d "$MAIN_PROFILE/Profile $i" ]; then
        PROFILES+=("Profile $i")
    fi
done

if [ ${#PROFILES[@]} -eq 0 ]; then
    echo "❌ No Chrome profiles found!"
    exit 1
fi

echo "Found ${#PROFILES[@]} profile(s) to copy:"
for profile in "${PROFILES[@]}"; do
    PROFILE_PATH="$MAIN_PROFILE/$profile"
    PROFILE_SIZE=$(du -sh "$PROFILE_PATH" 2>/dev/null | cut -f1)
    
    # Try to get email from Preferences
    PROFILE_EMAIL="N/A"
    if [ -f "$PROFILE_PATH/Preferences" ]; then
        PROFILE_EMAIL=$(cat "$PROFILE_PATH/Preferences" | python3 -c "import sys, json; data=json.load(sys.stdin); email=data.get('account_info', [{}])[0].get('email', 'N/A') if data.get('account_info') else 'N/A'; print(email)" 2>/dev/null || echo "N/A")
    fi
    
    echo "  📁 $profile ($PROFILE_SIZE) - $PROFILE_EMAIL"
done
echo ""

# Essential files to copy
ESSENTIAL_FILES=(
    "Cookies"
    "Cookies-journal"
    "Login Data"
    "Login Data-journal"
    "Bookmarks"
    "Bookmarks.bak"
    "Visited Links"
)

TOTAL_COPIED=0

# Copy each profile
for profile in "${PROFILES[@]}"; do
    echo "📦 Copying $profile..."
    
    SOURCE_PROFILE="$MAIN_PROFILE/$profile"
    DEST_PROFILE="$DEBUG_PROFILE/$profile"
    
    mkdir -p "$DEST_PROFILE"
    
    # Copy essential files
    for file in "${ESSENTIAL_FILES[@]}"; do
        if [ -e "$SOURCE_PROFILE/$file" ]; then
            cp -R "$SOURCE_PROFILE/$file" "$DEST_PROFILE/" 2>/dev/null
            FILE_SIZE=$(ls -lh "$SOURCE_PROFILE/$file" 2>/dev/null | awk '{print $5}')
            echo "  ✅ $file ($FILE_SIZE)"
            TOTAL_COPIED=$((TOTAL_COPIED + 1))
        fi
    done
    
    # Copy Preferences (needed for Chrome to recognize the profile)
    if [ -f "$SOURCE_PROFILE/Preferences" ]; then
        cp "$SOURCE_PROFILE/Preferences" "$DEST_PROFILE/" 2>/dev/null
        echo "  ✅ Preferences"
    fi
    
    echo ""
done

# Copy Local State from main Chrome profile (contains all profile info)
echo "Copying Chrome config with all profile information..."
if [ -f "$MAIN_PROFILE/Local State" ]; then
    cp "$MAIN_PROFILE/Local State" "$DEBUG_PROFILE/Local State"
    echo "  ✅ Chrome config copied (includes all profile info)"
else
    # Fallback: Create minimal Local State if main one doesn't exist
    cat > "$DEBUG_PROFILE/Local State" << 'EOF'
{
   "browser": {
      "enabled_labs_experiments": [],
      "check_default_browser": false
   },
   "profile": {
      "info_cache": {}
   }
}
EOF
    echo "  ✅ Chrome config created (minimal)"
fi

# Create First Run file
touch "$DEBUG_PROFILE/First Run"

# Create launcher in the debug profile folder
cat > "$DEBUG_PROFILE/🔴 CLICK HERE TO LAUNCH DEBUG CHROME.command" << 'LAUNCHER'
#!/bin/bash

echo "🔴 DEBUG CHROME LAUNCHER"
echo "======================="
echo ""

# Check if Chrome is running
if pgrep -x "Google Chrome" > /dev/null; then
    echo "⚠️  Chrome is currently running."
    echo ""
    echo "Closing Chrome in 3 seconds..."
    echo "3..."
    sleep 1
    echo "2..."
    sleep 1
    echo "1..."
    sleep 1
    
    # Close Chrome
    osascript -e 'quit app "Google Chrome"'
    
    echo "✅ Chrome closed!"
    echo ""
    echo "Waiting 2 seconds for Chrome to fully quit..."
    sleep 2
fi

# Launch Debug Chrome
echo "🚀 Launching Debug Chrome with Remote Debugging..."
echo ""

CHROME_PROFILE="$HOME/Library/Application Support/Google/Chrome-Debug"

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
	    --remote-debugging-address=127.0.0.1 \
	    --remote-debugging-port=9222 \
	    --user-data-dir="$CHROME_PROFILE" \
	    --new-window \
    "data:text/html,<html><head><title>🔴 DEBUG CHROME - All Profiles</title><style>body{margin:0;padding:40px;font-family:system-ui;background:linear-gradient(135deg,%20%23dc2626%200%25,%20%23991b1b%20100%25);color:white;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center;}h1{font-size:48px;margin:0%200%2020px;}p{font-size:24px;opacity:0.9;margin:10px%200;}.badge{background:rgba(255,255,255,0.2);padding:10px%2020px;border-radius:8px;display:inline-block;margin:20px%200;font-weight:bold;}</style></head><body><div><h1>🔴 DEBUG CHROME</h1><div class='badge'>All Profiles - Screenshot Tool Mode</div><p>✅ Remote Debugging: Enabled</p><p>✅ All Your Profiles: Available</p><p>✅ Cookies + Passwords + Bookmarks: Available</p><br><p style='font-size:18px;opacity:0.7;'>This is your debug Chrome with all profiles.<br>Switch profiles from Chrome menu.</p></div></body></html>" \
    > /dev/null 2>&1 &

sleep 2

# Check if Chrome started successfully
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Chrome launched successfully!"
    echo ""
    echo "🔴 LOOK FOR THE RED PAGE - That's your debug Chrome!"
    echo ""
    echo "CDP Endpoint: http://localhost:9222"
    echo ""
    echo "You can now:"
    echo "  1. Switch between profiles using Chrome's profile menu"
    echo "  2. Use the screenshot tool with 'Real Browser' mode"
    echo "  3. All your logins and bookmarks are available!"
    echo ""
else
    echo "❌ Failed to launch Chrome with remote debugging"
fi

echo ""
echo "Press any key to close this window..."
read -n 1
LAUNCHER

chmod +x "$DEBUG_PROFILE/🔴 CLICK HERE TO LAUNCH DEBUG CHROME.command"

# Create README
cat > "$DEBUG_PROFILE/README.txt" << 'README'
🔴 DEBUG CHROME PROFILE - ALL PROFILES
======================================

This debug profile contains ALL your Chrome profiles with essential data.

📋 What's Inside:
   ✅ Cookies (login sessions)
   ✅ Login Data (saved passwords)
   ✅ Bookmarks
   ✅ Visited Links
   ❌ NO history
   ❌ NO extensions
   ❌ NO cache

🚀 How to Launch:
   Double-click: 🔴 CLICK HERE TO LAUNCH DEBUG CHROME.command

🔄 Switch Profiles:
   Click your profile icon in Chrome's top-right corner

⚠️  DO NOT DELETE THIS FOLDER!
   The screenshot tool needs this profile to work.

📝 To Update:
   Re-run: ./setup-all-chrome-profiles.sh

🔗 Location:
   ~/Library/Application Support/Google/Chrome-Debug
README

echo ""
echo "✅ All profiles copied successfully!"
echo ""

# Check final size
FINAL_SIZE=$(du -sh "$DEBUG_PROFILE" 2>/dev/null | cut -f1)
echo "📊 Final size: $FINAL_SIZE"
echo "📁 Location: $DEBUG_PROFILE"
echo "📄 Files copied: $TOTAL_COPIED"
echo ""
echo "🎉 Done!"
echo ""
echo "To launch debug Chrome:"
echo "  1. Open: $DEBUG_PROFILE"
echo "  2. Double-click: 🔴 CLICK HERE TO LAUNCH DEBUG CHROME.command"
echo ""
echo "Or run from terminal:"
echo "  open '$DEBUG_PROFILE/🔴 CLICK HERE TO LAUNCH DEBUG CHROME.command'"
echo ""

