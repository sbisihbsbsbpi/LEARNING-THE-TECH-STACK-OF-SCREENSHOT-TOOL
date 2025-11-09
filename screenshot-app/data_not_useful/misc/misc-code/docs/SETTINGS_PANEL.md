# ⚙️ Settings Panel - VS Code Style

## Overview
Implemented a **VS Code-style settings panel** that opens as a full-width window/tab when clicking the settings icon (⚙️). All capture mode options have been moved from the main view to the settings panel for a cleaner UI.

---

## ✨ Features

### **1. Settings Icon in Header** ⚙️
- Added settings icon (⚙️) next to logs (📋) and dark mode (🌙) icons
- Rotates 90° on hover, 180° when active
- Purple gradient background when active
- Smooth transitions and animations

### **2. VS Code-Style Settings Panel**
- Opens as a full-width panel (not a popup modal)
- Slides in from top with smooth animation
- Clean, organized layout with sections
- Close button to return to main view

### **3. All Capture Options Moved**
- **Capture Mode**: Viewport, Full Page, Segmented
- **Advanced Settings**: Overlap, Scroll Delay, Max Segments, Duplicate Detection, Smart Lazy Load
- **Stealth Mode**: Bypass bot detection
- **Real Browser Mode**: Visible Chrome window

### **4. Clean Main UI**
- Only URL input and capture button visible
- No clutter from checkboxes and options
- Focused, minimal interface

### **5. Dark Mode Support**
- Settings panel fully themed for dark mode
- Smooth color transitions
- Consistent with app theme

---

## 🎨 Visual Design

### **Main View (Settings Closed):**
```
┌─────────────────────────────────────────────────────┐
│ 📸 Screenshot Tool    ⚙️ 📋 🌙                    │
├─────────────────────────────────────────────────────┤
│ Enter URLs (one per line)         [✨ Beautify]    │
│ ┌──────┬────────────────────────────────────────┐  │
│ │   1  │ https://example.com                    │  │
│ │   2  │ https://google.com                     │  │
│ │      │                                        │  │
│ └──────┴────────────────────────────────────────┘  │
│                                                     │
│ [📸 Capture Screenshots]                            │
└─────────────────────────────────────────────────────┘
```

---

### **Settings View (Settings Open):**
```
┌─────────────────────────────────────────────────────┐
│ 📸 Screenshot Tool    ⚙️ 📋 🌙                    │
├─────────────────────────────────────────────────────┤
│ ⚙️ Settings                          [✕ Close]     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 📸 Capture Mode                                 │ │
│ │                                                 │ │
│ │ ○ 🖼️ Viewport only                              │ │
│ │   Single screenshot of visible area (1920x1080)│ │
│ │                                                 │ │
│ │ ● 📄 Full page                                  │ │
│ │   Single tall screenshot of entire page        │ │
│ │                                                 │ │
│ │ ○ 📚 Segmented                                  │ │
│ │   Multiple viewport screenshots                │ │
│ │                                                 │ │
│ │   [⚙️ Advanced Settings ▼]                      │ │
│ │   ┌───────────────────────────────────────────┐ │ │
│ │   │ Overlap: 20%                              │ │ │
│ │   │ Scroll delay: 1000ms                      │ │ │
│ │   │ Max segments: 50                          │ │ │
│ │   │ ☑ Skip duplicate segments                 │ │ │
│ │   │ ☑ Smart lazy-load detection               │ │ │
│ │   └───────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 🥷 Stealth Mode                                 │ │
│ │                                                 │ │
│ │ ☑ Use stealth mode (bypass bot detection)      │ │
│ │ ✅ Enabled: Hides automation, adds realistic   │ │
│ │    headers (80-90% success on protected sites) │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 🌐 Real Browser Mode                            │ │
│ │                                                 │ │
│ │ ☐ Use real browser (slower, visible window)    │ │
│ │ ⚠️ Disabled: Runs headless (invisible, faster) │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **App.tsx - State Management**

```typescript
// Settings panel visibility
const [showSettings, setShowSettings] = useState(false);
```

---

### **App.tsx - Settings Icon**

```tsx
<div className="header-controls">
  {/* Settings Toggle Button */}
  <button
    className={`settings-toggle ${showSettings ? "active" : ""}`}
    onClick={() => setShowSettings(!showSettings)}
    aria-label="Toggle settings"
    title={showSettings ? "Close settings" : "Open settings"}
  >
    <span className="icon-settings">⚙️</span>
  </button>

  {/* Logs Toggle Button */}
  {/* ... */}

  {/* Dark Mode Toggle Button */}
  {/* ... */}
</div>
```

---

### **App.tsx - Conditional Rendering**

```tsx
{/* Settings Panel */}
{showSettings ? (
  <div className="settings-panel">
    <div className="settings-header">
      <h2>⚙️ Settings</h2>
      <button
        className="close-settings-btn"
        onClick={() => setShowSettings(false)}
      >
        ✕ Close
      </button>
    </div>

    <div className="settings-content">
      {/* All capture options here */}
    </div>
  </div>
) : (
  /* Main View */
  <div className="input-section">
    {/* URL input and capture button */}
  </div>
)}
```

---

### **styles.css - Settings Toggle Button**

```css
.settings-toggle {
  background: transparent;
  border: 2px solid #ddd;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.settings-toggle:hover {
  transform: scale(1.1);
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.settings-toggle.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  transform: scale(1.1);
}

.icon-settings {
  font-size: 24px;
  transition: transform 0.3s ease;
}

.settings-toggle:hover .icon-settings {
  transform: rotate(90deg);
}

.settings-toggle.active .icon-settings {
  transform: rotate(180deg);
}
```

---

### **styles.css - Settings Panel**

```css
.settings-panel {
  background: #ffffff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  animation: slideIn 0.3s ease-out;
}

body.dark-mode .settings-panel {
  background: #2a2a2a;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.close-settings-btn {
  background: linear-gradient(135deg, #f44336 0%, #e53935 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.settings-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}
```

---

## 🎯 Benefits

| Feature | Before | After |
|---------|--------|-------|
| **Main UI** | Cluttered with options | Clean, minimal |
| **Settings Access** | Always visible | Hidden until needed |
| **Organization** | Mixed with input | Separate panel |
| **Visual Hierarchy** | Flat | Sectioned, organized |
| **User Focus** | Distracted by options | Focused on URLs |
| **Professional Look** | Basic | VS Code-inspired |

---

## 🧪 Testing

### **Test 1: Settings Icon**
1. Open http://localhost:1420
2. ✅ Settings icon (⚙️) visible in header
3. ✅ Icon rotates 90° on hover
4. ✅ Purple gradient on hover

---

### **Test 2: Open Settings**
1. Click settings icon (⚙️)
2. ✅ Settings panel slides in from top
3. ✅ Icon rotates 180° and shows purple background
4. ✅ Main view hidden

---

### **Test 3: Settings Content**
1. With settings open
2. ✅ All capture modes visible
3. ✅ Advanced settings expandable
4. ✅ Stealth mode checkbox
5. ✅ Real browser checkbox

---

### **Test 4: Close Settings**
1. Click "✕ Close" button
2. ✅ Settings panel closes
3. ✅ Main view returns
4. ✅ Settings icon returns to normal

---

### **Test 5: Settings Persistence**
1. Change capture mode to "Full Page"
2. Close settings
3. Open settings again
4. ✅ "Full Page" still selected

---

### **Test 6: Dark Mode**
1. Toggle dark mode
2. Open settings
3. ✅ Settings panel dark themed
4. ✅ All sections properly styled
5. ✅ Close button themed

---

## 📝 Files Modified

- ✅ `App.tsx` - Added settings state, icon, panel, conditional rendering
- ✅ `styles.css` - Added settings toggle and panel styles
- ✅ `SETTINGS_PANEL.md` - This documentation

---

## 🎉 Result

**Users can now:**

1. ✅ **See clean main UI** - Only URL input and capture button
2. ✅ **Click settings icon** - Opens VS Code-style panel
3. ✅ **Configure all options** - In organized sections
4. ✅ **Close settings** - Return to main view
5. ✅ **Settings persist** - Saved to localStorage
6. ✅ **Dark mode support** - Fully themed
7. ✅ **Smooth animations** - Professional feel

**Perfect VS Code-style settings panel!** ⚙️✨🎨

