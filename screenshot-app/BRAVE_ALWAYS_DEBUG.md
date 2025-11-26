# 🦁 Brave Browser - Always in Debug Mode

**Goal**: Make Brave ALWAYS launch with CDP enabled (no manual flags needed)

---

## 🎯 Solution: Replace Brave's Launch Behavior

We'll create a wrapper script that intercepts Brave launches and adds CDP flags automatically.

---

## 📋 Method 1: Automator App (Recommended for macOS)

### **Step 1: Create Automator Application**

1. **Open Automator** (Applications → Automator)

2. **Create New Document** → Choose **"Application"**

3. **Add "Run Shell Script" action:**
   - Search for "Run Shell Script" in the left panel
   - Drag it to the right panel

4. **Paste this script:**
```bash
#!/bin/bash

# Kill any existing Brave instances
killall "Brave Browser" 2>/dev/null || true
sleep 1

# Launch Brave with CDP ALWAYS enabled
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/BraveSoftware/Brave-Browser" \
  > /dev/null 2>&1 &

# Show notification
osascript -e 'display notification "Brave launched with CDP on port 9222" with title "🦁 Brave Debug Mode"'
```

5. **Save as:**
   - Name: `Brave Debug`
   - Location: `Applications` folder
   - File Format: Application

6. **Set custom icon (optional):**
   - Right-click original Brave app → Get Info
   - Click the icon in top-left → Copy (⌘C)
   - Right-click "Brave Debug" app → Get Info
   - Click the icon in top-left → Paste (⌘V)

---

### **Step 2: Replace Brave in Dock**

1. **Remove original Brave** from Dock
2. **Add "Brave Debug"** to Dock
3. **Done!** Now clicking Brave always launches with CDP

---

## 📋 Method 2: Shell Alias (For Terminal Users)

### **Add to your shell config:**

**For Zsh (default on macOS):**
```bash
# Edit ~/.zshrc
nano ~/.zshrc

# Add this line:
alias brave='killall "Brave Browser" 2>/dev/null; /Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser --remote-debugging-port=9222 --user-data-dir="$HOME/Library/Application Support/BraveSoftware/Brave-Browser" > /dev/null 2>&1 &'

# Save and reload:
source ~/.zshrc
```

**For Bash:**
```bash
# Edit ~/.bash_profile
nano ~/.bash_profile

# Add this line:
alias brave='killall "Brave Browser" 2>/dev/null; /Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser --remote-debugging-port=9222 --user-data-dir="$HOME/Library/Application Support/BraveSoftware/Brave-Browser" > /dev/null 2>&1 &'

# Save and reload:
source ~/.bash_profile
```

**Now you can launch Brave from terminal:**
```bash
brave
```

---

## 📋 Method 3: LaunchAgent (Auto-start on Login)

### **Create a LaunchAgent that starts Brave with CDP on login:**

**Step 1: Create plist file:**
```bash
nano ~/Library/LaunchAgents/com.brave.debug.plist
```

**Step 2: Paste this content:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.brave.debug</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/Brave Browser.app/Contents/MacOS/Brave Browser</string>
        <string>--remote-debugging-port=9222</string>
        <string>--user-data-dir=/Users/YOUR_USERNAME/Library/Application Support/BraveSoftware/Brave-Browser</string>
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
```

**⚠️ IMPORTANT:** Replace `YOUR_USERNAME` with your actual username!

**Step 3: Load the LaunchAgent:**
```bash
launchctl load ~/Library/LaunchAgents/com.brave.debug.plist
```

**Step 4: Test it:**
```bash
launchctl start com.brave.debug
```

**To disable auto-start:**
```bash
launchctl unload ~/Library/LaunchAgents/com.brave.debug.plist
```

---

## 📋 Method 4: Rename Original Brave (Advanced)

### **⚠️ WARNING: This modifies the original Brave app!**

**Step 1: Backup original Brave:**
```bash
sudo cp -R "/Applications/Brave Browser.app" "/Applications/Brave Browser.app.backup"
```

**Step 2: Create wrapper script:**
```bash
sudo nano "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser.original"
```

**Step 3: Rename original binary:**
```bash
sudo mv "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
         "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser.original"
```

**Step 4: Create new wrapper:**
```bash
sudo nano "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
```

**Paste this:**
```bash
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$DIR/Brave Browser.original" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/BraveSoftware/Brave-Browser" \
  "$@" &
```

**Step 5: Make it executable:**
```bash
sudo chmod +x "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
```

**Now Brave ALWAYS launches with CDP!**

**To restore original:**
```bash
sudo rm "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
sudo mv "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser.original" \
         "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
```

---

## 🎯 Recommended Solution

**For most users: Method 1 (Automator App)**

**Pros:**
- ✅ Safe (doesn't modify original Brave)
- ✅ Easy to create
- ✅ Can have both debug and non-debug versions
- ✅ Easy to remove
- ✅ Works with Dock

**Cons:**
- ❌ Need to use "Brave Debug" app instead of original

---

## ✅ Verification

After setting up any method, verify CDP is working:

```bash
# Check if Brave is running with CDP
curl http://localhost:9222/json/version

# Check process arguments
ps aux | grep "remote-debugging-port"
```

**Expected output:**
```
... --remote-debugging-port=9222 ...
```

---

## 🔧 Troubleshooting

### **Problem: "Profile in use" error**

**Solution:** Make sure to kill existing Brave instances first:
```bash
killall "Brave Browser"
sleep 2
# Then launch again
```

---

### **Problem: Port 9222 already in use**

**Solution:** Check what's using it:
```bash
lsof -i :9222
# Kill the process if needed
```

---

### **Problem: Automator app doesn't work**

**Solution:** Give it permissions:
1. System Preferences → Security & Privacy → Privacy
2. Select "Automation"
3. Find "Brave Debug" and enable permissions

---

## 🎉 Result

After setup, you'll have:
- ✅ Brave ALWAYS launches with CDP enabled
- ✅ No need to remember flags
- ✅ No need to run scripts manually
- ✅ Screenshot tool can ALWAYS connect
- ✅ Port 9222 always available

**Your screenshot tool will work seamlessly with Brave!** 🦁📸

