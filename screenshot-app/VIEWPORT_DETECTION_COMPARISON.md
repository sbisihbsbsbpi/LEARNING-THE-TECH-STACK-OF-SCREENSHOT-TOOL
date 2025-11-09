# 📊 Viewport Detection: Headless vs Real Browser Mode

## 🔄 Side-by-Side Comparison

### Headless Mode (NEW BROWSER)

```
┌─────────────────────────────────────────────────────────┐
│ 1. User calls capture_segmented()                       │
│    viewport_width=1920, viewport_height=1080            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Launch new browser with exact dimensions             │
│    browser = await playwright.chromium.launch()         │
│    page = await browser.new_page()                      │
│    page.set_viewport_size(1920, 1080)  ✅               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Viewport is GUARANTEED to be 1920x1080               │
│    ✅ Correct dimensions                                │
│    ✅ Segmented capture uses correct values             │
│    ✅ 100% pixel coverage                               │
└─────────────────────────────────────────────────────────┘
```

### Real Browser Mode (EXISTING CHROME)

```
┌─────────────────────────────────────────────────────────┐
│ 1. User calls capture_segmented()                       │
│    viewport_width=1920, viewport_height=1080            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Connect to existing Chrome via CDP                   │
│    cdp_browser = await playwright.chromium              │
│                    .connect_over_cdp()                  │
│    new_tab = await cdp_browser.new_page()               │
│    ❌ NO VIEWPORT DETECTION!                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Chrome window might be ANY size!                     │
│    Real Chrome window: 1366x768                         │
│    Parameter says: 1920x1080                            │
│    ❌ MISMATCH!                                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Segmented capture uses WRONG dimensions              │
│    scroll_step = 1080 * 0.8 = 864px  ❌ WRONG!         │
│    Should be: 768 * 0.8 = 614px  ✅ CORRECT            │
│    Result: Missing pixels at bottom!                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Differences

| Aspect | Headless Mode | Real Browser Mode |
|--------|---------------|-------------------|
| **Browser Source** | New instance launched | Existing Chrome |
| **Viewport Control** | ✅ Set explicitly | ❌ Unknown |
| **Viewport Detection** | ✅ Guaranteed | ❌ Missing |
| **Parameter Usage** | ✅ Accurate | ❌ May be wrong |
| **Pixel Coverage** | ✅ 100% | ❌ May miss pixels |
| **Segment Count** | ✅ Correct | ❌ May be wrong |

---

## 🔍 Code Locations

### Headless Mode: Viewport is Set

```python
# screenshot_service.py:2195-2230
browser = await self._get_browser(use_real_browser=False)
new_tab = await browser.new_page()

# Viewport is set when browser is launched
# screenshot_service.py:677-690
self.browser = await self.playwright.chromium.launch_persistent_context(
    ...
    viewport={'width': random_viewport['width'], 'height': random_viewport['height']},
    ...
)
```

### Real Browser Mode: Viewport is NOT Detected

```python
# screenshot_service.py:2085-2181
if use_real_browser:
    # Connect to Chrome
    if self.cdp_browser is None:
        await self._connect_to_chrome_cdp()  # ← No viewport detection
    
    # Create new tab
    new_tab = await self._create_new_tab_next_to_active()  # ← No viewport detection
    
    # Navigate
    await new_tab.goto(url)  # ← No viewport detection
    
    # ❌ MISSING: Detect actual viewport here!
    
    # Use parameters (which may be wrong!)
    result = await self._capture_segments_from_page(
        page=new_tab,
        viewport_width=viewport_width,      # ← Parameter, not actual!
        viewport_height=viewport_height,    # ← Parameter, not actual!
        ...
    )
```

---

## 📐 Viewport Detection Methods Available

### Method 1: page.viewport_size (BEST)

```python
viewport = page.viewport_size
# Returns: {'width': 1366, 'height': 768}
# Works for: Both headless and real browser mode
# Reliability: ✅ High
```

### Method 2: JavaScript window.innerWidth/Height

```python
viewport_info = await page.evaluate("""() => {
    return {
        width: window.innerWidth,
        height: window.innerHeight
    };
}""")
# Returns: {'width': 1366, 'height': 768}
# Works for: Both headless and real browser mode
# Reliability: ✅ High
```

### Method 3: Scrollable Element (CURRENT)

```python
scrollable_info = await page.evaluate("""() => {
    // Find scrollable element
    return {
        clientHeight: bestElement.clientHeight  // ← Element height, not viewport!
    };
}""")
# Returns: {'clientHeight': 675}  ← This is element height, not viewport!
# Works for: Both modes
# Reliability: ❌ Low (measures element, not viewport)
```

---

## ✅ Recommended Implementation

### Add to capture_segmented() at line 2085

```python
if use_real_browser:
    print("🔗 Active Tab Mode: Using your existing Chrome browser")
    new_tab = None
    try:
        # Connect to Chrome via CDP
        if self.cdp_browser is None:
            await self._connect_to_chrome_cdp()
        
        # Create new tab
        new_tab = await self._create_new_tab_next_to_active()
        
        # Navigate to URL
        await new_tab.goto(url, wait_until='networkidle', timeout=30000)
        
        # ✅ NEW: DETECT ACTUAL VIEWPORT
        actual_viewport = new_tab.viewport_size
        if actual_viewport:
            viewport_width = actual_viewport['width']
            viewport_height = actual_viewport['height']
            print(f"📐 Detected Chrome viewport: {viewport_width}x{viewport_height}")
        else:
            # Fallback to JavaScript detection
            viewport_info = await new_tab.evaluate("""() => {
                return {
                    width: window.innerWidth,
                    height: window.innerHeight
                };
            }""")
            viewport_width = viewport_info['width']
            viewport_height = viewport_info['height']
            print(f"📐 Detected viewport from JS: {viewport_width}x{viewport_height}")
        
        # Continue with segmented capture using ACTUAL viewport
        result = await self._capture_segments_from_page(
            page=new_tab,
            url=url,
            viewport_width=viewport_width,      # ← Now ACTUAL!
            viewport_height=viewport_height,    # ← Now ACTUAL!
            ...
        )
```

---

## 🎉 Summary

**Headless Mode**: ✅ Viewport is controlled and known
**Real Browser Mode**: ❌ Viewport is unknown and not detected

**Fix**: Add 5-10 lines of viewport detection code before segmented capture

**Impact**: Ensures correct segmented capture calculations for real browser mode

