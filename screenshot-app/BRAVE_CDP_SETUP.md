# 🦁 Brave Browser CDP Setup Guide

**Date**: November 10, 2025  
**Purpose**: Enable Chrome DevTools Protocol (CDP) for Brave Browser  
**Status**: ✅ Ready to Use

---

## 🎯 What is CDP Mode?

**CDP (Chrome DevTools Protocol)** allows your screenshot tool to connect to and control an existing Brave browser instance.

**Benefits:**
- ✅ Use your existing Brave sessions (already logged in)
- ✅ Extract cookies from Brave automatically
- ✅ See what's happening in real-time
- ✅ Better for debugging
- ✅ Reuse authentication across captures

---

## 🚀 Quick Start

### **Step 1: Launch Brave with Remote Debugging**

**macOS:**
```bash
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/brave-debug-profile"
```

**Windows:**
```cmd
"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="C:\temp\brave-debug-profile"
```

**Linux:**
```bash
brave-browser \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/brave-debug-profile"
```

---

### **Step 2: Verify CDP is Running**

Open this URL in any browser:
```
http://localhost:9222/json/version
```

**Expected output:**
```json
{
  "Browser": "Chrome/120.0.6099.109",
  "Protocol-Version": "1.3",
  "User-Agent": "Mozilla/5.0...",
  "V8-Version": "12.0.267.8",
  "WebKit-Version": "537.36",
  "webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser/..."
}
```

✅ If you see this, CDP is working!

---

### **Step 3: Enable CDP Mode in Screenshot Tool**

**In the screenshot tool UI:**
1. Go to **Settings** section
2. Find **"🌐 Real Browser Mode (CDP Mode)"**
3. Check the box: ☑ **"Use real browser (slower, visible window)"**
4. The tool will now connect to Brave at `http://localhost:9222`

---

## 🔧 Advanced Configuration

### **Use Your Real Brave Profile (Keep Your Sessions)**

**⚠️ WARNING:** Close all Brave windows first, or you'll get a "profile in use" error!

**macOS:**
```bash
# Close all Brave windows first!
killall "Brave Browser"

# Launch with your real profile
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/BraveSoftware/Brave-Browser"
```

**Windows:**
```cmd
REM Close all Brave windows first!
taskkill /F /IM brave.exe

REM Launch with your real profile
"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data"
```

**Linux:**
```bash
# Close all Brave windows first!
killall brave-browser

# Launch with your real profile
brave-browser \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.config/BraveSoftware/Brave-Browser"
```

---

## 🎨 Create a Launch Script (Recommended)

### **macOS/Linux: `launch-brave-cdp.sh`**

Create this file:
```bash
#!/bin/bash

# Kill existing Brave instances
killall "Brave Browser" 2>/dev/null || true

# Wait for processes to close
sleep 2

# Launch Brave with CDP enabled
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/BraveSoftware/Brave-Browser" \
  > /dev/null 2>&1 &

echo "✅ Brave launched with CDP on port 9222"
echo "🔗 CDP endpoint: http://localhost:9222"
echo "📊 Verify: http://localhost:9222/json/version"
```

**Make it executable:**
```bash
chmod +x launch-brave-cdp.sh
```

**Run it:**
```bash
./launch-brave-cdp.sh
```

---

### **Windows: `launch-brave-cdp.bat`**

Create this file:
```batch
@echo off
echo Closing existing Brave instances...
taskkill /F /IM brave.exe 2>nul

echo Waiting for processes to close...
timeout /t 2 /nobreak >nul

echo Launching Brave with CDP...
start "" "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data"

echo.
echo ✅ Brave launched with CDP on port 9222
echo 🔗 CDP endpoint: http://localhost:9222
echo 📊 Verify: http://localhost:9222/json/version
```

**Run it:**
```cmd
launch-brave-cdp.bat
```

---

## 🔍 Troubleshooting

### **Problem 1: "Address already in use" (Port 9222 busy)**

**Solution:**
```bash
# macOS/Linux: Find what's using port 9222
lsof -i :9222

# Kill the process
kill -9 <PID>

# Windows: Find what's using port 9222
netstat -ano | findstr :9222

# Kill the process
taskkill /F /PID <PID>
```

---

### **Problem 2: "Profile is already in use"**

**Cause:** Brave is already running with that profile.

**Solution:**
```bash
# macOS/Linux
killall "Brave Browser"

# Windows
taskkill /F /IM brave.exe

# Wait 2 seconds, then launch again
```

---

### **Problem 3: "Connection refused" when tool tries to connect**

**Check if CDP is running:**
```bash
curl http://localhost:9222/json/version
```

**If it fails:**
1. Make sure Brave is running
2. Make sure you used `--remote-debugging-port=9222`
3. Check firewall settings
4. Try a different port (e.g., 9223)

---

### **Problem 4: Tool can't find Brave**

**Solution:** Update CDP URL in screenshot tool settings:
- Default: `http://localhost:9222`
- Custom port: `http://localhost:9223` (if you changed the port)

---

## 📊 CDP Mode vs Headless Mode

| Feature | CDP Mode (Brave) | Headless Mode |
|---------|------------------|---------------|
| **Browser** | Your Brave | Tool launches browser |
| **Visibility** | ✅ Visible | ❌ Invisible |
| **Sessions** | ✅ Reuse existing | ❌ Fresh each time |
| **Speed** | Slower (visible) | Faster (headless) |
| **Debugging** | ✅ Easy to see | ❌ Hard to debug |
| **Parallel URLs** | 1-10 tabs | Unlimited |
| **Best for** | Debugging, manual login | Batch processing |

---

## 🎯 Recommended Workflow

### **For Daily Use:**

1. **Launch Brave with CDP** (once per day)
   ```bash
   ./launch-brave-cdp.sh
   ```

2. **Login to your websites** (once per day)
   - Open tabs in Brave
   - Login to all your sites
   - Keep Brave open

3. **Use Screenshot Tool**
   - Enable CDP mode in settings
   - Tool connects to Brave
   - Tool uses your existing sessions
   - No need to login again!

4. **Extract Cookies** (optional, for headless mode)
   - Go to "🔐 Auth Data" tab
   - Click "Import from Browser"
   - Select "Brave"
   - Cookies saved for headless mode

---

## 🔐 Security Notes

### **⚠️ Important Security Warnings:**

1. **CDP exposes full browser control**
   - Anyone on your computer can control Brave via port 9222
   - Don't expose port 9222 to the internet
   - Only use on trusted networks

2. **Temporary profile is safer**
   - Use `--user-data-dir="/tmp/brave-debug-profile"` for testing
   - Use real profile only when you need existing sessions

3. **Close CDP when done**
   - Close Brave when not using screenshot tool
   - Prevents unauthorized access

---

## ✅ Quick Reference

### **Launch Commands**

**Temporary Profile (Safe):**
```bash
# macOS
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/brave-debug-profile"
```

**Real Profile (Keep Sessions):**
```bash
# macOS (close Brave first!)
killall "Brave Browser"
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/BraveSoftware/Brave-Browser"
```

### **Verify CDP:**
```bash
curl http://localhost:9222/json/version
```

### **Screenshot Tool Settings:**
- ☑ Enable "Real Browser Mode (CDP Mode)"
- CDP URL: `http://localhost:9222`

---

## 🎉 You're Ready!

**Next Steps:**
1. Launch Brave with CDP using the command above
2. Verify CDP is working: `http://localhost:9222/json/version`
3. Enable CDP mode in screenshot tool
4. Start capturing screenshots!

**All features work with Brave:**
- ✅ Auto-scroll (segmented capture)
- ✅ Dropdown detection
- ✅ Parallel processing (1-10 tabs)
- ✅ Cookie extraction
- ✅ Session reuse

**Happy screenshotting!** 🦁📸

