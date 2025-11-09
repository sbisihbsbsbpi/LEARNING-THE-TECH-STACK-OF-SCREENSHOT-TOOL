# 🗂️ Miscellaneous Code Archive

This folder contains files that are **not actively used** in the production application but are kept for reference, testing, or historical purposes.

---

## 📋 File Categories

### **1. Documentation Files (Moved from Root)**

These are implementation notes, research documents, and feature documentation that clutter the main directory:

#### **Stealth Mode Research & Implementation**
- `ADVANCED_STEALTH_RESEARCH_2025.md` - Comprehensive web research on 2025 stealth techniques
- `STEALTH_2025_COMPLETE.md` - Quick summary of stealth implementation
- `STEALTH_QUICK_START.md` - Quick reference guide for stealth modes
- `STEALTH_MODE_IMPROVEMENTS.md` - Original stealth mode improvements doc
- `IMPLEMENTATION_COMPLETE.md` - Implementation completion summary

#### **Feature Documentation**
- `AUTH_SETUP.md` - Authentication setup guide
- `BASE_URL_FEATURE.md` - Base URL feature documentation
- `BEAUTIFY_CONCATENATED_URLS.md` - URL beautification feature
- `BEAUTIFY_UPDATE.md` - Beautification updates
- `BEAUTIFY_URLS.md` - URL beautification guide
- `CHROME_TABS.md` - Chrome tabs feature
- `LOGS_FEATURE.md` - Logs feature documentation
- `LOGS_FIX.md` - Logs fixes
- `LOGS_INDICATOR.md` - Logs indicator feature
- `LOGS_TAB_SMALLER_ICONS.md` - UI improvements for logs
- `SETTINGS_PANEL.md` - Settings panel documentation
- `STOP_BUTTON_FEATURE.md` - Stop button feature
- `URL_LINE_NUMBERS.md` - URL line numbers feature
- `ANIMATED_ICONS.md` - Animated icons feature

#### **Debugging & Development**
- `DEBUGGING_REPORT.md` - Debugging reports
- `DEBUG_REPORT.md` - Debug reports
- `DEV_WORKFLOW.md` - Development workflow guide
- `LINE_NUMBERS_DEBUG.md` - Line numbers debugging
- `SEGMENTED_CAPTURE_FIXES.md` - Segmented capture fixes
- `UI_ENHANCEMENTS.md` - UI enhancements documentation
- `UI_IMPROVEMENTS.md` - UI improvements documentation

**Why moved:** These are historical documentation files that describe features already implemented. They're useful for reference but clutter the main directory.

---

### **2. Backend Test & Utility Scripts**

#### **Test Scripts**
- `test_improvements.py` - Tests for Phase 1, 2, 3 improvements
- `test_stealth.py` - Original stealth mode tests
- `test_stealth_2025.py` - 2025 stealth enhancements tests
- `check_stealth_install.py` - Stealth package installation checker
- `install_patchright.py` - Patchright installation script

**Why moved:** These are development/testing scripts not needed in production. They're useful for debugging but not part of the core application.

#### **Backend Documentation**
- `PHASE1_CHANGES.md` - Phase 1 implementation notes
- `PHASE2_CHANGES.md` - Phase 2 implementation notes
- `PHASE3_CHANGES.md` - Phase 3 implementation notes
- `STEALTH_2025_IMPLEMENTATION.md` - Stealth implementation guide
- `STEALTH_ENHANCEMENTS_IMPLEMENTED.md` - Stealth enhancements summary

**Why moved:** Historical documentation of development phases. Useful for understanding the evolution but not needed for daily development.

---

### **3. Chrome Extension (Separate Tool)**

The `chrome-extension/` folder is a **separate tool** for exporting cookies/localStorage from Chrome:

**Files:**
- `manifest.json` - Chrome extension manifest
- `popup.html` - Extension popup UI
- `popup.js` - Extension popup logic
- `popup.css` - Extension styling
- `background.js` - Background script
- `content.js` - Content script
- `create-icons.py` - Icon generation script
- `INSTALL.md` - Installation guide
- `README.md` - Extension documentation

**Why separate:** This is a standalone Chrome extension that helps users export auth state. It's not part of the main Tauri desktop app. Users who need it can install it separately.

---

### **4. Diagnostics Tools (Separate Tool)**

The `diagnostics/` folder contains **debugging scripts** for troubleshooting auth issues:

**Files:**
- `step1-capture-fresh.js` - Capture fresh auth state
- `step2-verify-session.js` - Verify session data
- `step3-debug-cookies.js` - Debug cookie issues
- `step4-test-with-stealth.js` - Test stealth mode
- `step5-test-real-capture.js` - Test real capture
- `test-auth-state.py` - Python auth state tester
- `package.json` - Node.js dependencies
- `QUICKSTART.md` - Quick start guide
- `README.md` - Diagnostics documentation

**Why separate:** These are diagnostic tools for troubleshooting. Most users won't need them. Developers can use them when debugging auth issues.

---

### **5. Utility Scripts (Root Level)**

- `save-auth-manual.js` - Manual auth state saver (Node.js)
- `save-auth-manual.py` - Manual auth state saver (Python)
- `start.sh` - Backend/frontend startup script
- `restart.sh` - Restart script
- `r` - Quick restart script

**Why kept in root:** These are convenience scripts that developers use frequently. Keeping them in root makes them easy to access.

---

## 🎯 Core Application Files (NOT Moved)

These files are **actively used** in production and should **NOT** be moved:

### **Backend (Python/FastAPI)**
- ✅ `main.py` - FastAPI application entry point
- ✅ `screenshot_service.py` - Screenshot capture service (1,800+ lines)
- ✅ `document_service.py` - Word document generation
- ✅ `quality_checker.py` - Screenshot quality validation
- ✅ `logging_config.py` - Structured logging configuration
- ✅ `config.py` - Centralized configuration (Pydantic)
- ✅ `requirements.txt` - Python dependencies
- ✅ `auth_state.json` - Saved authentication state (runtime)

### **Frontend (React/TypeScript)**
- ✅ `src/App.tsx` - Main React application (3,600+ lines)
- ✅ `src/main.tsx` - React entry point
- ✅ `src/styles.css` - Application styles
- ✅ `src/hooks/useDebouncedLocalStorage.ts` - Custom React hook
- ✅ `package.json` - Node.js dependencies
- ✅ `vite.config.ts` - Vite configuration
- ✅ `tsconfig.json` - TypeScript configuration
- ✅ `index.html` - HTML entry point

### **Documentation (Root Level)**
- ✅ `README.md` - Main project documentation
- ✅ `QUICKSTART.md` - Quick start guide
- ✅ `WHAT_WE_BUILT.md` - Project overview

---

## 📊 Impact Analysis

### **Before Cleanup:**
```
screenshot-app/
├── 29 documentation files (cluttered root)
├── 5 backend test scripts (mixed with production code)
├── 5 backend documentation files (mixed with production code)
├── chrome-extension/ (8 files - separate tool)
├── diagnostics/ (8 files - separate tool)
└── Core application files
```

### **After Cleanup:**
```
screenshot-app/
├── README.md (main docs)
├── QUICKSTART.md (quick start)
├── WHAT_WE_BUILT.md (overview)
├── backend/ (only production code)
│   ├── main.py
│   ├── screenshot_service.py
│   ├── document_service.py
│   ├── quality_checker.py
│   ├── logging_config.py
│   ├── config.py
│   └── requirements.txt
├── frontend/ (only production code)
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── styles.css
│       └── hooks/
└── misc-code/ (archived files)
    ├── docs/ (29 documentation files)
    ├── backend-tests/ (5 test scripts)
    ├── backend-docs/ (5 documentation files)
    ├── chrome-extension/ (separate tool)
    └── diagnostics/ (separate tool)
```

---

## 🚀 Benefits

1. **✅ Cleaner Project Structure** - Only production code in main directories
2. **✅ Faster Navigation** - Easier to find core files
3. **✅ Better Focus** - Developers see only what matters
4. **✅ Preserved History** - All files still accessible in `misc-code/`
5. **✅ Easier Onboarding** - New developers see clean structure
6. **✅ Better Git Diffs** - Less noise in version control

---

## 📖 How to Use This Folder

### **If you need to reference old documentation:**
```bash
cd screenshot-app/misc-code/docs
ls -la
```

### **If you need to run tests:**
```bash
cd screenshot-app/misc-code/backend-tests
python3 test_stealth_2025.py
```

### **If you need the Chrome extension:**
```bash
cd screenshot-app/misc-code/chrome-extension
# Follow INSTALL.md
```

### **If you need diagnostics:**
```bash
cd screenshot-app/misc-code/diagnostics
npm install
node step1-capture-fresh.js
```

---

## ⚠️ Important Notes

1. **Don't delete this folder** - It contains valuable reference material
2. **Don't move core files here** - Only move documentation and test files
3. **Update this README** - If you move more files, document them here
4. **Git history preserved** - All files maintain their git history

---

## 🎯 Next Steps

After moving files to `misc-code/`:

1. ✅ Update `.gitignore` to exclude `misc-code/` from main tracking (optional)
2. ✅ Update main `README.md` to reference this folder
3. ✅ Test that application still works (no broken imports)
4. ✅ Commit changes with clear message

---

**Last Updated:** 2025-11-02  
**Maintained By:** Development Team

