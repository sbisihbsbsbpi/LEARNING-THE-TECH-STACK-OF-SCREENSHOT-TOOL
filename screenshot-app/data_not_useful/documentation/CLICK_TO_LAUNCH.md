# 🖱️ Click to Launch - Like a Normal App!

**Just double-click the app icon to open in Chrome!**

---

## ✅ What I Created

You now have a **clickable app icon** that works just like Chrome, Slack, or any other app!

### **macOS App Bundle** 🍎

**File:** `Screenshot Tool.app`

**How to use:**

1. **Double-click** `Screenshot Tool.app`
2. App opens in **Chrome browser** automatically
3. Backend starts in background
4. Frontend loads at http://localhost:5173

**That's it!** Just like clicking Chrome! 🎉

---

## 🎯 How to Use

### **Step 1: Double-click the app**

Find `Screenshot Tool.app` in the `screenshot-app` folder and **double-click** it!

```
screenshot-app/
├── Screenshot Tool.app  ← Double-click this!
├── frontend/
├── backend/
└── ...
```

### **Step 2: App opens in Chrome**

- ✅ Backend starts automatically
- ✅ Frontend starts automatically
- ✅ Chrome opens to http://localhost:1420
- ✅ You see the Screenshot Tool UI!

### **Step 3: Use the app**

Use it normally! The UI is in Chrome, backend runs in the background.

### **Step 4: Close the app**

**Option 1:** Close the terminal window that opened

**Option 2:** Press Ctrl+C in the terminal window

Both frontend and backend will stop automatically!

---

## 🚀 Make It Even Better

### **Add to Dock (macOS)**

1. **Drag** `Screenshot Tool.app` to your **Dock**
2. Now you can click it from the Dock anytime!

### **Add to Applications (macOS)**

1. **Drag** `Screenshot Tool.app` to `/Applications` folder
2. Now it appears in Launchpad with all your other apps!

### **Create Desktop Shortcut**

1. **Drag** `Screenshot Tool.app` to your **Desktop**
2. Double-click from Desktop anytime!

---

## 📊 What Happens When You Click?

### **Behind the Scenes:**

```
1. You double-click "Screenshot Tool.app"
   ↓
2. App checks if backend is running
   ↓
3. If not, starts backend (FastAPI on port 8000)
   ↓
4. Checks if frontend is running
   ↓
5. If not, starts frontend (Vite on port 1420)
   ↓
6. Opens Chrome to http://localhost:1420
   ↓
7. You see the Screenshot Tool UI!
```

### **What You See:**

```
🚀 Launching Screenshot Tool...
📦 Starting backend...
⏳ Waiting for backend...
✅ Backend started
🎨 Starting frontend...
⏳ Waiting for frontend...
✅ Frontend started
🌐 Opening in browser...
✅ App is running!
📍 URL: http://localhost:1420
💡 Press Ctrl+C to stop the app
```

Then Chrome opens automatically!

---

## 🌐 Browser Support

### **Preferred: Chrome**

The app tries to open in **Chrome** first (best experience).

### **Fallback: Default Browser**

If Chrome is not installed, it opens in your default browser.

### **Supported Browsers:**

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Any modern browser

---

## 🔧 Advanced Options

### **Option 1: Use the App Icon** (Recommended)

```
Double-click "Screenshot Tool.app"
```

**Pros:**

- ✅ Just like any other app
- ✅ Can add to Dock/Applications
- ✅ Opens in Chrome automatically
- ✅ Easy for non-technical users

### **Option 2: Use the Script**

```bash
cd screenshot-app
./launch-app.sh
```

**Pros:**

- ✅ More control
- ✅ See detailed output
- ✅ Good for debugging

### **Option 3: Use npm**

```bash
cd screenshot-app
npm start
```

**Pros:**

- ✅ Opens Tauri desktop window (not browser)
- ✅ Native desktop app experience

---

## 🆚 Browser vs Desktop Window

### **Browser Mode** (What you have now)

**How:** Double-click `Screenshot Tool.app`

**Opens:** Chrome browser at http://localhost:1420

**Pros:**

- ✅ Familiar browser interface
- ✅ Can use browser DevTools
- ✅ Can open multiple tabs
- ✅ Faster development
- ✅ No Rust/Tauri build needed

**Cons:**

- ❌ Looks like a website
- ❌ Browser UI visible (address bar, etc.)

### **Desktop Window Mode**

**How:** Run `npm start` (uses Tauri)

**Opens:** Native desktop window

**Pros:**

- ✅ Looks like a native app
- ✅ No browser UI
- ✅ Can minimize to tray
- ✅ More "professional" look

**Cons:**

- ❌ Requires Rust/Tauri build
- ❌ Slower to start
- ❌ Harder to debug

---

## 💡 Recommendations

### **For Daily Use:**

Use the **app icon** (double-click `Screenshot Tool.app`)

**Why:**

- Quick and easy
- Opens in Chrome
- Just like any other app
- Can add to Dock

### **For Development:**

Use the **script** (`./launch-app.sh`)

**Why:**

- See detailed logs
- Better error messages
- More control

### **For Production/Distribution:**

Build the **Tauri desktop app** (`npm run build`)

**Why:**

- Native app experience
- No browser UI
- Can distribute to users

---

## 🐛 Troubleshooting

### **Problem: App doesn't open**

**Solution:** Make sure the script is executable

```bash
cd screenshot-app
chmod +x launch-app.sh
```

### **Problem: Chrome doesn't open**

**Solution:** The app will use your default browser instead. Or install Chrome:

```bash
# macOS
brew install --cask google-chrome
```

### **Problem: Backend fails to start**

**Solution:** Check the logs

```bash
cd screenshot-app
cat backend.log
```

### **Problem: Frontend fails to start**

**Solution:** Install dependencies

```bash
cd screenshot-app/frontend
npm install
```

### **Problem: Port already in use**

**Solution:** Kill existing processes

```bash
# Kill backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Kill frontend (port 5173)
lsof -ti:5173 | xargs kill -9
```

---

## 🎨 Customize the App

### **Change App Name**

Edit `create-mac-app.sh` and change:

```bash
APP_NAME="Screenshot Tool"
```

To:

```bash
APP_NAME="My Custom Name"
```

Then run:

```bash
bash create-mac-app.sh
```

### **Change App Icon**

Replace `frontend/src-tauri/icons/icon.icns` with your own icon, then run:

```bash
bash create-mac-app.sh
```

### **Change Browser**

Edit `launch-app.sh` and modify the browser opening section.

---

## 📚 Files Created

| File                  | Purpose                                               |
| --------------------- | ----------------------------------------------------- |
| `Screenshot Tool.app` | **Clickable app icon** (double-click to launch!)      |
| `launch-app.sh`       | Script that starts backend + frontend + opens browser |
| `create-mac-app.sh`   | Script to create the .app bundle                      |
| `CLICK_TO_LAUNCH.md`  | This guide                                            |

---

## 🎉 Summary

You can now launch your Screenshot Tool **just like Chrome**!

### **To Launch:**

1. **Double-click** `Screenshot Tool.app`
2. App opens in Chrome
3. Start using it!

### **To Stop:**

1. Close the terminal window
2. Or press Ctrl+C

### **To Add to Dock:**

1. Drag `Screenshot Tool.app` to Dock
2. Click from Dock anytime!

---

## 🚀 Quick Start

```bash
# First time: Create the app
cd screenshot-app
bash create-mac-app.sh

# Daily use: Just double-click!
# Double-click "Screenshot Tool.app"
```

**That's it!** 🎉

---

## 🆘 Need Help?

- **Logs:** `cat screenshot-app/backend.log`
- **Frontend logs:** `cat screenshot-app/frontend.log`
- **Health check:** http://127.0.0.1:8000/health
- **Direct URL:** http://localhost:1420

---

**Enjoy your click-to-launch app!** 🖱️✨
