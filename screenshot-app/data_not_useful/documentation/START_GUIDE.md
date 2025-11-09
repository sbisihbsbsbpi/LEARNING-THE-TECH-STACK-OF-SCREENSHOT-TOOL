# 🚀 Quick Start Guide - Screenshot Tool

**One-button start for both frontend and backend!**

---

## ⚡ Quick Start (Recommended)

### **Option 1: Using npm (Easiest)**

```bash
cd screenshot-app
npm start
```

That's it! This will:
1. ✅ Check all prerequisites (Python, Node, Rust)
2. ✅ Install frontend dependencies if needed
3. ✅ Start backend (FastAPI) in background
4. ✅ Start frontend (Tauri Desktop App)
5. ✅ Auto-cleanup when you press Ctrl+C

---

### **Option 2: Using bash script**

```bash
cd screenshot-app
bash start.sh
```

Same as Option 1, just using the script directly.

---

### **Option 3: Using chmod + execute**

```bash
cd screenshot-app
chmod +x start.sh
./start.sh
```

Make the script executable and run it.

---

## 📋 Prerequisites

Before running the app, make sure you have:

### **1. Python 3.12+**

```bash
python3 --version
# Should show: Python 3.12.x or higher
```

**Install if needed:**
- macOS: `brew install python@3.12`
- Ubuntu: `sudo apt install python3.12`
- Windows: Download from [python.org](https://www.python.org/)

### **2. Node.js 22+**

```bash
node --version
# Should show: v22.x.x or higher
```

**Install if needed:**
- macOS: `brew install node@22`
- Ubuntu: `curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt-get install -y nodejs`
- Windows: Download from [nodejs.org](https://nodejs.org/)

### **3. Rust 1.91+ (for Tauri)**

```bash
rustc --version
# Should show: rustc 1.91.x or higher
```

**Install if needed:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

---

## 🔧 First-Time Setup

### **1. Install Backend Dependencies**

```bash
cd screenshot-app/backend
pip install -r requirements.txt
cd ..
```

### **2. Install Frontend Dependencies**

```bash
cd screenshot-app/frontend
npm install
cd ..
```

**Or install both at once:**

```bash
cd screenshot-app
npm run install:all
```

---

## 🎯 All Available Commands

### **Starting the App**

| Command | Description |
|---------|-------------|
| `npm start` | Start both frontend and backend (recommended) |
| `npm run dev` | Same as `npm start` |
| `bash start.sh` | Start using bash script directly |

### **Running Components Separately**

| Command | Description |
|---------|-------------|
| `npm run backend` | Start only backend (FastAPI) |
| `npm run frontend` | Start only frontend (Tauri Desktop App) |
| `npm run frontend:web` | Start frontend in web browser (dev mode) |

### **Installation**

| Command | Description |
|---------|-------------|
| `npm run install:all` | Install all dependencies (frontend + backend) |
| `npm run install:frontend` | Install only frontend dependencies |
| `npm run install:backend` | Install only backend dependencies |

### **Building**

| Command | Description |
|---------|-------------|
| `npm run build` | Build frontend for production |

### **Testing**

| Command | Description |
|---------|-------------|
| `npm test` | Run backend tests |

### **Utilities**

| Command | Description |
|---------|-------------|
| `npm run logs` | View backend logs in real-time |
| `npm run clean` | Clean all build artifacts and dependencies |

---

## 🖥️ What Happens When You Start?

### **Step 1: Prerequisites Check**

```
🚀 Starting Screenshot Tool...

✅ All prerequisites installed
```

The script checks for Python, Node, and Rust.

### **Step 2: Backend Starts**

```
📦 Starting backend (FastAPI)...
⏳ Waiting for backend to start...
✅ Backend started successfully at http://127.0.0.1:8000
```

The FastAPI backend starts on port 8000.

### **Step 3: Frontend Starts**

```
🎨 Starting frontend (Tauri Desktop App)...
💡 This will open the desktop application window
💡 Press Ctrl+C to stop both frontend and backend
```

The Tauri desktop app opens in a new window.

### **Step 4: App is Running!**

- **Backend:** http://127.0.0.1:8000
- **Frontend:** Desktop application window
- **Logs:** `screenshot-app/backend.log`

---

## 🛑 Stopping the App

### **Press Ctrl+C in the terminal**

```
^C
🛑 Shutting down...
✅ Stopped backend
```

Both frontend and backend will stop automatically!

---

## 🐛 Troubleshooting

### **Problem: Backend fails to start**

**Check the logs:**
```bash
cd screenshot-app
cat backend.log
```

**Common issues:**
- Port 8000 already in use: Kill the process using port 8000
- Missing dependencies: Run `npm run install:backend`
- Python version too old: Upgrade to Python 3.12+

### **Problem: Frontend fails to start**

**Common issues:**
- Missing dependencies: Run `npm run install:frontend`
- Rust not installed: Install Rust (see Prerequisites)
- Node version too old: Upgrade to Node 22+

### **Problem: "command not found: npm"**

**Solution:** Install Node.js (see Prerequisites)

### **Problem: "command not found: python3"**

**Solution:** Install Python 3 (see Prerequisites)

### **Problem: Port 8000 already in use**

**Find and kill the process:**
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Or use the restart script
cd screenshot-app
bash restart.sh
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│         Tauri Desktop App               │
│         (React + TypeScript)            │
│         Port: Desktop Window            │
└─────────────┬───────────────────────────┘
              │
              │ HTTP Requests
              │
┌─────────────▼───────────────────────────┐
│         FastAPI Backend                 │
│         (Python + Playwright)           │
│         Port: 8000                      │
└─────────────────────────────────────────┘
```

---

## 🎨 Development Workflow

### **1. Start the app**

```bash
npm start
```

### **2. Make changes**

- **Frontend:** Edit files in `screenshot-app/frontend/src/`
- **Backend:** Edit files in `screenshot-app/backend/`

### **3. See changes**

- **Frontend:** Auto-reloads on save (Vite HMR)
- **Backend:** Auto-reloads on save (FastAPI auto-reload)

### **4. Test changes**

- Use the desktop app to test features
- Check `backend.log` for backend logs
- Check browser console for frontend logs

---

## 🔥 Pro Tips

### **Tip 1: View logs in real-time**

```bash
# In a separate terminal
cd screenshot-app
npm run logs
```

### **Tip 2: Run frontend in browser for faster development**

```bash
npm run frontend:web
```

Then open http://localhost:5173 in your browser.

### **Tip 3: Clean everything and start fresh**

```bash
npm run clean
npm run install:all
npm start
```

### **Tip 4: Check backend health**

```bash
curl http://127.0.0.1:8000/health
```

Should return: `{"status":"healthy"}`

---

## 📚 Next Steps

After starting the app:

1. **Test the UI refactoring** - See the Phase 2 improvements!
2. **Try screenshot capture** - Test viewport, fullpage, and segmented modes
3. **Test stealth mode** - Try Playwright, Rebrowser, and Camoufox
4. **Save auth state** - Login to a site and save cookies/localStorage
5. **Create sessions** - Save your favorite configurations

---

## 🆘 Need Help?

- **Backend logs:** `cat screenshot-app/backend.log`
- **Frontend logs:** Check the desktop app's developer console
- **API docs:** http://127.0.0.1:8000/docs (when backend is running)
- **Health check:** http://127.0.0.1:8000/health

---

## 🎉 You're Ready!

Just run:

```bash
cd screenshot-app
npm start
```

And you're good to go! 🚀

