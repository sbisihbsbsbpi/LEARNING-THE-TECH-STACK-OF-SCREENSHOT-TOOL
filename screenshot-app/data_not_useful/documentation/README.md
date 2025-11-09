# 📸 Screenshot Tool

A professional desktop application for bulk screenshot capture with quality checks and document generation.

**Built with**: Tauri + React + FastAPI + Playwright

---

## ⚡ Quick Start (One Command!)

```bash
npm start
```

That's it! This starts both frontend and backend automatically. 🚀

**See [START_GUIDE.md](./START_GUIDE.md) for detailed instructions.**

---

## ✨ Features

- ✅ **Bulk Screenshot Capture** - Capture 100+ URLs at once
- ✅ **Active Tab Mode** - 🆕 Use your existing Chrome browser's active tab
- ✅ **3-Tier Stealth System** - Playwright → Rebrowser → Camoufox
- ✅ **Multiple Capture Modes** - Viewport, Fullpage, Segmented
- ✅ **Auth State Management** - Save cookies & localStorage for login-protected sites
- ✅ **Quality Checks** - Auto-detect blank pages, errors, and quality issues
- ✅ **Review UI** - Accept/Retry/Reject screenshots
- ✅ **Document Generation** - Generate Word .docx with screenshots
- ✅ **Session Management** - Save and reuse configurations
- ✅ **URL Organization** - Organize URLs into folders
- ✅ **Real-time Progress** - WebSocket updates
- ✅ **Cross-platform** - macOS, Windows, Linux

---

## 🚀 All Start Options

### **Option 1: npm (Recommended)**

```bash
npm start
```

### **Option 2: Bash script**

```bash
bash start.sh
```

### **Option 3: Execute directly**

```bash
./start.sh
```

### **Option 4: Manual (Old Way)**

**Terminal 1 - Backend:**

```bash
cd backend
python3 main.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run tauri dev
```

---

## 📦 Installation

### **Prerequisites**

- Python 3.12+
- Node.js 22+
- Rust 1.91+

### **Install Dependencies**

#### **Backend**:

```bash
cd backend
pip3 install -r requirements.txt
playwright install chromium
```

#### **Frontend**:

```bash
cd frontend
npm install
```

---

## 🎯 How to Use

### **Standard Mode (Automated)**

1. **Launch the app** (see Quick Start above)
2. **Enter URLs** (one per line) in the text area
3. **Click "Capture Screenshots"**
4. **Review results** - See quality scores and issues
5. **Retry failed screenshots** - Click "🔄 Retry" button
6. **Generate document** - Click "Generate Word Document"
7. **Find your document** in `backend/output/screenshots_report.docx`

### **Active Tab Mode (Visual)** 🆕

Use your existing Chrome browser's active tab for screenshots:

1. **Launch Chrome with debugging**:
   ```bash
   ./launch-chrome-debug.sh
   ```
2. **Enable "Real Browser" mode** in Settings
3. **Enter URLs** and click "Capture Screenshots"
4. **Watch** as URLs load in your active Chrome tab
5. Screenshots are captured while you watch!

**See [ACTIVE_TAB_MODE.md](./ACTIVE_TAB_MODE.md) for full details.**

---

## 📁 Project Structure

```
screenshot-app/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Main API server
│   ├── screenshot_service.py  # Playwright screenshot capture
│   ├── quality_checker.py     # Quality checks
│   ├── document_service.py    # Word document generation
│   ├── requirements.txt       # Python dependencies
│   ├── screenshots/           # Captured screenshots (auto-created)
│   └── output/                # Generated documents (auto-created)
│
└── frontend/                  # Tauri + React frontend
    ├── src/
    │   ├── App.tsx           # Main React component
    │   └── styles.css        # Styles
    ├── src-tauri/            # Tauri Rust backend
    └── package.json          # Node dependencies
```

---

## 🔧 Development

### **Backend Development**

```bash
cd backend
python3 main.py
```

API will be available at `http://127.0.0.1:8000`

API docs: `http://127.0.0.1:8000/docs`

### **Frontend Development**

```bash
cd frontend
npm run tauri dev
```

Hot reload is enabled - changes will reflect automatically!

### **Build for Production**

```bash
cd frontend
npm run tauri build
```

Installers will be in `frontend/src-tauri/target/release/bundle/`

---

## 🧪 Testing

### **Test Backend API**

```bash
curl http://127.0.0.1:8000/health
```

### **Test Screenshot Capture**

```bash
curl -X POST http://127.0.0.1:8000/api/screenshots/capture \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com"],
    "viewport_width": 1920,
    "viewport_height": 1080,
    "full_page": true
  }'
```

---

## 📊 API Endpoints

### **GET /**

Health check

### **POST /api/screenshots/capture**

Capture screenshots for multiple URLs

**Request**:

```json
{
  "urls": ["https://example.com", "https://google.com"],
  "viewport_width": 1920,
  "viewport_height": 1080,
  "full_page": true
}
```

**Response**:

```json
{
  "results": [
    {
      "url": "https://example.com",
      "status": "success",
      "screenshot_path": "screenshots/example.com_20251101_120000.png",
      "quality_score": 95.0,
      "quality_issues": [],
      "timestamp": "2025-11-01T12:00:00"
    }
  ]
}
```

### **POST /api/screenshots/retry**

Retry a single screenshot

**Query Params**: `url` (string)

### **POST /api/document/generate**

Generate Word document

**Request**:

```json
{
  "screenshot_paths": ["screenshots/example.com_20251101_120000.png"],
  "output_path": "output/report.docx",
  "title": "Screenshot Report"
}
```

### **WebSocket /ws**

Real-time progress updates

---

## 🎨 Customization

### **Change Viewport Size**

Edit `frontend/src/App.tsx`:

```typescript
viewport_width: 1920,  // Change this
viewport_height: 1080, // Change this
```

### **Change Quality Thresholds**

Edit `backend/quality_checker.py`:

```python
self.min_file_size = 5000  # Minimum file size in bytes
self.min_brightness = 10   # Minimum brightness
self.max_brightness = 250  # Maximum brightness
```

### **Change Document Template**

Edit `backend/document_service.py` to customize the Word document format.

---

## 🐛 Troubleshooting

### **Backend won't start**

- Make sure Python 3.12+ is installed: `python3 --version`
- Install dependencies: `pip3 install -r requirements.txt`
- Install Playwright browsers: `playwright install chromium`

### **Frontend won't start**

- Make sure Node.js 22+ is installed: `node --version`
- Make sure Rust is installed: `rustc --version`
- Install dependencies: `npm install`

### **Screenshots failing**

- Check if URLs are accessible
- Check internet connection
- Try increasing timeout in `screenshot_service.py`

### **Quality checks too strict**

- Adjust thresholds in `quality_checker.py`

---

## 📝 License

MIT License - Feel free to use for personal or commercial projects!

---

## 🚀 Next Steps

- [ ] Add concurrent screenshot processing
- [ ] Add session save/load
- [ ] Add PDF export
- [ ] Add custom viewport presets
- [ ] Add active tab detection (macOS)
- [ ] Add screenshot preview thumbnails
- [ ] Add batch retry for all failed screenshots

---

## 💡 Tips

- Use full URLs with `https://` or `http://`
- For best results, use viewport size 1920x1080
- Quality score above 60% is considered good
- Screenshots are saved in `backend/screenshots/`
- Documents are saved in `backend/output/`

---

**Built with ❤️ using Tauri, React, FastAPI, and Playwright**
