# 🔐 Auth State Monitor & Exporter

A Chrome extension that monitors and exports authentication data (cookies, localStorage, sessionStorage, tokens) for use with the screenshot automation tool.

---

## ✨ Features

### **Real-time Monitoring**
- 🍪 **Cookies** - Monitor all cookies on the current page
- 💾 **localStorage** - Track localStorage items
- 📦 **sessionStorage** - Track sessionStorage items
- 🔑 **Auth Tokens** - Automatically detect auth-related items

### **Smart Detection**
Automatically identifies auth-related items by looking for keywords:
- `token`, `auth`, `session`, `jwt`, `bearer`
- `access`, `refresh`, `sid`, `jsession`
- `user`, `login`, `credential`, `api_key`
- Tekion-specific: `t_token`, `dse_t_user`, `t_user`

### **Export Options**

1. **Playwright Storage State** (Recommended)
   - Exports in Playwright format
   - Includes cookies + localStorage + sessionStorage
   - Ready to use with screenshot tool
   - File: `auth_state.json`

2. **Individual Exports**
   - Export cookies only
   - Export localStorage only
   - Export sessionStorage only

3. **Auto-Save to Screenshot Tool**
   - One-click save to backend
   - Automatically sends to `http://127.0.0.1:8000/api/auth/save-from-extension`
   - No manual file copying needed!

---

## 📦 Installation

### **Method 1: Load Unpacked (Development)**

1. **Open Chrome Extensions page:**
   ```
   chrome://extensions/
   ```

2. **Enable Developer Mode:**
   - Toggle the switch in the top-right corner

3. **Load the extension:**
   - Click "Load unpacked"
   - Navigate to `screenshot-app/chrome-extension/`
   - Click "Select Folder"

4. **Extension installed!** ✅
   - You'll see the extension icon in your toolbar
   - Pin it for easy access

### **Method 2: Create Icons (Optional)**

The extension needs icons. You can either:

**Option A: Use placeholder icons**
- Create simple 16x16, 48x48, and 128x128 PNG files
- Save them in `chrome-extension/icons/`
- Name them: `icon16.png`, `icon48.png`, `icon128.png`

**Option B: Use emoji as icon (quick)**
- Use an online tool to convert 🔐 emoji to PNG
- Or use any lock/key icon you like

---

## 🚀 Usage

### **Basic Workflow:**

1. **Navigate to your app** (e.g., https://preprodapp.tekioncloud.com)

2. **Log in** (complete Okta/MFA/etc.)

3. **Wait for dashboard to load** (make sure no errors)

4. **Click the extension icon** in Chrome toolbar

5. **View real-time stats:**
   - See how many cookies, localStorage items, etc.
   - See detected auth tokens

6. **Export:**
   - Click "📥 Export for Screenshot Tool"
   - Save as `auth_state.json`
   - Move to `screenshot-app/backend/auth_state.json`

### **Auto-Save Workflow (Easier!):**

1. **Make sure screenshot tool backend is running:**
   ```bash
   cd screenshot-app/backend
   python main.py
   ```

2. **Navigate to your app and log in**

3. **Click the extension icon**

4. **Click "🚀 Auto-Save to Tool"**

5. **Done!** Auth state is automatically saved to backend

6. **Capture screenshots** - tool will use the saved auth state

---

## 🔧 Backend API Endpoint

The extension can auto-save to the backend via this endpoint:

```
POST http://127.0.0.1:8000/api/auth/save-from-extension
Content-Type: application/json

{
  "cookies": [...],
  "origins": [...]
}
```

You need to add this endpoint to your FastAPI backend (see below).

---

## 📝 Adding Backend Endpoint

Add this to `screenshot-app/backend/main.py`:

```python
@app.post("/api/auth/save-from-extension")
async def save_auth_from_extension(storage_state: dict):
    """Save auth state from Chrome extension"""
    try:
        # Save to auth_state.json
        with open(STORAGE_STATE_FILE, 'w') as f:
            json.dump(storage_state, f, indent=2)
        
        # Get stats
        cookie_count = len(storage_state.get('cookies', []))
        ls_count = sum(len(origin.get('localStorage', [])) for origin in storage_state.get('origins', []))
        
        return {
            "success": True,
            "message": "Auth state saved successfully",
            "cookie_count": cookie_count,
            "localStorage_count": ls_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🎯 Extension UI

The extension popup shows:

### **📍 Current Page**
- Displays the current URL

### **📊 Live Monitoring**
- **Cookies count** - Total cookies on page
- **localStorage count** - Total localStorage items
- **sessionStorage count** - Total sessionStorage items
- **Auth Tokens count** - Detected auth-related items

### **🔑 Detected Auth Items**
- Lists all detected auth tokens/cookies
- Shows name, truncated value, and source
- Scrollable list

### **📤 Export Options**
- Multiple export formats
- One-click downloads
- Auto-save to backend

---

## 🔍 How It Works

### **Content Script (`content.js`)**
- Runs in the context of web pages
- Has access to `localStorage` and `sessionStorage`
- Monitors storage changes in real-time
- Sends data to popup when requested

### **Background Script (`background.js`)**
- Service worker running in the background
- Handles message passing
- Updates badge with auth token count
- Monitors cookie changes

### **Popup (`popup.html/js/css`)**
- User interface
- Displays real-time stats
- Handles export functionality
- Communicates with content script and background

### **Permissions**
- `cookies` - Read cookies from all sites
- `storage` - Access chrome.storage API
- `activeTab` - Access current tab
- `tabs` - Query tabs
- `scripting` - Inject content scripts
- `<all_urls>` - Work on all websites

---

## 🎨 Customization

### **Add More Keywords**

Edit `popup.js` to detect more auth-related items:

```javascript
function isAuthRelated(name) {
  const keywords = [
    'token', 'auth', 'session', 'jwt', 'bearer',
    'access', 'refresh', 'sid', 'jsession',
    'user', 'login', 'credential', 'api_key',
    't_token', 'dse_t_user', 't_user',  // Tekion-specific
    'your_custom_keyword'  // Add your own!
  ];
  
  const lowerName = name.toLowerCase();
  return keywords.some(keyword => lowerName.includes(keyword));
}
```

### **Change Backend URL**

Edit `popup.js` to point to a different backend:

```javascript
const response = await fetch('http://your-backend-url:8000/api/auth/save-from-extension', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(storageState)
});
```

---

## 🐛 Troubleshooting

### **Extension not loading**
- Make sure Developer Mode is enabled
- Check for errors in `chrome://extensions/`
- Click "Errors" button if there are any

### **No data showing**
- Refresh the page you're monitoring
- Click the "🔄 Refresh Data" button
- Check browser console for errors

### **Auto-save failing**
- Make sure backend is running (`python main.py`)
- Check backend is on `http://127.0.0.1:8000`
- Check CORS settings in backend
- Look for errors in extension console

### **Icons not showing**
- Create placeholder PNG files in `icons/` folder
- Or remove icon references from `manifest.json`

---

## 🔒 Security Notes

⚠️ **Important:**

1. **This extension has access to sensitive data**
   - Cookies, tokens, localStorage
   - Only use on trusted sites
   - Don't share exported files

2. **Exported files contain credentials**
   - Treat `auth_state.json` like a password
   - Don't commit to git
   - Don't share with others

3. **Extension permissions**
   - Requires `<all_urls>` to work on all sites
   - Only install from trusted sources
   - Review code before installing

---

## 📚 Resources

- [Chrome Extension Documentation](https://developer.chrome.com/docs/extensions/)
- [Playwright Storage State](https://playwright.dev/docs/auth#reuse-signed-in-state)
- [Chrome Cookies API](https://developer.chrome.com/docs/extensions/reference/cookies/)

---

## 🎉 Summary

This extension makes it **super easy** to:
1. ✅ Monitor auth data in real-time
2. ✅ Export in Playwright format
3. ✅ Auto-save to screenshot tool
4. ✅ No manual copying needed!

**One-click auth state export!** 🚀

