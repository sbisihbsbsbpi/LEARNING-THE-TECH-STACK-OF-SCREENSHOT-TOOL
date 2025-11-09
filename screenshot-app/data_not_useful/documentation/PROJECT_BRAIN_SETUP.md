# 🧠 Project Brain - Complete Setup Guide

**An intelligent algorithm that knows your project inside-out and answers "what/where" questions instantly.**

---

## 🎯 What You Get

### **Two Modes of Operation:**

#### **1. 🔍 Local Mode (No API Key Required)**
- Fast pattern-based search
- Intent mapping ("find screenshot" → screenshot_service.py)
- Dependency tracking
- File categorization
- **Perfect for:** Quick file lookups, dependency analysis

#### **2. 🤖 AI Mode (OpenAI API Key Required)**
- Semantic understanding of code
- Natural language questions
- Context-aware answers
- Reasoning about file purposes
- **Perfect for:** Complex queries, understanding unfamiliar codebases

---

## 🚀 Quick Start (Local Mode)

### **Step 1: Install (No Dependencies)**

```bash
cd screenshot-app
# No installation needed - uses only Python standard library!
```

### **Step 2: Generate Index**

```bash
python3 project_brain.py
```

**Output:**
```
🧠 Scanning project structure...
✅ Indexed 87 files
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

### **Step 3: Use Interactive CLI**

```bash
python3 brain_cli.py
```

**Example:**
```
🧠 > find screenshot
  ✅ backend/screenshot_service.py
     └─ Screenshot capture with Playwright + stealth

🧠 > search config
  ⚙️ backend/config.py (score: 18)
     └─ Centralized configuration with Pydantic

🧠 > production
  ✅ backend/main.py
  ✅ backend/screenshot_service.py
  ... (7 files)
```

---

## 🤖 AI Mode Setup (Optional)

### **Step 1: Install OpenAI**

```bash
pip install openai
```

### **Step 2: Get API Key**

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-...`)

### **Step 3: Set Environment Variable**

**macOS/Linux:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Windows:**
```cmd
set OPENAI_API_KEY=sk-your-key-here
```

**Permanent (add to ~/.bashrc or ~/.zshrc):**
```bash
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### **Step 4: Use AI Features**

```bash
python3 brain_cli.py
```

**Now you can ask semantic questions:**

```
🧠 > ask where is the code that handles screenshot capture?

🤖 Asking AI: 'where is the code that handles screenshot capture?'
⏳ Thinking...

The code that handles screenshot capture is in:

**backend/screenshot_service.py**

Reasoning:
- This file contains the ScreenshotService class
- It uses Playwright for browser automation
- Implements stealth mode with rebrowser-playwright
- Handles authentication state management
- Manages screenshot quality and validation

Key functions:
- capture_screenshot() - Main capture logic
- _setup_browser_context() - Browser configuration
- _apply_stealth() - Anti-detection measures
```

---

## 📖 Command Reference

### **Local Mode Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `find <intent>` | Find files by purpose | `find screenshot` |
| `search <query>` | Smart search | `search config` |
| `production` | Show production files | `production` |
| `deps <file>` | Show dependencies | `deps backend/main.py` |
| `dependents <module>` | Show dependents | `dependents config` |
| `summary` | Project overview | `summary` |
| `rescan` | Refresh index | `rescan` |
| `help` | Show commands | `help` |
| `quit` | Exit | `quit` |

### **AI Mode Commands (Requires OpenAI)**

| Command | Description | Example |
|---------|-------------|---------|
| `ask <question>` | Semantic search | `ask where is auth code?` |

---

## 💡 Example Use Cases

### **1. Finding Code (Local Mode)**

```bash
🧠 > find screenshot
🧠 > deps backend/screenshot_service.py
🧠 > dependents screenshot_service
```

### **2. Understanding Code (AI Mode)**

```bash
🧠 > ask how does authentication work?
🧠 > ask what files handle document generation?
🧠 > ask where is the quality checking logic?
```

### **3. Impact Analysis**

```bash
🧠 > dependents config
# Shows all files that will be affected if you change config.py
```

### **4. Onboarding New Developers**

```bash
🧠 > summary
🧠 > production
🧠 > ask what are the main components of this project?
```

---

## 🔧 Configuration

### **Customize Intent Mappings**

Edit `project_brain.py`:

```python
self.intent_map = {
    "screenshot": ["screenshot_service.py", "main.py"],
    "your_intent": ["your_pattern"],
    # Add more...
}
```

### **Customize File Purposes**

Edit `_infer_purpose()` in `project_brain.py`:

```python
purposes = {
    "main.py": "FastAPI backend entry point",
    "your_file.py": "Your custom purpose",
    # Add more...
}
```

### **Change OpenAI Model**

Edit `ask_ai()` in `project_brain.py`:

```python
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",  # or "gpt-4", "gpt-3.5-turbo"
    # ...
)
```

---

## 📊 How It Works

### **Local Mode (Pattern-Based)**

1. **Scan** - Walks project directory recursively
2. **Index** - Extracts metadata (name, size, type, modified date)
3. **Categorize** - Assigns category (production, test, docs, etc.)
4. **Infer Purpose** - Determines what file does from name/location
5. **Extract Dependencies** - Parses imports (Python AST, JS regex)
6. **Search** - Scores results by filename, path, purpose matches

### **AI Mode (Semantic)**

1. **Build Context** - Gathers file previews (first 500 chars)
2. **Send to OpenAI** - Includes context + user question
3. **Get Answer** - AI analyzes code and provides reasoning
4. **Return Results** - File paths + explanations

---

## 💰 Cost Estimate (AI Mode)

**Using gpt-4o-mini:**
- **Input:** ~2,000 tokens per query (file previews)
- **Output:** ~200 tokens per answer
- **Cost:** ~$0.001 per query (less than 1 cent!)
- **100 queries:** ~$0.10

**Using gpt-4:**
- **Cost:** ~$0.03 per query
- **100 queries:** ~$3.00

**Recommendation:** Use `gpt-4o-mini` for 99% of queries. It's fast, cheap, and accurate.

---

## 🎯 Comparison: Local vs AI Mode

| Feature | Local Mode | AI Mode |
|---------|-----------|---------|
| **Speed** | <100ms | 1-3 seconds |
| **Cost** | Free | ~$0.001/query |
| **Accuracy** | Pattern-based | Semantic understanding |
| **Setup** | None | API key required |
| **Best For** | Quick lookups | Complex questions |
| **Dependencies** | None | `pip install openai` |

**Recommendation:** Use **both**! Local mode for quick lookups, AI mode for complex questions.

---

## 🛠️ Troubleshooting

### **"OpenAI not available"**

```bash
pip install openai
```

### **"API key not found"**

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### **"Rate limit exceeded"**

Wait 60 seconds or upgrade your OpenAI plan.

### **"Index not found"**

```bash
python3 project_brain.py  # Generate index first
```

### **"No results found"**

Try broader search terms or use AI mode:
```bash
🧠 > ask where is the code for X?
```

---

## 📁 Files

- **`project_brain.py`** - Core engine (350 lines)
- **`brain_cli.py`** - Interactive CLI (220 lines)
- **`project_index.json`** - Generated index (auto-created)
- **`PROJECT_BRAIN_README.md`** - User guide
- **`PROJECT_BRAIN_SETUP.md`** - This file
- **`PROJECT_BRAIN_COMPLETE.md`** - Implementation summary

---

## 🎉 Summary

**You now have TWO powerful ways to navigate your project:**

### **🔍 Local Mode (Free, Fast)**
```bash
python3 brain_cli.py
🧠 > find screenshot
🧠 > search config
🧠 > production
```

### **🤖 AI Mode (Semantic, Smart)**
```bash
export OPENAI_API_KEY="sk-..."
python3 brain_cli.py
🧠 > ask where is the authentication code?
🧠 > ask how does screenshot capture work?
🧠 > ask what files handle quality checking?
```

**Start with Local Mode (no setup), upgrade to AI Mode when you need semantic understanding!** 🚀

