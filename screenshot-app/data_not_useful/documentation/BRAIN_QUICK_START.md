# 🧠 Project Brain - Quick Start Guide

**The intelligent algorithm that knows your project inside-out**

---

## 🎯 What You Have

An intelligent file management system with **4 powerful tools**:

1. **`project_brain.py`** - Core engine (scans and indexes)
2. **`brain_cli.py`** - Interactive assistant (ask questions)
3. **`brain_visualizer.py`** - Visual dashboard (see the graph)
4. **`brain_watcher.py`** - Auto-updater (real-time monitoring)

---

## ⚡ 30-Second Quick Start

```bash
cd screenshot-app

# Step 1: Generate index (first time only)
python3 project_brain.py

# Step 2: Start interactive assistant
python3 brain_cli.py
```

**That's it!** Now you can ask questions like:

```
🧠 > find screenshot
🧠 > search config
🧠 > impact backend/config.py
🧠 > health
🧠 > production
```

---

## 📖 The 4 Tools Explained

### **1. 🔍 project_brain.py - The Scanner**

**What it does:** Scans your project and builds an intelligent index.

**When to use:** First time, or when you want to refresh the index.

```bash
python3 project_brain.py
```

**Output:**
```
🧠 Scanning project structure...
✅ Indexed 87 files
📊 Graph built: 87 nodes, 15 edges
💾 Saved index to project_index.json

============================================================
📊 PROJECT BRAIN SUMMARY
============================================================

📁 Files by Category:
   production       7 files
   config           5 files
   test            10 files
   docs            24 files
   archived        15 files
   runtime         26 files

📦 Total Files: 87
🔗 Dependencies Tracked: 15
```

---

### **2. 💬 brain_cli.py - The Interactive Assistant**

**What it does:** Interactive command-line interface for asking questions.

**When to use:** Anytime you need to find files or understand dependencies.

```bash
python3 brain_cli.py
```

**Available Commands:**

#### **🔍 Search & Discovery**
```bash
find screenshot      # Find files by purpose
search config        # Smart search
ask "where is X?"    # AI semantic search (requires OpenAI)
```

#### **📊 Graph Intelligence**
```bash
impact config.py     # Show impact of changing a file
circular             # Find circular dependencies
orphans              # Find orphaned files
health               # Full health check
```

#### **📁 Project Info**
```bash
production           # Show production files
deps main.py         # Show dependencies
dependents config    # Show what depends on config
summary              # Project overview
```

**Example Session:**
```
🧠 > find screenshot

🔍 Finding files for: 'screenshot'

  ✅ backend/screenshot_service.py
     └─ Screenshot capture with Playwright + stealth
     └─ Match: Matches intent 'screenshot'

🧠 > impact backend/config.py

💥 Impact analysis for: backend/config.py

📊 Total files affected: 5

🔴 Direct dependents (5):
  📄 backend/main.py
     └─ FastAPI backend entry point
  📄 backend/screenshot_service.py
     └─ Screenshot capture with Playwright

🧠 > health

🏥 Running dependency health check...

📊 DEPENDENCY HEALTH REPORT
============================================================

✅ Perfect health! No issues found.
```

---

### **3. 🌐 brain_visualizer.py - The Visual Dashboard**

**What it does:** Generates an interactive HTML visualization of your project.

**When to use:** When you want to see the big picture visually.

```bash
python3 brain_visualizer.py
```

**Features:**
- ✅ Interactive force-directed graph
- ✅ Color-coded by category (production, test, docs, etc.)
- ✅ Zoom and pan controls
- ✅ Hover tooltips with file info
- ✅ Filter by category
- ✅ Drag nodes to rearrange
- ✅ Beautiful gradient background

**Output:**
```
🧠 Generating Project Brain Dashboard...
📖 Loading existing index...
✅ Loaded 87 files
✅ Dashboard generated: project_brain_dashboard.html
📂 Open in browser: file:///path/to/project_brain_dashboard.html
🌐 Opening in browser...
```

**What you'll see:**
- Green nodes = Production files
- Blue nodes = Config files
- Orange nodes = Test files
- Purple nodes = Docs
- Lines = Dependencies

**Controls:**
- **Drag** nodes to rearrange
- **Scroll** to zoom in/out
- **Hover** to see file details
- **Click category buttons** to filter
- **Click "Reset Zoom"** to reset view
- **Click "Toggle Labels"** to show/hide names

---

### **4. 🔄 brain_watcher.py - The Auto-Updater**

**What it does:** Monitors file changes and auto-updates the index in real-time.

**When to use:** During active development to keep index fresh.

```bash
python3 brain_watcher.py
```

**Features:**
- ✅ Real-time file monitoring
- ✅ Auto-updates on create/modify/delete
- ✅ Debounced updates (waits 2 seconds)
- ✅ Rebuilds graph automatically
- ✅ Runs in background

**Output:**
```
============================================================
🧠 PROJECT BRAIN WATCHER
============================================================
Monitoring file changes and auto-updating index...
Press Ctrl+C to stop

📖 Loading existing index...
✅ Loaded 87 files from index

👀 Watching for changes...

📝 Detected change: screenshot_service.py

🔄 Updating index for 1 files...
📊 Graph built: 87 nodes, 15 edges
✅ Index updated!
```

**Use case:**
```bash
# Terminal 1: Start watcher
python3 brain_watcher.py

# Terminal 2: Make changes
vim backend/new_service.py

# Terminal 1: Auto-updates immediately
✨ Detected new file: new_service.py
🔄 Updating index...
✅ Index updated!

# Terminal 3: Query immediately
python3 brain_cli.py
🧠 > find new_service
  ✅ backend/new_service.py
```

---

## 🎯 Common Workflows

### **Workflow 1: First Time Setup**

```bash
# 1. Generate index
python3 project_brain.py

# 2. Explore interactively
python3 brain_cli.py
🧠 > summary
🧠 > production
🧠 > health

# 3. Visualize
python3 brain_visualizer.py
```

---

### **Workflow 2: Finding Code**

```bash
python3 brain_cli.py

🧠 > find screenshot
# Shows screenshot_service.py

🧠 > deps backend/screenshot_service.py
# Shows what it depends on

🧠 > dependents screenshot_service
# Shows what depends on it
```

---

### **Workflow 3: Impact Analysis**

```bash
python3 brain_cli.py

🧠 > impact backend/config.py
# Shows all files affected by changing config.py

# Output shows:
# - Direct dependents (5 files)
# - Indirect dependents (0 files)
# - Total impact: 5 files

# Now you know: changing config.py affects 5 files!
```

---

### **Workflow 4: Health Check**

```bash
python3 brain_cli.py

🧠 > health

# Checks for:
# - Circular dependencies
# - Orphaned files
# - Large files (>100KB)
# - Unresolved imports
# - Missing dependencies

# Shows actionable issues to fix
```

---

### **Workflow 5: Active Development**

```bash
# Terminal 1: Start watcher
python3 brain_watcher.py

# Terminal 2: Code normally
vim backend/new_feature.py

# Terminal 3: Query anytime
python3 brain_cli.py
🧠 > find new_feature
```

---

## 🔧 Optional Enhancements

### **Enable Graph Intelligence**

```bash
pip install networkx
```

**Unlocks:**
- `impact` command
- `circular` command
- `orphans` command
- `health` command
- Visual dashboard

---

### **Enable Auto-Updating**

```bash
pip install watchdog
```

**Unlocks:**
- `python3 brain_watcher.py`

---

### **Enable AI Semantic Search**

```bash
pip install openai
export OPENAI_API_KEY="sk-your-key-here"
```

**Unlocks:**
- `ask` command in CLI
- Natural language queries
- Semantic understanding

**Example:**
```bash
🧠 > ask where is the code that handles screenshot capture?

🤖 The code that handles screenshot capture is in:

**backend/screenshot_service.py**

Reasoning:
- Contains ScreenshotService class
- Uses Playwright for browser automation
- Implements stealth mode
- Handles authentication state
```

---

## 📊 Cheat Sheet

| What You Want | Command |
|---------------|---------|
| **Find a file** | `find <intent>` |
| **Search everywhere** | `search <query>` |
| **See impact of change** | `impact <file>` |
| **Check project health** | `health` |
| **Find circular deps** | `circular` |
| **Find orphaned files** | `orphans` |
| **Show production files** | `production` |
| **Show dependencies** | `deps <file>` |
| **Show dependents** | `dependents <module>` |
| **Project overview** | `summary` |
| **Refresh index** | `rescan` |
| **Ask AI** | `ask <question>` |
| **Visual dashboard** | `python3 brain_visualizer.py` |
| **Auto-update** | `python3 brain_watcher.py` |

---

## 🎉 Summary

**You have 4 powerful tools:**

1. **`project_brain.py`** - Scans and indexes (run once)
2. **`brain_cli.py`** - Interactive assistant (use daily)
3. **`brain_visualizer.py`** - Visual dashboard (explore visually)
4. **`brain_watcher.py`** - Auto-updater (run during dev)

**Start with:**
```bash
python3 project_brain.py    # Generate index
python3 brain_cli.py         # Start exploring
```

**Your project now has a brain!** 🧠✨

