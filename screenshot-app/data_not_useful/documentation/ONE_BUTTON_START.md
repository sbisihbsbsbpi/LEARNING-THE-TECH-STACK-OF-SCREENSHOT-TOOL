# 🚀 One-Button Start - Complete Setup!

**Your Screenshot Tool now starts with just ONE command!**

---

## ✅ What's Been Set Up

I've created a complete one-button start solution for your Screenshot Tool! Here's what's new:

### **1. Improved Start Script** ✅

**File:** `start.sh`

**Features:**
- ✅ Colored output for better readability
- ✅ Automatic prerequisite checks (Python, Node, Rust)
- ✅ Auto-install frontend dependencies if missing
- ✅ Backend starts in background with logging
- ✅ Health check before starting frontend
- ✅ Automatic cleanup on Ctrl+C (stops both frontend and backend!)
- ✅ Better error messages with helpful tips

### **2. Root Package.json** ✅

**File:** `package.json`

**Features:**
- ✅ `npm start` - Start both frontend and backend
- ✅ `npm run backend` - Start only backend
- ✅ `npm run frontend` - Start only frontend
- ✅ `npm run install:all` - Install all dependencies
- ✅ `npm run logs` - View backend logs in real-time
- ✅ Many more useful commands!

### **3. Comprehensive Start Guide** ✅

**File:** `START_GUIDE.md`

**Includes:**
- ✅ Quick start instructions
- ✅ Prerequisites checklist
- ✅ All available commands
- ✅ Troubleshooting guide
- ✅ Development workflow
- ✅ Pro tips

### **4. Updated README** ✅

**File:** `README.md`

**Updated with:**
- ✅ One-command quick start
- ✅ Link to START_GUIDE.md
- ✅ All start options
- ✅ Recent updates (Phase 2 complete!)

---

## 🎯 How to Start (3 Easy Ways!)

### **Method 1: npm (Recommended)**

```bash
cd screenshot-app
npm start
```

### **Method 2: Bash Script**

```bash
cd screenshot-app
bash start.sh
```

### **Method 3: Execute Directly**

```bash
cd screenshot-app
./start.sh
```

**All three methods do the same thing:**
1. Check prerequisites
2. Install dependencies if needed
3. Start backend in background
4. Start frontend (Tauri desktop app)
5. Auto-cleanup when you press Ctrl+C

---

## 📊 What Happens When You Start?

### **Console Output:**

```bash
🚀 Starting Screenshot Tool...

✅ All prerequisites installed

📦 Starting backend (FastAPI)...
⏳ Waiting for backend to start...
✅ Backend started successfully at http://127.0.0.1:8000

🎨 Starting frontend (Tauri Desktop App)...
💡 This will open the desktop application window
💡 Press Ctrl+C to stop both frontend and backend

# ... Tauri build output ...
# ... Desktop app opens! ...
```

### **What's Running:**

- **Backend:** http://127.0.0.1:8000 (FastAPI)
- **Frontend:** Desktop application window (Tauri)
- **Logs:** `screenshot-app/backend.log`

---

## 🛑 How to Stop

### **Just press Ctrl+C in the terminal!**

```bash
^C
🛑 Shutting down...
✅ Stopped backend
```

Both frontend and backend will stop automatically! No need to kill processes manually!

---

## 📚 All Available Commands

### **Starting**

| Command | Description |
|---------|-------------|
| `npm start` | Start both frontend and backend (recommended) |
| `npm run dev` | Same as `npm start` |
| `bash start.sh` | Start using bash script |
| `./start.sh` | Execute script directly |

### **Running Separately**

| Command | Description |
|---------|-------------|
| `npm run backend` | Start only backend |
| `npm run frontend` | Start only frontend (Tauri) |
| `npm run frontend:web` | Start frontend in browser (dev mode) |

### **Installation**

| Command | Description |
|---------|-------------|
| `npm run install:all` | Install all dependencies |
| `npm run install:frontend` | Install frontend dependencies |
| `npm run install:backend` | Install backend dependencies |

### **Utilities**

| Command | Description |
|---------|-------------|
| `npm run logs` | View backend logs in real-time |
| `npm run build` | Build frontend for production |
| `npm test` | Run backend tests |
| `npm run clean` | Clean all build artifacts |

---

## 🔧 First-Time Setup

### **1. Install Prerequisites**

- **Python 3.12+** - `python3 --version`
- **Node.js 22+** - `node --version`
- **Rust 1.91+** - `rustc --version`

### **2. Install Dependencies**

```bash
cd screenshot-app
npm run install:all
```

This installs both frontend and backend dependencies.

### **3. Start the App**

```bash
npm start
```

Done! 🎉

---

## 🐛 Troubleshooting

### **Problem: "command not found: npm"**

**Solution:** Install Node.js

```bash
# macOS
brew install node@22

# Ubuntu
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### **Problem: Backend fails to start**

**Check the logs:**

```bash
cat screenshot-app/backend.log
```

**Common fixes:**
- Install dependencies: `npm run install:backend`
- Check Python version: `python3 --version` (need 3.12+)
- Port 8000 in use: `bash restart.sh`

### **Problem: Frontend fails to start**

**Common fixes:**
- Install dependencies: `npm run install:frontend`
- Install Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Check Node version: `node --version` (need 22+)

### **Problem: Port 8000 already in use**

**Solution:**

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use restart script
bash restart.sh
```

---

## 🎨 Development Workflow

### **1. Start the app**

```bash
npm start
```

### **2. Make changes**

- **Frontend:** Edit `screenshot-app/frontend/src/App.tsx`
- **Backend:** Edit `screenshot-app/backend/screenshot_service.py`

### **3. See changes automatically**

- **Frontend:** Auto-reloads (Vite HMR)
- **Backend:** Auto-reloads (FastAPI auto-reload)

### **4. View logs**

```bash
# In a separate terminal
npm run logs
```

### **5. Stop the app**

Press **Ctrl+C** in the terminal

---

## 🔥 Pro Tips

### **Tip 1: Run frontend in browser for faster dev**

```bash
npm run frontend:web
```

Then open http://localhost:5173 in your browser. Much faster than Tauri!

### **Tip 2: View logs in real-time**

```bash
# Terminal 1: Start app
npm start

# Terminal 2: Watch logs
npm run logs
```

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

## 📈 What's New vs Old Way

### **Old Way (2 terminals required):**

```bash
# Terminal 1
cd screenshot-app/backend
python3 main.py

# Terminal 2
cd screenshot-app/frontend
npm run tauri dev

# To stop: Ctrl+C in both terminals
```

### **New Way (1 command!):**

```bash
cd screenshot-app
npm start

# To stop: Ctrl+C once (stops both!)
```

**Benefits:**
- ✅ One command instead of two
- ✅ Automatic dependency checks
- ✅ Automatic cleanup on exit
- ✅ Better error messages
- ✅ Colored output
- ✅ Health checks
- ✅ Logs saved to file

---

## 🎉 Summary

You can now start your Screenshot Tool with just:

```bash
cd screenshot-app
npm start
```

**That's it!** 🚀

- Backend starts automatically
- Frontend opens automatically
- Both stop when you press Ctrl+C
- Logs saved to `backend.log`
- No manual process management needed!

---

## 📚 Documentation

- **[START_GUIDE.md](./START_GUIDE.md)** - Complete startup guide
- **[README.md](./README.md)** - Main project README
- **[Phase 2 Complete](./misc-code/docs/ui-refactoring/PHASE2_COMPLETE.md)** - UI refactoring results

---

## 🆘 Need Help?

- **Backend logs:** `cat screenshot-app/backend.log`
- **View logs live:** `npm run logs`
- **Health check:** http://127.0.0.1:8000/health
- **API docs:** http://127.0.0.1:8000/docs

---

**Enjoy your one-button start! 🎉**

