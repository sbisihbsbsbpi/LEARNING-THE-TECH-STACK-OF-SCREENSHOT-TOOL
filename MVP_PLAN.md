# MVP Plan: Headless Screenshot Tool for macOS

## 🎯 Vision
A professional macOS app that captures full-page screenshots of websites and generates Word documents with embedded screenshots.

---

## 📊 Project Phases: Start Small → Scale Up

### **Phase 1: MVP (Minimum Viable Product)** ⭐ START HERE
**Goal**: Prove the core concept works with minimal features
**Timeline**: 1-2 days
**Status**: ✅ COMPLETE (Current Implementation)

#### Features
- ✅ Command-line interface (CLI)
- ✅ Manual URL input (one or multiple)
- ✅ Headless browser screenshot capture (Puppeteer + Chrome)
- ✅ Full-page screenshots (PNG)
- ✅ Word document generation (.docx)
- ✅ Basic error handling and retries
- ✅ Progress indicators

#### Tech Stack
- **Language**: Node.js (JavaScript/ES6)
- **Browser**: Puppeteer-core + System Chrome
- **Document**: docx npm package
- **CLI**: inquirer, ora, chalk
- **Images**: sharp

#### Why This First?
- ✅ Fastest to build and test
- ✅ Validates core functionality
- ✅ No GUI complexity
- ✅ Easy to debug
- ✅ Cross-platform foundation

#### Current Status
**COMPLETE** - All MVP features implemented and tested successfully.

---

### **Phase 2: Enhanced CLI** 🔄 NEXT STEP
**Goal**: Add power-user features while staying in CLI
**Timeline**: 2-3 days
**Status**: 📋 PLANNED

#### New Features
- [ ] Active browser tab detection (AppleScript)
  - Safari support
  - Chrome support
  - Brave support
  - Edge support
- [ ] Configuration file support (`.screenshotrc.json`)
- [ ] Batch processing from file (read URLs from .txt)
- [ ] Custom templates for Word documents
- [ ] PDF export option
- [ ] Screenshot annotations (optional text overlays)
- [ ] Scheduled captures (cron-like)

#### Tech Additions
- AppleScript integration (already implemented in current version)
- PDF generation: `pdfkit` or `puppeteer-pdf`
- Config: `cosmiconfig` or simple JSON
- Scheduling: `node-cron`

#### Why This Second?
- Adds real value without GUI complexity
- Tests macOS-specific features (AppleScript)
- Builds power-user base
- Validates market fit

---

### **Phase 3: Simple GUI (Electron)** 🖥️
**Goal**: Add a basic graphical interface
**Timeline**: 1 week
**Status**: 📋 PLANNED

#### Features
- [ ] Simple window with URL input fields
- [ ] "Add URL" and "Remove URL" buttons
- [ ] "Capture Active Tab" button
- [ ] Progress bar during capture
- [ ] Settings panel (viewport size, quality, etc.)
- [ ] Output folder selection
- [ ] Recent captures history

#### Tech Stack
- **Framework**: Electron (wraps existing Node.js code)
- **UI**: HTML + CSS + Vanilla JS (or React if needed)
- **State**: Simple localStorage or electron-store

#### Why Electron?
- ✅ Reuses 100% of existing Node.js code
- ✅ Cross-platform (macOS, Windows, Linux)
- ✅ Familiar web technologies
- ✅ Large ecosystem
- ✅ Easy to package (.app, .dmg)

#### Design Mockup (Simple)
```
┌─────────────────────────────────────────┐
│  Screenshot Tool                    ⚙️  │
├─────────────────────────────────────────┤
│                                         │
│  URLs to Capture:                       │
│  ┌───────────────────────────────────┐  │
│  │ https://example.com            [×]│  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ https://github.com             [×]│  │
│  └───────────────────────────────────┘  │
│                                         │
│  [+ Add URL]  [📋 Active Tab]           │
│                                         │
│  Output: [/Users/.../output/]  [Browse] │
│                                         │
│  [Capture Screenshots]                  │
│                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Capturing 2 of 5... (40%)              │
│                                         │
└─────────────────────────────────────────┘
```

---

### **Phase 4: Native macOS App (SwiftUI)** 🍎
**Goal**: Build a true native macOS experience
**Timeline**: 2-3 weeks
**Status**: 📋 FUTURE

#### Features
- [ ] Native SwiftUI interface
- [ ] macOS menu bar integration
- [ ] Drag & drop URL support
- [ ] Quick Actions (right-click in browser)
- [ ] Spotlight integration
- [ ] iCloud sync for settings
- [ ] Touch Bar support (if applicable)
- [ ] Notification Center integration

#### Tech Stack
- **Language**: Swift 5.9+
- **UI**: SwiftUI (macOS 13+)
- **Browser**: Keep Node.js + Puppeteer backend OR use WKWebView
- **IPC**: Swift ↔ Node.js communication (NDJSON, sockets, or XPC)

#### Architecture Options

**Option A: Hybrid (Swift UI + Node.js Backend)**
```
┌─────────────────┐
│   SwiftUI App   │
│   (Frontend)    │
└────────┬────────┘
         │ IPC (JSON)
┌────────▼────────┐
│  Node.js Server │
│  (Puppeteer)    │
└─────────────────┘
```
- Pros: Reuses existing code, proven screenshot engine
- Cons: Requires bundling Node.js

**Option B: Pure Swift (WKWebView)**
```
┌─────────────────┐
│   SwiftUI App   │
│   + WKWebView   │
│   + DocX Swift  │
└─────────────────┘
```
- Pros: Single binary, App Store friendly, smaller size
- Cons: WKWebView limitations (no true headless, harder full-page)

**Recommended**: Start with Option A (hybrid) for reliability, migrate to Option B later if needed.

#### Why Native Last?
- Most complex to build
- Requires Swift expertise
- App Store submission process
- Code signing & notarization
- But: Best user experience, best performance, best integration

---

### **Phase 5: Pro Features** 💎
**Goal**: Monetization and advanced features
**Timeline**: Ongoing
**Status**: 📋 FUTURE

#### Features
- [ ] Cloud storage integration (Dropbox, Google Drive, iCloud)
- [ ] Team collaboration (shared captures)
- [ ] API for automation
- [ ] Browser extensions (Chrome, Safari)
- [ ] Comparison mode (before/after screenshots)
- [ ] Video recording option
- [ ] OCR text extraction from screenshots
- [ ] Automated testing integration (CI/CD)
- [ ] Custom branding/watermarks
- [ ] Bulk operations (100s of URLs)

#### Monetization Options
- Free tier: 10 captures/month
- Pro tier: $9.99/month - unlimited captures
- Team tier: $29.99/month - shared workspace
- Enterprise: Custom pricing - API access, SSO

---

## 🎯 Current Recommendation: Stay in Phase 1 (MVP)

### What We Have Now (Phase 1 - COMPLETE)
✅ Fully functional CLI tool
✅ All core features working
✅ Tested and documented
✅ Ready to use

### What to Do Next

#### Option 1: **Validate & Iterate** (Recommended)
1. **Use the current tool** for real work
2. **Gather feedback** - What's missing? What's annoying?
3. **Identify pain points** - What would make it 10x better?
4. **Prioritize features** - What's the #1 most requested feature?
5. **Build that one thing** - Don't build everything at once

#### Option 2: **Jump to Phase 3** (GUI)
- If you need a GUI immediately
- Skip Phase 2 (Enhanced CLI)
- Build Electron wrapper around existing code
- Estimated: 3-5 days for basic GUI

#### Option 3: **Enhance Current MVP** (Phase 2)
- Add the features you personally need most
- Examples:
  - Better error messages
  - Faster captures (parallel processing)
  - More output formats (PDF, HTML)
  - Custom styling for documents

---

## 📋 Decision Framework

Ask yourself:
1. **Who is the user?**
   - Me only → Stay CLI (Phase 1)
   - Technical users → Enhanced CLI (Phase 2)
   - Non-technical users → GUI (Phase 3)
   - Mac enthusiasts → Native app (Phase 4)

2. **What's the goal?**
   - Personal tool → Current MVP is enough
   - Side project → Add features as needed
   - Product/startup → Build GUI (Phase 3)
   - App Store app → Native (Phase 4)

3. **How much time do you have?**
   - 1 day → Polish current MVP
   - 1 week → Add Phase 2 features
   - 1 month → Build Electron GUI
   - 3 months → Build native SwiftUI app

---

## 🚀 Recommended Next Steps

### Immediate (Today)
1. ✅ Test current MVP with real URLs
2. ✅ Verify Word documents look good
3. ✅ Check performance with 10+ URLs
4. ✅ Document any bugs or issues

### Short-term (This Week)
1. [ ] Decide: CLI or GUI?
2. [ ] If CLI: Pick 1-2 features from Phase 2
3. [ ] If GUI: Start Electron prototype
4. [ ] Create user feedback form

### Medium-term (This Month)
1. [ ] Complete Phase 2 OR Phase 3
2. [ ] Get 5-10 people to test it
3. [ ] Iterate based on feedback
4. [ ] Decide if Phase 4 (native) is worth it

---

## 💡 Key Principles

1. **Start Small** - MVP first, features later
2. **Validate Early** - Test with real users ASAP
3. **Iterate Fast** - Small improvements > big rewrites
4. **Stay Focused** - One phase at a time
5. **Ship Often** - Release early, release often

---

## 📊 Success Metrics

### Phase 1 (MVP) - Current
- ✅ Can capture any URL
- ✅ Can generate Word document
- ✅ Works reliably (>95% success rate)
- ✅ Documented and tested

### Phase 2 (Enhanced CLI)
- [ ] Active tab detection works 100%
- [ ] Config file reduces setup time
- [ ] 5+ power users actively using it

### Phase 3 (GUI)
- [ ] Non-technical users can use it
- [ ] <5 minutes to first screenshot
- [ ] 50+ downloads

### Phase 4 (Native)
- [ ] App Store approved
- [ ] 4+ star rating
- [ ] 500+ downloads

---

## 🎯 Bottom Line

**You have a working MVP (Phase 1).** ✅

**Next decision**: 
- **Use it** and see what you actually need
- **OR** jump to GUI if you know you need it

**Don't build Phase 4 until you've validated Phase 1-3.**

Start small. Ship fast. Iterate based on real feedback.

---

**Current Status**: Phase 1 Complete ✅  
**Recommended Next**: Validate with real use → Pick Phase 2 OR Phase 3  
**Timeline**: 1 week to decide, 1-2 weeks to build next phase

