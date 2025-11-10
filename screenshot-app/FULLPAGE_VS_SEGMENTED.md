# 📄 Full Page vs Segmented Mode - When to Use Which

## 🔍 The Issue You're Experiencing

**Problem**: AccountPayable screenshot is only 1366x768 (viewport only) instead of capturing the full scrollable content.

**Root Cause**: You're using **"Full page" mode** on a page with a **fixed-height scrollable container**.

---

## 📊 How Different Modes Work

### 1. **Viewport Mode** 🖼️
- Captures only what's visible in the browser window
- **Size**: Exactly viewport size (e.g., 1366x768)
- **Use case**: Quick previews, above-the-fold content

### 2. **Full Page Mode** 📄
- Uses Playwright's `full_page=True` parameter
- Captures from `scrollY=0` to `document.body.scrollHeight`
- **Works for**: Normal scrolling pages (Wikipedia, blogs, etc.)
- **Doesn't work for**: Fixed-height containers with internal scrolling

### 3. **Segmented Mode** 📚
- Captures page in viewport-sized segments
- Detects scrollable containers automatically
- Scrolls the correct element (not just window)
- **Works for**: ALL page types (including fixed containers)

---

## 🎯 The Tekion AccountPayable Issue

### What's Happening:

```
┌─────────────────────────────────┐
│  Browser Window (1366x768)      │
│  ┌───────────────────────────┐  │
│  │ #tekion-workspace         │  │ ← Fixed height container
│  │ (overflow: auto)          │  │    with internal scrolling
│  │                           │  │
│  │ [Scrollable content]      │  │ ← 2500px of content
│  │ [2500px total height]     │  │    inside 675px container
│  │                           │  │
│  │ ▼ Scroll bar here         │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### Why Full Page Mode Fails:

1. **Full page mode** calls `page.screenshot(full_page=True)`
2. Playwright captures from `scrollY=0` to `document.body.scrollHeight`
3. **But** `document.body.scrollHeight = 768px` (viewport height)
4. **Because** scrolling happens inside `#tekion-workspace`, not on the body
5. **Result**: Only captures 768px (viewport), not 2500px (actual content)

### Why Segmented Mode Works:

1. **Segmented mode** detects scrollable containers
2. Finds `#tekion-workspace` (priority selector)
3. Scrolls the **container** (not the window)
4. Captures all 2500px of content in segments
5. **Result**: Complete capture of all content

---

## ✅ Solution

### Option 1: Use Segmented Mode (Recommended)

**In the UI**:
1. Go to Settings
2. Under "📸 Capture Mode", select **"📚 Segmented"**
3. Click "Capture Screenshots"

**Result**: Will capture all content in the scrollable container

---

### Option 2: Let the Code Warn You (New Feature)

I've added **automatic detection** that warns you when full page mode won't work:

**When you use "Full page" mode on Tekion pages, you'll now see**:

```
⚠️  WARNING: Fixed-height scrollable container detected!
   Container: #tekion-workspace (2500px scrollable)
   Document body: 768px (viewport height)
   💡 RECOMMENDATION: Use 'Segmented' mode instead of 'Full page' mode
   💡 Full page mode will only capture 768px (viewport)
   💡 Segmented mode will capture all 2500px of content
```

---

## 📋 Quick Reference

| Page Type | Example | Full Page Works? | Segmented Works? | Recommended |
|-----------|---------|------------------|------------------|-------------|
| **Normal scrolling** | Wikipedia, blogs | ✅ Yes | ✅ Yes | Full Page (faster) |
| **Fixed container** | Tekion, Gmail, Slack | ❌ No | ✅ Yes | **Segmented** |
| **Lazy loading** | Infinite scroll | ⚠️ Partial | ✅ Yes | **Segmented** |
| **Single screen** | Login pages | ✅ Yes | ✅ Yes | Viewport (fastest) |

---

## 🧪 Test It Now

### Test 1: Wikipedia (Normal Scrolling)
```
URL: https://en.wikipedia.org/wiki/Main_Page
Mode: Full page
Expected: ✅ Captures full page (1920x3509)
```

### Test 2: Tekion AccountPayable (Fixed Container)
```
URL: https://preprodapp.tekioncloud.com/accounting/accountPayable
Mode: Full page
Expected: ⚠️ Only captures viewport (1366x768) + WARNING message
```

### Test 3: Tekion AccountPayable (Segmented)
```
URL: https://preprodapp.tekioncloud.com/accounting/accountPayable
Mode: Segmented
Expected: ✅ Captures all content (multiple segments)
```

---

## 🎯 Why This Matters

### Before (Full Page Mode on Tekion):
- ❌ Only captures 768px (viewport)
- ❌ Misses 1732px of content (69% missing!)
- ❌ No warning to user

### After (Segmented Mode on Tekion):
- ✅ Captures all 2500px (100% complete)
- ✅ Automatic detection of scrollable container
- ✅ Warning if using wrong mode

---

## 🔧 Technical Details

### Full Page Mode Implementation:
```python
await page.screenshot(
    path=str(filepath),
    full_page=True,  # ← Captures document.body.scrollHeight
    type='png'
)
```

### Segmented Mode Implementation:
```python
# 1. Detect scrollable container
scrollable_element = find_scrollable_container(page)  # Finds #tekion-workspace

# 2. Scroll the container (not window)
await page.evaluate(f"""() => {{
    const element = document.querySelector('#tekion-workspace');
    element.scrollBy(0, {viewport_height});
}}""")

# 3. Capture each segment
await page.screenshot(path=segment_path, full_page=False)
```

---

## 📝 Summary

**The fix is simple**: Use **"Segmented" mode** for Tekion pages (and any page with fixed-height scrollable containers).

**The code now helps you**: Automatically detects when you're using the wrong mode and warns you with a clear recommendation.

**Performance**: Segmented mode is only slightly slower (~2-3 seconds per page) but captures 100% of content vs 31% with full page mode.

---

## 🎉 Next Steps

1. **Try it now**: Switch to Segmented mode and capture AccountPayable
2. **Check the logs**: You'll see the new warning messages
3. **Compare screenshots**: Full page (768px) vs Segmented (2500px)

The improvements we made earlier (priority selectors, adaptive stabilization, browser mode detection) all work in **Segmented mode**, making it both **faster** and **more reliable**!
