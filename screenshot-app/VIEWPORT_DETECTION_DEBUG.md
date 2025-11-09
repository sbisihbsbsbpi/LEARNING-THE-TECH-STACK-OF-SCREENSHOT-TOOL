# 🔍 Viewport Detection Debug Guide

## Quick Debug Checklist

- [ ] Chrome is running with `--remote-debugging-port=9222`
- [ ] FastAPI backend is running
- [ ] Frontend is running
- [ ] Console output shows viewport detection messages
- [ ] Detected viewport matches actual Chrome window size

---

## 🧪 Testing Steps

### Step 1: Launch Chrome with Remote Debugging
```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

### Step 2: Verify Chrome is Listening
```bash
curl http://localhost:9222/json/version
```

Expected output:
```json
{
  "Browser": "Chrome/...",
  "Protocol-Version": "1.3",
  "User-Agent": "Mozilla/5.0...",
  "V8-Version": "...",
  "WebKit-Version": "...",
  "webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser/..."
}
```

### Step 3: Run Screenshot Tool in Real Browser Mode
1. Open the screenshot tool UI
2. Click "Active Tab Mode" or similar
3. Enter a URL
4. Click "Capture"

### Step 4: Check Console Output
Look for these messages in the backend console:

```
🔗 Active Tab Mode: Using your existing Chrome browser
   ⏳ Waiting for React app to render...
   ✅ Network idle - content loaded
   ⏳ Waiting for dynamic content to load...
   🔄 Triggered content loading in workspace
   📐 Detecting actual Chrome window viewport...
   ✅ Detected Chrome viewport: 1366x768
   📊 Segmented capture: 4 segments
   ✅ Screenshot captured - tab left open for review
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Could not detect viewport"
**Symptom**: Console shows `⚠️ Could not detect viewport: ...`

**Causes**:
- Chrome not running with remote debugging
- Network connectivity issue
- Playwright version mismatch

**Solutions**:
1. Verify Chrome is running: `curl http://localhost:9222/json/version`
2. Check Playwright version: `pip show playwright`
3. Restart Chrome with `--remote-debugging-port=9222`

---

### Issue 2: "viewport_size is None"
**Symptom**: Console shows `⚠️ viewport_size is None, using JavaScript detection...`

**Causes**:
- Playwright's `viewport_size` property not available
- Page not fully loaded yet

**Solutions**:
1. This is normal - fallback to JavaScript detection works fine
2. If JavaScript detection also fails, check page load status
3. Verify page is accessible in the tab

---

### Issue 3: Wrong Viewport Detected
**Symptom**: Detected viewport doesn't match actual Chrome window

**Causes**:
- Chrome window was resized after connection
- Multiple Chrome windows open
- Browser zoom level affecting measurements

**Solutions**:
1. Don't resize Chrome window during capture
2. Close other Chrome windows
3. Reset browser zoom to 100%

---

### Issue 4: Missing Pixels at Bottom
**Symptom**: Screenshot is missing pixels at the bottom

**Causes**:
- Viewport detection failed silently
- Using parameter values instead of detected values
- Scroll calculation still wrong

**Solutions**:
1. Check console output for viewport detection message
2. Verify detected viewport is correct
3. Check scroll_step calculation in logs

---

## 📊 Debug Output Analysis

### Expected Output (Success)
```
📐 Detecting actual Chrome window viewport...
✅ Detected Chrome viewport: 1366x768
```

**What this means**:
- ✅ Viewport detection succeeded
- ✅ Using actual Chrome window size (1366x768)
- ✅ Scroll_step will be calculated correctly

### Fallback Output (Still OK)
```
📐 Detecting actual Chrome window viewport...
⚠️ viewport_size is None, using JavaScript detection...
✅ Detected viewport from JS: 1366x768
```

**What this means**:
- ⚠️ Primary method didn't work
- ✅ Fallback JavaScript method worked
- ✅ Still using correct viewport size

### Error Output (Problem)
```
📐 Detecting actual Chrome window viewport...
⚠️ Could not detect viewport: [error message]
ℹ️ Using parameter values: 1920x1080
```

**What this means**:
- ❌ Both detection methods failed
- ⚠️ Falling back to parameter values
- ⚠️ May have wrong viewport size

---

## 🔧 Manual Testing

### Test 1: Verify Viewport Detection Works
```python
# In Python shell
from playwright.async_api import async_playwright
import asyncio

async def test_viewport():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        
        # Test 1: Check viewport_size
        print(f"viewport_size: {page.viewport_size}")
        
        # Test 2: Check window.innerWidth/Height
        viewport_info = await page.evaluate("""() => {
            return {
                width: window.innerWidth,
                height: window.innerHeight
            };
        }""")
        print(f"window.inner: {viewport_info}")
        
        await browser.close()

asyncio.run(test_viewport())
```

### Test 2: Verify Scroll Step Calculation
```python
# Expected calculation
viewport_height = 768  # Detected
overlap_percent = 20
scroll_step = int(viewport_height * (1 - overlap_percent / 100))
print(f"scroll_step: {scroll_step}")  # Should be 614

# Before fix (WRONG)
viewport_height = 1080  # Parameter
scroll_step = int(viewport_height * (1 - overlap_percent / 100))
print(f"scroll_step (wrong): {scroll_step}")  # Would be 864
```

---

## 📈 Performance Metrics

### Expected Performance
- Viewport detection: < 100ms
- Total capture time: Depends on page size
- No additional overhead

### Monitoring
Check backend logs for timing:
```
📐 Detecting actual Chrome window viewport...
✅ Detected Chrome viewport: 1366x768
[capture starts]
```

---

## 🎯 Verification Checklist

After implementing the fix, verify:

- [ ] Console shows viewport detection message
- [ ] Detected viewport matches actual Chrome window
- [ ] Scroll_step is calculated correctly
- [ ] Segment count is correct
- [ ] No missing pixels at bottom
- [ ] Screenshot quality is good
- [ ] Works with different Chrome window sizes

---

## 📞 Debug Commands

### Check Chrome Connection
```bash
curl http://localhost:9222/json/version
```

### Check Backend Logs
```bash
# If using FastAPI with uvicorn
tail -f backend.log
```

### Test Viewport Detection Directly
```bash
# In Python
python -c "
from playwright.async_api import async_playwright
import asyncio

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        page = await browser.contexts[0].new_page()
        print(f'Viewport: {page.viewport_size}')
        await browser.close()

asyncio.run(test())
"
```

---

## ✅ Success Indicators

You'll know the fix is working when:

1. ✅ Console shows "✅ Detected Chrome viewport: [size]"
2. ✅ Detected size matches actual Chrome window
3. ✅ Screenshots capture all pixels (no missing bottom)
4. ✅ Segment count is correct
5. ✅ Works with different Chrome window sizes

---

## 🚀 Next Steps

If debugging is successful:
1. Test with different Chrome window sizes
2. Test with different page heights
3. Test with different overlap percentages
4. Proceed to Phase 2 improvements

If issues persist:
1. Check Chrome version compatibility
2. Verify Playwright version
3. Check network connectivity
4. Review error messages in console

