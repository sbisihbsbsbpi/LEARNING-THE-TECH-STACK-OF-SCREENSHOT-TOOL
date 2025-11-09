#!/bin/bash

# COOKIES ONLY Chrome Profile Setup - ABSOLUTE BARE MINIMUM
# Only copies cookies (2-10 MB total)

echo "🍪 Setting up COOKIES-ONLY Chrome Debug Profile (Absolute Bare Minimum)..."
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
    echo "This ensures all cookies are saved properly."
    echo ""
    exit 1
fi

# Check if debug debug profile already exists
if [ -d "$DEBUG_PROFILE" ]; then
    echo "⚠️  Debug debug profile already exists!"
    echo ""
    read -p "Do you want to delete it and create a fresh copy? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Deleting old debug debug profile..."
        rm -rf "$DEBUG_PROFILE"
        echo "✅ Deleted!"
        echo ""
    else
        echo "❌ Cancelled. Keeping existing profile."
        exit 0
    fi
fi

echo "📋 What will be copied (ABSOLUTE MINIMUM):"
echo "   ✅ Cookies ONLY (active sessions)"
echo ""
echo "📋 What will NOT be copied:"
echo "   ❌ Passwords (you'll need to login manually if sessions expire)"
echo "   ❌ Bookmarks"
echo "   ❌ History"
echo "   ❌ Extensions"
echo "   ❌ Autofill data"
echo "   ❌ Preferences"
echo "   ❌ Cache (5+ GB)"
echo "   ❌ Everything else"
echo ""
echo "💾 Expected size: ~2-10 MB (absolute minimum!)"
echo ""
echo "⚠️  WARNING: If your login sessions expire, you'll need to login manually!"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled."
    exit 0
fi

echo ""
echo "🚀 Creating debug debug profile..."
echo ""

# Create the debug profile directory
mkdir -p "$DEBUG_PROFILE"

# Detect which profile to copy
echo "🔍 Detecting your active Chrome profile..."
echo ""

# List available profiles
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

echo "Found ${#PROFILES[@]} profile(s):"
for i in "${!PROFILES[@]}"; do
    PROFILE_PATH="$MAIN_PROFILE/${PROFILES[$i]}"
    PROFILE_SIZE=$(du -sh "$PROFILE_PATH" 2>/dev/null | cut -f1)
    
    # Try to get email from Preferences
    PROFILE_EMAIL="N/A"
    if [ -f "$PROFILE_PATH/Preferences" ]; then
        PROFILE_EMAIL=$(cat "$PROFILE_PATH/Preferences" | python3 -c "import sys, json; data=json.load(sys.stdin); email=data.get('account_info', [{}])[0].get('email', 'N/A') if data.get('account_info') else 'N/A'; print(email)" 2>/dev/null || echo "N/A")
    fi
    
    echo "  $((i+1)). ${PROFILES[$i]} ($PROFILE_SIZE) - $PROFILE_EMAIL"
done
echo ""

if [ ${#PROFILES[@]} -eq 1 ]; then
    SELECTED_PROFILE="${PROFILES[0]}"
    echo "✅ Auto-selected: $SELECTED_PROFILE"
else
    read -p "Which profile do you use? (1-${#PROFILES[@]}): " PROFILE_NUM
    SELECTED_PROFILE="${PROFILES[$((PROFILE_NUM-1))]}"
    echo "✅ Selected: $SELECTED_PROFILE"
fi

echo ""
echo "📦 Copying ONLY cookies from $SELECTED_PROFILE..."
echo ""

SOURCE_PROFILE="$MAIN_PROFILE/$SELECTED_PROFILE"
DEST_PROFILE="$DEBUG_PROFILE/Default"

mkdir -p "$DEST_PROFILE"

# Copy ONLY cookies
COOKIES_FILES=(
    "Cookies"
    "Cookies-journal"
)

echo "Copying files..."
for file in "${COOKIES_FILES[@]}"; do
    if [ -e "$SOURCE_PROFILE/$file" ]; then
        cp -R "$SOURCE_PROFILE/$file" "$DEST_PROFILE/" 2>/dev/null
        FILE_SIZE=$(ls -lh "$SOURCE_PROFILE/$file" 2>/dev/null | awk '{print $5}')
        echo "  ✅ $file ($FILE_SIZE)"
    else
        echo "  ⚠️  $file (not found - skipping)"
    fi
done

# Create minimal Local State file (required for Chrome to start)
echo ""
echo "Creating minimal Chrome config..."
cat > "$DEBUG_PROFILE/Local State" << 'EOF'
{
   "browser": {
      "enabled_labs_experiments": []
   }
}
EOF
echo "  ✅ Minimal config created"

# Create minimal First Run file
touch "$DEBUG_PROFILE/First Run"

echo ""
echo "✅ Debug debug profile created successfully!"
echo ""

# Check final size
FINAL_SIZE=$(du -sh "$DEBUG_PROFILE" 2>/dev/null | cut -f1)
echo "📊 Final size: $FINAL_SIZE"
echo ""
echo "📁 Location: $DEBUG_PROFILE"
echo ""
echo "🎉 Done! Now you can launch Chrome with:"
echo "   ./launch-chrome-debug-debug.sh"
echo ""
echo "💡 This profile has:"
echo "   ✅ Your login sessions (cookies) ONLY"
echo "   ❌ NO passwords (manual login if sessions expire)"
echo "   ❌ Nothing else (absolute minimum!)"
echo ""
echo "⚠️  If your sessions expire, you'll need to:"
echo "   1. Login manually in the debug Chrome"
echo "   2. Or re-run this script to get fresh cookies"
echo ""

