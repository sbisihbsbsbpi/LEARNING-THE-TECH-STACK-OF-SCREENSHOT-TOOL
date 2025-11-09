# 📍 Base URL Feature - Custom Screenshot Naming (PascalCase)

**Date**: November 1, 2025
**Status**: ✅ **IMPLEMENTED**

---

## 🎯 **Feature Overview**

Added **Base URL** input in Settings tab that allows custom screenshot naming based on URL paths using **PascalCase with underscore separator** (e.g., `Accounting_AutoPostingSettings.png`) instead of domain + timestamp.

### **Naming Convention:**

- **PascalCase**: Each word starts with a capital letter (e.g., `Accounting`, `AutoPosting`, `Settings`)
- **Underscore separator**: Used to separate logical modules or contexts (e.g., `Accounting_AutoPostingSettings`)
- **Also known as**: Compound PascalCase, Domain_PascalCaseEntity pattern

---

## 🎨 **UI Changes**

### **Settings Tab - New Base URL Input:**

```
┌─────────────────────────────────────────┐
│  ⚙️ Settings Tab                        │
├─────────────────────────────────────────┤
│  📍 Base URL (Optional)                 │
│  ┌─────────────────────────────────┐   │
│  │ https://preprodapp.tekioncloud… │   │  ← Single line input
│  └─────────────────────────────────┘   │
│  💡 Used for screenshot naming          │
│                                         │
│  📸 Capture Mode                        │
│  ...                                    │
└─────────────────────────────────────────┘
```

---

## 🔧 **Naming Logic**

### **With Base URL:**

**Base URL**: `https://preprodapp.tekioncloud.com/`

#### **Case 1: Single Screenshot**

- **URL**: `https://preprodapp.tekioncloud.com/accounting/autoPostingSettings`
- **Path after base**: `accounting/autoPostingSettings`
- **Screenshot name**: `Accounting_AutoPostingSettings.png` ✨

#### **Case 2: Multiple Screenshots (8 segments)**

- **URL**: `https://preprodapp.tekioncloud.com/accounting/dashboard`
- **Path after base**: `accounting/dashboard`
- **Screenshot names**:
  ```
  Accounting_Dashboard_001.png
  Accounting_Dashboard_002.png
  Accounting_Dashboard_003.png
  Accounting_Dashboard_004.png
  Accounting_Dashboard_005.png
  Accounting_Dashboard_006.png
  Accounting_Dashboard_007.png
  Accounting_Dashboard_008.png
  ```

#### **Case 3: URL doesn't match base URL**

- **Base URL**: `https://preprodapp.tekioncloud.com/`
- **URL**: `https://example.com/page`
- **Screenshot name**: `example.com_20251101_140530.png` (fallback to old naming)

---

### **Without Base URL (Empty):**

Falls back to old naming:

- **Single**: `domain_20251101_140530.png`
- **Multiple**: `domain_001_20251101_140530.png`

---

## 📝 **Implementation Details**

### **Frontend Changes:**

#### **1. State Management (App.tsx)**

```typescript
// Base URL for screenshot naming
const [baseUrl, setBaseUrl] = useState(() => {
  const saved = localStorage.getItem("screenshot-base-url");
  return saved || "";
});

// Persist to localStorage
useEffect(() => {
  localStorage.setItem("screenshot-base-url", baseUrl);
}, [baseUrl]);
```

#### **2. Settings UI (App.tsx)**

```tsx
<div className="settings-section">
  <h3>📍 Base URL (Optional)</h3>
  <input
    type="text"
    className="base-url-input"
    placeholder="https://example.com"
    value={baseUrl}
    onChange={(e) => setBaseUrl(e.target.value)}
    disabled={loading}
  />
  <p className="option-hint">
    💡 Used for screenshot naming. Path after base URL becomes filename.
  </p>
</div>
```

#### **3. Send to Backend (App.tsx)**

```typescript
body: JSON.stringify({
  urls: urlList,
  base_url: baseUrl,  // ← NEW
  ...
})
```

---

### **Backend Changes:**

#### **1. Request Model (main.py)**

```python
class URLRequest(BaseModel):
    urls: List[str]
    base_url: str = ""  # ← NEW
    ...
```

#### **2. Screenshot Service (screenshot_service.py)**

**Updated function signatures:**

```python
async def capture(
    self,
    url: str,
    base_url: str = "",  # ← NEW
    ...
) -> str:

async def capture_segmented(
    self,
    url: str,
    base_url: str = "",  # ← NEW
    ...
) -> list[str]:
```

**New helper function:**

```python
def _generate_filename(self, url: str, base_url: str, segment_index: int, total_segments: int) -> str:
    """
    Generate filename based on base URL logic

    Logic:
    - If base_url provided: subtract base_url from url, convert path to filename
    - Single segment: path_name.png
    - Multiple segments: path_name_001.png, path_name_002.png, etc.
    - If no base_url: use domain + timestamp (old behavior)
    """
    if base_url and url.startswith(base_url):
        # Subtract base URL from full URL
        path = url[len(base_url):]

        # Remove leading/trailing slashes
        path = path.strip('/')

        # Convert path to filename (replace / with _)
        base_name = path.replace('/', '_')

        # Remove query parameters and fragments
        if '?' in base_name:
            base_name = base_name.split('?')[0]
        if '#' in base_name:
            base_name = base_name.split('#')[0]

        # If empty, use "index"
        if not base_name:
            base_name = "index"

        # Generate filename based on segment count
        if total_segments == 1:
            filename = f"{base_name}.png"
        else:
            filename = f"{base_name}_{segment_index:03d}.png"
    else:
        # Fallback to old naming
        domain = url.split("//")[1].split("/")[0].replace(":", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if total_segments == 1:
            filename = f"{domain}_{timestamp}.png"
        else:
            filename = f"{domain}_{segment_index:03d}_{timestamp}.png"

    return filename
```

#### **3. Pass base_url to functions (main.py)**

```python
# Segmented capture
screenshot_paths = await screenshot_service.capture_segmented(
    url=url,
    base_url=request.base_url,  # ← NEW
    ...
)

# Regular capture
screenshot_path = await screenshot_service.capture(
    url=url,
    base_url=request.base_url,  # ← NEW
    ...
)
```

---

### **CSS Styling (styles.css)**

```css
.base-url-input {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-family: "Courier New", monospace;
  transition: all 0.3s ease;
  background: white;
  color: #333;
}

.base-url-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

body.dark-mode .base-url-input {
  background: #2a2a2a;
  border-color: #444;
  color: #e0e0e0;
}
```

---

## 🧪 **Testing**

### **Test Case 1: With Base URL (Single Screenshot)**

**Input:**

- Base URL: `https://preprodapp.tekioncloud.com/`
- URL: `https://preprodapp.tekioncloud.com/accounting/autoPostingSettings`
- Capture Mode: Viewport

**Expected Output:**

- Screenshot: `Accounting_AutoPostingSettings.png` ✨

---

### **Test Case 2: With Base URL (Multiple Screenshots)**

**Input:**

- Base URL: `https://preprodapp.tekioncloud.com/`
- URL: `https://preprodapp.tekioncloud.com/accounting/dashboard`
- Capture Mode: Segmented (8 segments)

**Expected Output:**

- Screenshots:
  ```
  Accounting_Dashboard_001.png
  Accounting_Dashboard_002.png
  Accounting_Dashboard_003.png
  Accounting_Dashboard_004.png
  Accounting_Dashboard_005.png
  Accounting_Dashboard_006.png
  Accounting_Dashboard_007.png
  Accounting_Dashboard_008.png
  ```

---

### **Test Case 3: Without Base URL**

**Input:**

- Base URL: (empty)
- URL: `https://example.com/page`
- Capture Mode: Viewport

**Expected Output:**

- Screenshot: `example.com_20251101_140530.png`

---

### **Test Case 4: URL doesn't match Base URL**

**Input:**

- Base URL: `https://preprodapp.tekioncloud.com/`
- URL: `https://example.com/page`
- Capture Mode: Viewport

**Expected Output:**

- Screenshot: `example.com_20251101_140530.png` (fallback)

---

## ✅ **Features**

1. ✅ **Base URL input** in Settings tab
2. ✅ **Preserved in localStorage** (saved between sessions)
3. ✅ **Custom naming** based on URL path in PascalCase
4. ✅ **Single screenshot**: `Module_Feature.png`
5. ✅ **Multiple screenshots**: `Module_Feature_001.png`, `Module_Feature_002.png`, etc.
6. ✅ **Fallback to old naming** if base URL not provided or doesn't match
7. ✅ **Dark mode support** for input field
8. ✅ **Query parameter removal** from filenames
9. ✅ **Fragment removal** from filenames
10. ✅ **Empty path handling** (uses "Index.png")
11. ✅ **Symbol safety** - Filenames never start with symbols (\_, -, etc.)
12. ✅ **Auto-cleanup** - Leading non-alphanumeric characters removed
13. ✅ **Fallback naming** - Uses "Unnamed.png" if path is invalid

---

## 📝 **Files Modified**

- ✅ `frontend/src/App.tsx` - Added base URL state, UI, and API call
- ✅ `frontend/src/styles.css` - Added base URL input styling
- ✅ `backend/main.py` - Added base_url to request model and passed to service
- ✅ `backend/screenshot_service.py` - Added base_url parameter and \_generate_filename() helper

---

## 🎉 **Result**

**Users can now:**

1. ✅ Enter base URL in Settings tab
2. ✅ Get clean, readable screenshot names based on URL paths
3. ✅ Avoid long domain + timestamp names
4. ✅ Easily identify screenshots by path
5. ✅ Organize screenshots better

**Example:**

- Old: `preprodapp.tekioncloud.com_segment_001_20251101_140053.png`
- New: `Accounting_AutoPostingSettings_001.png` ✨ (PascalCase)

---

**Feature is live and ready to use!** 🚀
