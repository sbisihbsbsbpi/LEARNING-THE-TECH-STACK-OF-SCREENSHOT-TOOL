# 🚀 Installation Guide - Auth State Monitor Extension

Quick guide to install and use the Chrome extension.

---

## 📦 Step 1: Create Icons

The extension needs icons. Choose one option:

### **Option A: Generate Icons with Python (Recommended)**

```bash
cd screenshot-app/chrome-extension
pip install pillow
python create-icons.py
```

This creates:
- `icons/icon16.png` (16x16)
- `icons/icon48.png` (48x48)
- `icons/icon128.png` (128x128)

### **Option B: Use Emoji Icons (Quick)**

1. Go to https://emojipedia.org/locked/
2. Right-click the 🔐 emoji and save as PNG
3. Resize to 16x16, 48x48, and 128x128
4. Save in `chrome-extension/icons/`

### **Option C: Skip Icons (Temporary)**

Remove icon references from `manifest.json`:

```json
{
  "manifest_version": 3,
  "name": "Auth State Monitor & Exporter",
  "version": "1.0.0",
  "description": "Monitor and export cookies, localStorage, sessionStorage, and tokens",
  "permissions": [
    "cookies",
    "storage",
    "activeTab",
    "tabs",
    "scripting"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "action": {
    "default_popup": "popup.html"
  },
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"],
      "run_at": "document_idle"
    }
  ]
}
```

---

## 🔧 Step 2: Install Extension in Chrome

1. **Open Chrome Extensions page:**
   - Type `chrome://extensions/` in address bar
   - Or: Menu → More Tools → Extensions

2. **Enable Developer Mode:**
   - Toggle switch in top-right corner

3. **Load the extension:**
   - Click "Load unpacked" button
   - Navigate to `screenshot-app/chrome-extension/`
   - Click "Select Folder"

4. **Extension installed!** ✅
   - You'll see "Auth State Monitor & Exporter" in the list
   - Extension icon appears in toolbar
   - Click the puzzle icon and pin it for easy access

---

## 🎯 Step 3: Test the Extension

1. **Navigate to a website** (e.g., https://preprodapp.tekioncloud.com)

2. **Log in** (complete authentication)

3. **Click the extension icon** in Chrome toolbar

4. **You should see:**
   - Current URL
   - Cookie count
   - localStorage count
   - sessionStorage count
   - Detected auth tokens

---

## 🚀 Step 4: Use with Screenshot Tool

### **Method 1: Manual Export**

1. **Click extension icon**
2. **Click "📥 Export for Screenshot Tool"**
3. **Save as `auth_state.json`**
4. **Move file to `screenshot-app/backend/auth_state.json`**
5. **Capture screenshots!**

### **Method 2: Auto-Save (Recommended)**

1. **Start the backend:**
   ```bash
   cd screenshot-app/backend
   python main.py
   ```

2. **Navigate to your app and log in**

3. **Click extension icon**

4. **Click "🚀 Auto-Save to Tool"**

5. **Done!** Auth state is automatically saved

6. **Capture screenshots** - tool will use the saved auth

---

## 🔍 Troubleshooting

### **Extension not showing in toolbar**
- Click the puzzle icon (Extensions)
- Find "Auth State Monitor & Exporter"
- Click the pin icon to pin it

### **"Manifest file is missing or unreadable" error**
- Make sure you selected the `chrome-extension` folder
- Check that `manifest.json` exists in the folder

### **"Icons not found" error**
- Either create icons (see Step 1)
- Or remove icon references from manifest.json

### **No data showing in popup**
- Refresh the page you're monitoring
- Click "🔄 Refresh Data" button
- Check browser console for errors (F12)

### **Auto-save failing**
- Make sure backend is running on port 8000
- Check backend logs for errors
- Try manual export instead

### **CORS errors when auto-saving**
- Backend should allow requests from `chrome-extension://`
- Check FastAPI CORS middleware settings

---

## 📝 Quick Reference

### **Extension Files:**
```
chrome-extension/
├── manifest.json       # Extension configuration
├── popup.html          # UI layout
├── popup.css           # UI styling
├── popup.js            # UI logic & export functions
├── content.js          # Runs in web pages (access to storage)
├── background.js       # Background service worker
├── icons/              # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
├── README.md           # Full documentation
├── INSTALL.md          # This file
└── create-icons.py     # Icon generator script
```

### **Keyboard Shortcuts:**
- None by default (can be added in manifest.json)

### **Permissions:**
- `cookies` - Read cookies
- `storage` - Use chrome.storage API
- `activeTab` - Access current tab
- `tabs` - Query tabs
- `scripting` - Inject content scripts
- `<all_urls>` - Work on all websites

---

## 🎉 You're Done!

The extension is now installed and ready to use!

**Next steps:**
1. Navigate to your app
2. Log in
3. Click extension icon
4. Export or auto-save auth state
5. Use with screenshot tool

**Happy screenshotting!** 🚀

