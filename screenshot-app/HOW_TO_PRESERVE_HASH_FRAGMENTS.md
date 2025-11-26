# 📖 How to Preserve Hash Fragments in Filenames

**Quick Guide:** Enable unique filenames for URLs with different hash fragments (e.g., `#media-upload`, `#oem-details`)

---

## 🎯 What This Solves

**Problem:**
```
URL 1: https://example.com/page#section1
URL 2: https://example.com/page#section2

Both generate: Page_001.png (DUPLICATE!)
```

**Solution:**
```
URL 1: https://example.com/page#section1  →  Page_Section1.png ✅
URL 2: https://example.com/page#section2  →  Page_Section2.png ✅
```

---

## 🚀 Step-by-Step Setup

### **Step 1: Open Settings**

Click the **⚙️ Settings** icon in the top-right corner of the app.

---

### **Step 2: Find Word Transformations Section**

Scroll down to the **"🧹 Word Transformations"** section.

---

### **Step 3: Add `#` Transformation**

1. **Type `#` in the input box**
2. **Press Enter** (or click outside the box)
3. A new tag will appear: `# → [space]`

---

### **Step 4: Verify the Transformation**

You should see a blue tag that looks like this:

```
┌─────────────────┐
│ # → [space]  ×  │  ← Blue gradient tag
└─────────────────┘
```

**Optional:** Click the tag to edit and verify:
- **Word:** `#`
- **Replacement:** (empty, which means space)
- **Type:** `space`

---

### **Step 5: Test It!**

**Capture these two URLs:**
```
https://preprodapp.tekioncloud.com/core/setups/dealer-configuration/dealerDetails#media-upload
https://preprodapp.tekioncloud.com/core/setups/dealer-configuration/dealerDetails#oem-details
```

**Expected filenames:**
```
Core_Setups_DealerConfiguration_DealerDetails_MediaUpload.png
Core_Setups_DealerConfiguration_DealerDetails_OemDetails.png
```

**Word document headings:**
```
## Core Setups DealerConfiguration DealerDetails MediaUpload
## Core Setups DealerConfiguration DealerDetails OemDetails
```

---

## 🎨 Visual Example

### **Settings UI:**

```
┌─────────────────────────────────────────────────────────────┐
│ ⚙️ Settings                                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🧹 Word Transformations                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ┌─────────────────┐                                     │ │
│ │ │ # → [space]  ×  │  ← Your new transformation          │ │
│ │ └─────────────────┘                                     │ │
│ │                                                         │ │
│ │ [Add more...]                                           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Advanced: Custom Replacement

**Want to use a different separator instead of space?**

1. Click the `# → [space]` tag
2. Change **Type** to `custom`
3. Enter your custom replacement (e.g., `-`, `_`, `--`)
4. Click **💾 Save**

**Examples:**

| Replacement | URL                      | Filename                                    |
|-------------|--------------------------|---------------------------------------------|
| `(space)`   | `page#section`           | `Page_Section.png`                          |
| `-`         | `page#section`           | `Page-Section.png`                          |
| `_`         | `page#section`           | `Page_Section.png` (same as space)          |
| `--`        | `page#section`           | `Page--Section.png`                         |
| `""`        | `page#section`           | `PageSection.png` (no separator)            |

---

## ❓ FAQ

### **Q: Will this break my existing screenshots?**
**A:** No! This is opt-in. If you don't add `#` to transformations, hash fragments are removed (old behavior).

### **Q: What if I remove the `#` transformation later?**
**A:** Hash fragments will be removed again (back to old behavior). Existing screenshots won't be affected.

### **Q: Can I use this with query parameters too?**
**A:** Query parameters (e.g., `?module=SERVICE`) are already preserved by default. No transformation needed.

### **Q: What about other special characters?**
**A:** You can add transformations for any character:
- `?` → `_` (transform query params)
- `&` → `_And_` (transform ampersands)
- `=` → `_` (transform equals signs)

---

## 🎯 Real-World Example

**Your URLs:**
```
https://preprodapp.tekioncloud.com/core/setups/dealer-configuration/dealerDetails#media-upload
https://preprodapp.tekioncloud.com/core/setups/dealer-configuration/dealerDetails#oem-details
```

**With `#` transformation:**

**Filenames:**
```
Core_Setups_DealerConfiguration_DealerDetails_MediaUpload.png
Core_Setups_DealerConfiguration_DealerDetails_OemDetails.png
```

**Word Document:**
```
┌─────────────────────────────────────────────────────────────┐
│ Screenshot Documentation                                    │
│ Generated: 2025-11-13                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ## Core Setups DealerConfiguration DealerDetails MediaUpload│
│                                                             │
│ [Screenshot showing media upload section]                  │
│                                                             │
│ ## Core Setups DealerConfiguration DealerDetails OemDetails │
│                                                             │
│ [Screenshot showing OEM details section]                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Perfect! No duplicates! ✅**

---

## 🚀 You're All Set!

Just add `#` to word transformations and you'll get unique filenames for URLs with different hash fragments.

**Happy screenshotting! 📸**

