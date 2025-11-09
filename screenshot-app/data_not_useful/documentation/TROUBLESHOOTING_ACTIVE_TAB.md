# 🔧 Active Tab Mode - Troubleshooting Guide

**Common issues and how to fix them**

---

## ❌ Error: "ECONNREFUSED ::1:9222"

### **Problem**
The screenshot tool cannot connect to Chrome because Chrome is not running with remote debugging enabled.

### **Solution**

**Step 1: Close Chrome completely**
```bash
# Close all Chrome windows
# Or use Activity Monitor to quit Chrome
```

**Step 2: Launch Chrome with debugging**
```bash
cd screenshot-app
./launch-chrome-debug.sh
```

**Step 3: Verify Chrome is ready**
```bash
./check-chrome-debug.sh
```

You should see:
```
✅ Chrome is running with remote debugging on port 9222
```

**Step 4: Try capturing again**
- Enable "Real Browser" mode in Settings
- Enter URLs and click "Capture Screenshots"

---

## ❌ Error: "Chrome is already running"

### **Problem**
Chrome is running but without remote debugging enabled.

### **Solution**

**Option 1: Close and relaunch (Recommended)**
1. Close all Chrome windows completely
2. Run: `./launch-chrome-debug.sh`
3. Chrome will open with debugging enabled

**Option 2: Manual launch**
1. Close all Chrome windows
2. Run this command:
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug-profile
   ```

---

## ❌ Error: "No tabs found in Chrome"

### **Problem**
Chrome is running with debugging, but has no tabs open.

### **Solution**

1. Open a new tab in Chrome (Cmd+T)
2. Try capturing again

---

## ❌ Error: "Failed to connect to Chrome via CDP"

### **Problem**
The CDP connection failed for an unknown reason.

### **Solution**

**Step 1: Check if Chrome is listening on port 9222**
```bash
lsof -Pi :9222 -sTCP:LISTEN
```

If nothing is returned, Chrome is not running with debugging.

**Step 2: Restart Chrome with debugging**
```bash
# Close Chrome completely
./launch-chrome-debug.sh
```

**Step 3: Check the CDP endpoint**
```bash
curl http://localhost:9222/json/version
```

You should see JSON output with Chrome version info.

**Step 4: Try again**

---

## ❌ Screenshots are blank or incomplete

### **Problem**
Screenshots are being captured but they're blank or missing content.

### **Solution**

**Increase timeout:**
1. Go to Settings tab
2. Increase "Page Load Timeout" to 30000ms or higher
3. Try capturing again

**Wait for page to load:**
- Some pages take longer to load
- Watch the Chrome tab to see when the page is fully loaded
- The tool waits 2 seconds after page load before capturing

**Check for lazy-loaded content:**
- Enable "Smart Lazy Load" in Settings
- This scrolls the page to trigger lazy-loaded images

---

## ❌ Chrome closes immediately after launching

### **Problem**
Chrome opens and then closes right away.

### **Solution**

**Check for Chrome updates:**
1. Chrome might be trying to update
2. Let it update and restart
3. Then run `./launch-chrome-debug.sh` again

**Try manual launch:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir=/tmp/chrome-debug-profile \
    --no-first-run \
    --no-default-browser-check
```

---

## ❌ Port 9222 is already in use

### **Problem**
Another process is using port 9222.

### **Solution**

**Find what's using the port:**
```bash
lsof -Pi :9222 -sTCP:LISTEN
```

**Kill the process:**
```bash
# If it's an old Chrome instance
pkill -f "remote-debugging-port=9222"

# Or kill by PID
kill <PID>
```

**Then launch Chrome again:**
```bash
./launch-chrome-debug.sh
```

---

## ❌ "Real Browser" mode is slow

### **Problem**
Capturing screenshots in Active Tab Mode is slower than expected.

### **Explanation**
This is normal! Active Tab Mode is slower because:
- Chrome renders everything visibly (not headless)
- Uses a single tab (no parallelization)
- Waits for full page load and rendering

### **Solutions**

**For speed, use Standard Mode:**
- Disable "Real Browser" mode
- Use headless mode for bulk captures
- Active Tab Mode is best for debugging and verification

**Optimize Active Tab Mode:**
- Reduce "Scroll Delay" in Settings (for segmented capture)
- Disable "Smart Lazy Load" if not needed
- Use "Viewport" capture instead of "Segmented"

---

## ❌ Chrome profile conflicts

### **Problem**
Chrome won't start because of profile conflicts.

### **Solution**

**Use a clean profile:**
```bash
# Remove the debug profile
rm -rf /tmp/chrome-debug-profile

# Launch Chrome again
./launch-chrome-debug.sh
```

**Or use a different profile location:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir=/tmp/chrome-debug-$(date +%s)
```

---

## ❌ Backend not connecting to Chrome

### **Problem**
The backend shows connection errors even though Chrome is running.

### **Solution**

**Check backend logs:**
Look for error messages in the backend terminal.

**Restart the backend:**
1. Stop the backend (Ctrl+C)
2. Start it again: `cd backend && python3 main.py`
3. Try capturing again

**Check Playwright installation:**
```bash
cd screenshot-app/backend
python3 -m playwright install chromium
```

---

## 🔍 Diagnostic Commands

### **Check if Chrome is running with debugging:**
```bash
lsof -Pi :9222 -sTCP:LISTEN
```

### **Check CDP endpoint:**
```bash
curl http://localhost:9222/json/version
```

### **List all Chrome tabs:**
```bash
curl http://localhost:9222/json/list
```

### **Check Chrome processes:**
```bash
ps aux | grep Chrome
```

### **Kill all Chrome processes:**
```bash
pkill -f "Google Chrome"
```

---

## 📚 Still Having Issues?

### **Check the logs:**

**Backend logs:**
- Look at the terminal where you ran `npm start` or `python3 main.py`
- Look for error messages with ❌

**Frontend logs:**
- Open browser DevTools (F12)
- Check Console tab for errors

### **Test with the test script:**
```bash
cd screenshot-app
python3 test_cdp_connection.py
```

This will test:
1. CDP connection
2. Active tab detection
3. Navigation
4. Screenshot capture

### **Verify your setup:**

**Required:**
- ✅ Chrome installed at `/Applications/Google Chrome.app`
- ✅ Python 3.8+ with Playwright installed
- ✅ Backend running on port 8000
- ✅ Chrome running with `--remote-debugging-port=9222`

**Check versions:**
```bash
# Chrome version
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version

# Python version
python3 --version

# Playwright version
python3 -c "import playwright; print(playwright.__version__)"
```

---

## 💡 Best Practices

### **For reliable Active Tab Mode:**

1. ✅ **Always launch Chrome with the script**
   ```bash
   ./launch-chrome-debug.sh
   ```

2. ✅ **Verify Chrome is ready before capturing**
   ```bash
   ./check-chrome-debug.sh
   ```

3. ✅ **Keep Chrome visible** (don't minimize)

4. ✅ **Don't switch tabs** during capture

5. ✅ **Watch for errors** in the Chrome tab

6. ✅ **Use Standard Mode for bulk captures** (100+ URLs)

7. ✅ **Use Active Tab Mode for debugging** and verification

---

## 🆘 Emergency Reset

If nothing works, try this complete reset:

```bash
# 1. Kill all Chrome processes
pkill -f "Google Chrome"

# 2. Remove debug profile
rm -rf /tmp/chrome-debug-profile

# 3. Restart backend
cd screenshot-app/backend
pkill -f "python3 main.py"
python3 main.py &

# 4. Launch Chrome with debugging
cd ..
./launch-chrome-debug.sh

# 5. Verify
./check-chrome-debug.sh

# 6. Try capturing again
```

---

## 📞 Need More Help?

If you're still having issues:

1. Check the documentation:
   - [ACTIVE_TAB_MODE.md](./ACTIVE_TAB_MODE.md) - Full guide
   - [ACTIVE_TAB_ARCHITECTURE.md](./ACTIVE_TAB_ARCHITECTURE.md) - Technical details

2. Run the diagnostic test:
   ```bash
   python3 test_cdp_connection.py
   ```

3. Check the error messages carefully - they usually tell you exactly what's wrong!

