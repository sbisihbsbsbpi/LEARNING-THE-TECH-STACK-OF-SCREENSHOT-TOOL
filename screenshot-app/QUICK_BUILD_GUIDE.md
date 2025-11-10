# ⚡ Quick Build Guide

Fast reference for building the Screenshot Tool.

---

## 🚀 One-Command Build

```bash
# From screenshot-app directory
cd backend && python build_backend.py && cd ../frontend && npm run tauri build
```

---

## 📝 Step-by-Step

### **1. Build Backend**

```bash
cd screenshot-app/backend
python build_backend.py
```

**Expected output:**
```
🚀 Screenshot Tool Backend - PyInstaller Build
🎯 Target platform: aarch64-apple-darwin
✅ Playwright browsers found
✅ Build successful!
📁 Output: dist/screenshot-backend-aarch64-apple-darwin
```

### **2. Build Frontend**

```bash
cd screenshot-app/frontend
npm run tauri build
```

**Expected output:**
```
    Finished 2 bundles at:
        /path/to/screenshot-app/frontend/src-tauri/target/release/bundle/dmg/frontend_0.1.0_aarch64.dmg
        /path/to/screenshot-app/frontend/src-tauri/target/release/bundle/macos/frontend.app
```

### **3. Test the DMG**

```bash
# Open the DMG
open src-tauri/target/release/bundle/dmg/*.dmg

# Install to Applications
# Drag app to Applications folder

# Launch
open /Applications/frontend.app
```

---

## 🧪 Testing Checklist

- [ ] App launches successfully
- [ ] Backend starts automatically (check Console.app logs)
- [ ] Frontend connects to backend (port 8000)
- [ ] Headless mode works (capture screenshots)
- [ ] Headful mode works (visible browser)
- [ ] Real Browser Mode detects Chrome
- [ ] Chrome launches with debugging (if installed)
- [ ] Settings persist across restarts
- [ ] Batch processing works
- [ ] Export to CSV works

---

## 🐛 Quick Troubleshooting

**Backend not found:**
```bash
ls -lh frontend/src-tauri/binaries/
# Should show: screenshot-backend-aarch64-apple-darwin
```

**Playwright browsers missing:**
```bash
python -m playwright install chromium
```

**Tauri build fails:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run tauri build
```

**App won't open (Gatekeeper):**
```bash
xattr -cr /Applications/frontend.app
```

---

## 📦 File Locations

**Backend binary:**
```
screenshot-app/backend/dist/screenshot-backend-aarch64-apple-darwin
screenshot-app/frontend/src-tauri/binaries/screenshot-backend-aarch64-apple-darwin
```

**DMG installer:**
```
screenshot-app/frontend/src-tauri/target/release/bundle/dmg/frontend_0.1.0_aarch64.dmg
```

**App bundle:**
```
screenshot-app/frontend/src-tauri/target/release/bundle/macos/frontend.app
```

---

## 🎯 Next Steps

1. **Test locally** → Install DMG and verify all features
2. **Create GitHub release** → `git tag v1.0.0 && git push origin v1.0.0`
3. **Share with testers** → Send DMG link
4. **Collect feedback** → Iterate and improve

---

**Need help?** See `BUILD_AND_DISTRIBUTION.md` for detailed guide.

