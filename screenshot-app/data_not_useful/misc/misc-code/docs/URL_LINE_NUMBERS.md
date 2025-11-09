# 🔢 URL Line Numbers - Transparent Serial Numbers

## Overview
Added **transparent line numbers** to the URL textarea that automatically show serial numbers (1, 2, 3...) for each URL entered. The numbers are **embedded transparently** as an overlay and update dynamically as URLs are added or removed.

---

## ✨ Features

### 1. **Transparent Line Numbers**
- Serial numbers appear on the left side of the textarea
- Semi-transparent (30% opacity) - not distracting
- Monospace font matching the textarea
- Vertical border separating numbers from text

### 2. **Dynamic Auto-Update**
- **Add URL** → Next number appears automatically
- **Remove URL** → Numbers renumber automatically
- **Empty line** → No number shown
- **Real-time** → Updates as you type

### 3. **Non-Editable**
- Line numbers are **visual only** (overlay)
- Cannot be selected or copied
- Not part of the actual text content
- `user-select: none` and `pointer-events: none`

### 4. **Dark Mode Compatible**
- Light mode: Dark gray numbers (rgba(0,0,0,0.3))
- Dark mode: Light gray numbers (rgba(255,255,255,0.3))
- Subtle gradient background
- Themed border color

---

## 🎨 Visual Design

### **Light Mode:**
```
┌────────────────────────────────────────┐
│ 1 │ https://example.com              │
│ 2 │ https://google.com               │
│ 3 │ https://github.com               │
│   │                                  │
│   │                                  │
└────────────────────────────────────────┘
    ↑
  Line numbers
  (transparent gray)
```

### **Dark Mode:**
```
┌────────────────────────────────────────┐
│ 1 │ https://example.com              │
│ 2 │ https://google.com               │
│ 3 │ https://github.com               │
│   │                                  │
│   │                                  │
└────────────────────────────────────────┘
    ↑
  Line numbers
  (transparent white)
```

---

## 🎯 Behavior Examples

### **Example 1: Adding URLs**

**Step 1 - Empty:**
```
┌────────────────────────────────────────┐
│   │                                  │
│   │                                  │
└────────────────────────────────────────┘
```

**Step 2 - Add first URL:**
```
┌────────────────────────────────────────┐
│ 1 │ https://example.com              │
│   │                                  │
└────────────────────────────────────────┘
```

**Step 3 - Add second URL:**
```
┌────────────────────────────────────────┐
│ 1 │ https://example.com              │
│ 2 │ https://google.com               │
│   │                                  │
└────────────────────────────────────────┘
```

**Step 4 - Add third URL:**
```
┌────────────────────────────────────────┐
│ 1 │ https://example.com              │
│ 2 │ https://google.com               │
│ 3 │ https://github.com               │
│   │                                  │
└────────────────────────────────────────┘
```

---

### **Example 2: Removing URLs**

**Before - 3 URLs:**
```
┌────────────────────────────────────────┐
│ 1 │ https://example.com              │
│ 2 │ https://google.com               │
│ 3 │ https://github.com               │
└────────────────────────────────────────┘
```

**After - Delete line 2:**
```
┌────────────────────────────────────────┐
│ 1 │ https://example.com              │
│ 2 │ https://github.com               │  ← Renumbered!
│   │                                  │
└────────────────────────────────────────┘
```

---

### **Example 3: Empty Lines**

**With empty lines:**
```
┌────────────────────────────────────────┐
│ 1 │ https://example.com              │
│   │                                  │  ← No number
│ 2 │ https://google.com               │
│   │                                  │  ← No number
│ 3 │ https://github.com               │
└────────────────────────────────────────┘
```

**Behavior:**
- Empty lines don't get numbers
- Only lines with content get numbered
- Numbers skip empty lines

---

## 💻 Implementation

### **App.tsx Changes**

**Old Structure:**
```tsx
<div className="input-section">
  <h2>Enter URLs (one per line)</h2>
  <textarea
    value={urls}
    onChange={(e) => setUrls(e.target.value)}
    placeholder="..."
    rows={10}
    disabled={loading}
  />
</div>
```

**New Structure:**
```tsx
<div className="input-section">
  <h2>Enter URLs (one per line)</h2>
  <div className="textarea-wrapper">
    {/* Line numbers overlay */}
    <div className="line-numbers">
      {urls.split("\n").map((line, index) => (
        <div key={index} className="line-number">
          {line.trim() !== "" ? index + 1 : ""}
        </div>
      ))}
    </div>
    {/* Textarea */}
    <textarea
      value={urls}
      onChange={(e) => setUrls(e.target.value)}
      placeholder="..."
      rows={10}
      disabled={loading}
      className="numbered-textarea"
    />
  </div>
</div>
```

**Key Points:**
- Wrapper div with `position: relative`
- Line numbers div with `position: absolute`
- Split URLs by newline to count lines
- Show number only if line is not empty (`line.trim() !== ""`)
- Each line gets sequential number (index + 1)

---

### **styles.css Changes**

#### **1. Textarea Wrapper**
```css
.textarea-wrapper {
  position: relative;
  width: 100%;
  margin-bottom: 15px;
}
```

#### **2. Line Numbers Overlay**
```css
.line-numbers {
  position: absolute;
  left: 0;
  top: 0;
  padding: 15px 0;
  padding-left: 8px;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.5;
  color: rgba(0, 0, 0, 0.3);
  user-select: none;        /* Cannot select */
  pointer-events: none;     /* Cannot interact */
  z-index: 1;
  width: 35px;
  text-align: right;
  border-right: 2px solid rgba(0, 0, 0, 0.1);
  background: linear-gradient(
    to right,
    rgba(0, 0, 0, 0.02) 0%,
    rgba(0, 0, 0, 0) 100%
  );
}
```

**Dark Mode:**
```css
body.dark-mode .line-numbers {
  color: rgba(255, 255, 255, 0.3);
  border-right-color: rgba(255, 255, 255, 0.1);
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0.03) 0%,
    rgba(255, 255, 255, 0) 100%
  );
}
```

#### **3. Individual Line Number**
```css
.line-number {
  height: 21px;           /* Match line height */
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  font-weight: 500;
}
```

#### **4. Numbered Textarea**
```css
.numbered-textarea {
  width: 100%;
  padding: 15px;
  padding-left: 50px;     /* Space for line numbers */
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: monospace;
  line-height: 1.5;       /* Match line numbers */
  resize: vertical;
  background: white;
  color: #333;
  position: relative;
  z-index: 2;             /* Above line numbers */
}
```

---

## 🎨 Design Details

### **Spacing:**
- Line numbers width: 35px
- Textarea left padding: 50px (35px + 15px gap)
- Line height: 1.5 (21px at 14px font)
- Vertical padding: 15px (matches textarea)

### **Colors:**

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| **Numbers** | rgba(0,0,0,0.3) | rgba(255,255,255,0.3) |
| **Border** | rgba(0,0,0,0.1) | rgba(255,255,255,0.1) |
| **Background** | rgba(0,0,0,0.02) | rgba(255,255,255,0.03) |

### **Typography:**
- Font: Monospace (matches textarea)
- Size: 14px (matches textarea)
- Weight: 500 (medium)
- Alignment: Right-aligned

---

## 🧪 Testing

### **Test 1: Add URLs**
1. Open http://localhost:1420
2. Click in textarea
3. Type: `https://example.com`
4. ✅ Should see "1" on the left
5. Press Enter, type: `https://google.com`
6. ✅ Should see "2" on the left
7. Press Enter, type: `https://github.com`
8. ✅ Should see "3" on the left

---

### **Test 2: Remove URLs**
1. Have 3 URLs (numbered 1, 2, 3)
2. Delete line 2 (middle URL)
3. ✅ Line 3 should renumber to "2"
4. ✅ Only 2 numbers visible (1, 2)

---

### **Test 3: Empty Lines**
1. Type URL: `https://example.com`
2. ✅ Shows "1"
3. Press Enter twice (empty line)
4. ✅ No number on empty line
5. Type URL: `https://google.com`
6. ✅ Shows "2" (skipped empty line)

---

### **Test 4: Non-Editable**
1. Try to click on line numbers
2. ✅ Click passes through to textarea
3. Try to select line numbers
4. ✅ Cannot select numbers
5. Try to copy line numbers
6. ✅ Numbers not included in copy

---

### **Test 5: Dark Mode**
1. Toggle dark mode
2. ✅ Line numbers turn light gray
3. ✅ Border turns light gray
4. ✅ Background gradient adjusts
5. ✅ Still readable and subtle

---

## 📊 Benefits

| Benefit | Description |
|---------|-------------|
| **Visual Clarity** | Easy to see how many URLs are entered |
| **Auto-Update** | Numbers adjust automatically |
| **Non-Intrusive** | Transparent, doesn't distract |
| **Professional** | Looks like a code editor |
| **User-Friendly** | Clear visual feedback |
| **Dark Mode** | Works in both themes |
| **Clean Copy** | Numbers not copied with text |

---

## 🎉 Result

**Users now see:**

1. ✅ **Serial numbers** (1, 2, 3...) for each URL
2. ✅ **Transparent overlay** - not editable text
3. ✅ **Auto-renumbering** when URLs added/removed
4. ✅ **Empty lines skipped** - only content gets numbered
5. ✅ **Dark mode compatible** - themed colors
6. ✅ **Professional look** - like a code editor
7. ✅ **Clean copy/paste** - numbers not included

**Perfect for tracking how many URLs are in the list!** 🔢✨

