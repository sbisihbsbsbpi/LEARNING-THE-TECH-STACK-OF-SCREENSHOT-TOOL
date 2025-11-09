# 🔗 Active Tab Mode - Use Your Existing Chrome Browser

**NEW FEATURE:** The screenshot tool can now connect to your existing Chrome browser and use the **active tab** for capturing screenshots!

---

## 🎯 What is Active Tab Mode?

Instead of launching a new browser window, the tool connects to your **already-running Chrome browser** via CDP (Chrome DevTools Protocol) and:

1. ✅ Finds your **currently active tab**
2. ✅ Loads each URL in that tab
3. ✅ Takes screenshots while you watch
4. ✅ Keeps the browser **visible** throughout the process

---

## 🚀 Quick Start

### **Step 1: Launch Chrome with Remote Debugging**

```bash
cd screenshot-app
./launch-chrome-debug.sh
```

This will launch Chrome with remote debugging enabled on port 9222.

**Or manually:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

### **Step 2: Enable Real Browser Mode**

In the screenshot tool UI:
1. Go to **Settings** tab
2. Enable **"Real Browser"** mode
3. Go back to **Main** tab
4. Enter your URLs and click **Capture**

### **Step 3: Watch the Magic!**

The tool will:
- Connect to your Chrome browser
- Use your active tab
- Load each URL one by one
- Capture screenshots
- Keep the browser visible so you can see what's happening

---

## 🆚 Active Tab Mode vs Standard Mode

| Feature | Active Tab Mode | Standard Mode |
|---------|----------------|---------------|
| **Browser** | Your existing Chrome | New browser window |
| **Visibility** | Always visible | Can be headless |
| **Tab** | Uses active tab | Creates new tabs |
| **Connection** | CDP (port 9222) | Direct launch |
| **Speed** | Slightly slower | Faster |
| **Use Case** | Debugging, watching | Bulk automation |

---

## 🔧 How It Works

### **Technical Details**

1. **Chrome Launch**: Chrome must be launched with `--remote-debugging-port=9222`
2. **CDP Connection**: Playwright connects via `connect_over_cdp()`
3. **Active Tab Detection**: The tool finds the first tab in the first window
4. **URL Loading**: Each URL is loaded in that same tab
5. **Screenshot Capture**: Screenshots are taken after each page load

### **Code Flow**

```python
# Connect to Chrome via CDP
browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

# Get active tab
contexts = browser.contexts
pages = contexts[0].pages
active_page = pages[0]

# Load URL in active tab
await active_page.goto(url)

# Capture screenshot
await active_page.screenshot(path=filepath)
```

---

## 💡 Use Cases

### **When to Use Active Tab Mode**

✅ **Debugging**: Watch what's happening in real-time  
✅ **Manual Login**: Login manually, then let the tool capture  
✅ **Interactive Sites**: Sites that need manual interaction  
✅ **Verification**: Verify screenshots are correct as they're captured  

### **When to Use Standard Mode**

✅ **Bulk Automation**: Capture 100+ URLs quickly  
✅ **Headless Mode**: Run in background without UI  
✅ **CI/CD**: Automated testing and deployment  
✅ **Speed**: Faster parallel processing  

---

## 🐛 Troubleshooting

### **Error: "Failed to connect to Chrome via CDP"**

**Solution:**
1. Make sure Chrome is running with remote debugging:
   ```bash
   ./launch-chrome-debug.sh
   ```
2. Check that port 9222 is not blocked
3. Verify Chrome is actually running

### **Error: "No tabs found in Chrome"**

**Solution:**
1. Make sure Chrome has at least one tab open
2. Try opening a new tab (Cmd+T)
3. Restart Chrome with the debug script

### **Screenshots are blank**

**Solution:**
1. Wait for pages to fully load before capturing
2. Increase the timeout in settings
3. Check if the page has content restrictions

---

## 🔐 Security Notes

- **Port 9222**: Chrome's debugging port is only accessible locally (localhost)
- **No Remote Access**: The CDP endpoint is not exposed to the internet
- **Same Machine**: The tool and Chrome must be on the same machine
- **User Control**: You maintain full control of the browser

---

## 📚 Advanced Usage

### **Custom CDP Port**

If you need to use a different port:

```bash
# Launch Chrome on port 9223
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223
```

Then modify `screenshot_service.py`:
```python
await self._connect_to_chrome_cdp("http://localhost:9223")
```

### **Multiple Chrome Instances**

You can run multiple Chrome instances on different ports:
```bash
# Instance 1 (port 9222)
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome1

# Instance 2 (port 9223)
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223 --user-data-dir=/tmp/chrome2
```

---

## 🎓 Learn More

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Playwright connect_over_cdp](https://playwright.dev/docs/api/class-browsertype#browser-type-connect-over-cdp)
- [Remote Debugging in Chrome](https://developer.chrome.com/docs/devtools/remote-debugging/)

---

## 🎉 Summary

Active Tab Mode gives you:
- ✅ **Visual feedback** - See what's being captured
- ✅ **Manual control** - Interact with pages if needed
- ✅ **Debugging** - Troubleshoot issues in real-time
- ✅ **Flexibility** - Use your existing browser setup

Perfect for when you need to **see what's happening** or **manually interact** with pages during capture!

