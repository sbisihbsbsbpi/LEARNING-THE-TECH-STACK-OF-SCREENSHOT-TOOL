# 📦 Build and Distribution Guide

Complete guide for building and distributing the Screenshot Tool as a standalone macOS application.

---

## 🎯 Overview

The Screenshot Tool is distributed as a **native macOS application** (.dmg installer) that includes:

✅ **Bundled Components:**
- Tauri desktop app (native macOS UI)
- Python FastAPI backend (PyInstaller executable)
- Playwright Chromium browser (~400 MB)
- Chrome launcher helper script
- Empty Chrome profile template

❌ **User Must Install:**
- Google Chrome (only for Real Browser Mode)

**Total Bundle Size:** ~500-700 MB

---

## 🛠️ Build Process

### **Prerequisites**

1. **macOS** (10.15 or later)
2. **Node.js** 22.x
3. **Rust** (latest stable)
4. **Python** 3.12
5. **Xcode Command Line Tools**

### **Step 1: Install Dependencies**

```bash
# Backend dependencies
cd screenshot-app/backend
pip install -r requirements.txt
pip install pyinstaller

# Install Playwright browsers
python -m playwright install chromium

# Frontend dependencies
cd ../frontend
npm install
```

### **Step 2: Build Python Backend**

```bash
cd screenshot-app/backend
python build_backend.py
```

**What this does:**
- Bundles Python backend with PyInstaller
- Includes Playwright Chromium browser (~400 MB)
- Creates platform-specific binary (e.g., `screenshot-backend-aarch64-apple-darwin`)
- Copies binary to `frontend/src-tauri/binaries/`

**Output:**
```
dist/screenshot-backend-aarch64-apple-darwin  (~500 MB)
```

### **Step 3: Build Tauri App**

```bash
cd screenshot-app/frontend
npm run tauri build
```

**What this does:**
- Builds React frontend
- Bundles Python backend as sidecar
- Creates macOS .app bundle
- Creates DMG installer

**Output:**
```
src-tauri/target/release/bundle/dmg/frontend_0.1.0_aarch64.dmg  (~600-700 MB)
src-tauri/target/release/bundle/macos/frontend.app/
```

---

## 🚀 Distribution Methods

### **Method 1: GitHub Releases (Recommended)**

**Automated with GitHub Actions:**

1. **Create a version tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions automatically:**
   - Builds the app
   - Creates DMG installer
   - Uploads to GitHub Releases

3. **Users download from:**
   ```
   https://github.com/YOUR_USERNAME/YOUR_REPO/releases
   ```

**Manual Release:**

```bash
# Build locally
cd screenshot-app/backend && python build_backend.py
cd ../frontend && npm run tauri build

# Upload DMG to GitHub Releases
# Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/releases/new
# Upload: src-tauri/target/release/bundle/dmg/*.dmg
```

### **Method 2: TestFlight (Beta Testing)**

**Requirements:**
- Apple Developer Account ($99/year)
- App Store Connect access

**Steps:**

1. **Code Signing:**
   ```bash
   # Add to tauri.conf.json
   "bundle": {
     "macOS": {
       "signingIdentity": "Developer ID Application: Your Name (TEAM_ID)"
     }
   }
   ```

2. **Build for TestFlight:**
   ```bash
   npm run tauri build -- --target universal-apple-darwin
   ```

3. **Upload to App Store Connect:**
   - Use Transporter app
   - Upload the .app bundle
   - Submit for TestFlight review

4. **Invite beta testers**

### **Method 3: Direct Distribution**

**For internal use or small teams:**

1. **Build the DMG:**
   ```bash
   cd screenshot-app/frontend
   npm run tauri build
   ```

2. **Share the DMG file:**
   ```
   src-tauri/target/release/bundle/dmg/frontend_0.1.0_aarch64.dmg
   ```

3. **Users install:**
   - Download DMG
   - Open DMG
   - Drag app to Applications folder
   - Launch app

---

## 📋 User Installation Guide

### **Step 1: Download**

Download the DMG file from:
- GitHub Releases
- TestFlight
- Direct link

### **Step 2: Install**

1. Open the DMG file
2. Drag the app to Applications folder
3. Eject the DMG

### **Step 3: First Launch**

1. Open the app from Applications
2. If you see "App is damaged" error:
   ```bash
   xattr -cr /Applications/ScreenshotTool.app
   ```
3. App will automatically start the backend

### **Step 4: Using Real Browser Mode (Optional)**

1. Install Google Chrome from https://www.google.com/chrome/
2. In the app, enable "Real Browser Mode"
3. App will automatically launch Chrome with debugging
4. Start capturing screenshots

---

## 🔧 How It Works

### **App Startup Sequence**

1. **User launches app** → Tauri window opens
2. **Tauri starts backend sidecar** → Python FastAPI server starts on port 8000
3. **Frontend connects to backend** → React app communicates via HTTP
4. **User enables Real Browser Mode** → App launches Chrome with `--remote-debugging-port=9222`
5. **Backend connects to Chrome via CDP** → Screenshots captured from user's Chrome

### **Architecture**

```
┌─────────────────────────────────────────┐
│         macOS Application (.app)        │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │   Tauri (Rust + WebView)          │  │
│  │   - Native macOS window           │  │
│  │   - Launches backend sidecar      │  │
│  │   - Manages Chrome launcher       │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │   React Frontend                  │  │
│  │   - UI components                 │  │
│  │   - Settings management           │  │
│  │   - HTTP client to backend        │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │   Python Backend (Sidecar)        │  │
│  │   - FastAPI server (port 8000)    │  │
│  │   - Playwright automation         │  │
│  │   - Screenshot capture logic      │  │
│  │   - Bundled Chromium browser      │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │
         │ (Optional: Real Browser Mode)
         ↓
┌─────────────────────────────────────────┐
│   User's Chrome (CDP Connection)        │
│   - Launched with --remote-debugging    │
│   - Port 9222                           │
│   - User's login sessions               │
└─────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### **Build Issues**

**Problem:** PyInstaller fails to bundle Playwright browsers

**Solution:**
```bash
# Ensure browsers are installed
python -m playwright install chromium

# Check browser location
python -c "from pathlib import Path; print(Path.home() / 'Library/Caches/ms-playwright')"
```

**Problem:** Tauri build fails with "sidecar not found"

**Solution:**
```bash
# Verify backend binary exists
ls -lh screenshot-app/frontend/src-tauri/binaries/

# Rebuild backend
cd screenshot-app/backend && python build_backend.py
```

### **Runtime Issues**

**Problem:** App won't open (macOS Gatekeeper)

**Solution:**
```bash
# Remove quarantine attribute
xattr -cr /Applications/ScreenshotTool.app

# Or: System Preferences → Security & Privacy → Open Anyway
```

**Problem:** Backend doesn't start

**Solution:**
```bash
# Check logs in Console.app
# Search for: "screenshot-backend"

# Or run backend manually to see errors
cd /Applications/ScreenshotTool.app/Contents/MacOS/
./screenshot-backend-aarch64-apple-darwin
```

**Problem:** Chrome won't launch for Real Browser Mode

**Solution:**
```bash
# Verify Chrome is installed
ls -la "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# If not installed, download from:
# https://www.google.com/chrome/
```

---

## 📊 Bundle Size Breakdown

| Component | Size | Notes |
|-----------|------|-------|
| Tauri App | ~10 MB | Native macOS binary |
| React Frontend | ~5 MB | Compiled JavaScript |
| Python Backend | ~50 MB | PyInstaller bundle |
| Playwright Chromium | ~400 MB | Browser engine |
| Chrome Launcher | ~100 KB | Helper script |
| **Total** | **~465 MB** | Compressed in DMG: ~350 MB |

---

## ✅ Next Steps

1. **Test the build locally:**
   ```bash
   cd screenshot-app/backend && python build_backend.py
   cd ../frontend && npm run tauri build
   ```

2. **Install and test the DMG:**
   ```bash
   open src-tauri/target/release/bundle/dmg/*.dmg
   ```

3. **Create a GitHub release:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Share with beta testers**

5. **Iterate based on feedback**

---

**Status:** ✅ Ready for distribution!

