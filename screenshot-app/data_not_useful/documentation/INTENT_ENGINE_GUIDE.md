# 🎯 Intent Engine - Developer Purpose Understanding

**Understands what you want to do and finds the most relevant code**

---

## 🔍 What Is This?

The **Intent Engine** is a semantic code discovery system that:

✅ **Understands developer intent** - "fix login lag", "add payment support"  
✅ **Maps to semantic vectors** - Uses embeddings for deep understanding  
✅ **Finds code hotspots** - Files, functions, commits most relevant to your goal  
✅ **Provides actionable insights** - Specific suggestions for where to start  
✅ **Learns from history** - Analyzes git commits and patterns  

**It's like having a senior developer who knows exactly where everything is.**

---

## 🧠 How It Works (3 Layers)

### **Layer 1: Intent Understanding**

Takes natural language input and classifies it:

**Categories:**
- `performance` - slow, lag, optimize, speed, cache, async
- `bug` - fix, error, crash, issue, broken, fail
- `feature` - add, implement, create, new, support
- `refactor` - clean, improve, restructure, organize
- `security` - auth, login, permission, vulnerability
- `ui` - interface, design, layout, component
- `api` - endpoint, route, request, response
- `database` - query, sql, schema, migration
- `test` - testing, spec, coverage, unit

**Domains:**
- `authentication` - login, auth, user, password, token
- `payment` - pay, checkout, stripe, paypal, apple pay
- `screenshot` - capture, image, browser, playwright
- `config` - settings, environment, configuration
- `api` - endpoint, route, fastapi, rest
- `frontend` - react, component, ui, tsx, tauri
- `backend` - server, service, controller, model

---

### **Layer 2: Code Hotspot Mapping**

Builds an indexed graph:

```
Files ↔ Functions ↔ Commits ↔ Issues
```

**Each node contains:**
- Text summary
- Embedding vector (optional, with OpenAI)
- Metadata (size, category, purpose, etc.)

**Matching strategies:**
1. **Keyword matching** (fast) - Matches words in file names, purposes, commit messages
2. **Semantic matching** (smart) - Uses embeddings for deep similarity
3. **Hybrid scoring** - Combines both for best results

---

### **Layer 3: Insight Generation**

Analyzes matches and provides:

- 🔍 **Performance insights** - "Found 3 async functions - check for await bottlenecks"
- 📝 **Recent changes** - "Most recent related commit: Fix login timeout (2025-10-28)"
- 🎯 **Primary hotspots** - "Primary hotspot: backend/auth_service.py"
- ⚡ **Function suggestions** - "Check function: authenticate_user at line 45"

---

## 🚀 Quick Start

### **Standalone CLI:**

```bash
python3 brain_intent.py "fix login lag"
```

**Output:**
```
🎯 Analyzing intent: 'fix login lag'
📊 Category: performance
📊 Domain: authentication
🤖 Computing semantic similarity...
🔥 Building code hotspot graph...
✅ Indexed 87 files
✅ Indexed 234 functions
✅ Indexed 45 commits

============================================================
🎯 INTENT ENGINE RESULTS
============================================================

💡 Insights:
   🔍 Found 3 async functions - check for await bottlenecks
   📝 Most recent related commit: Optimize login response (2025-10-28)
   🎯 Primary hotspot: backend/auth_service.py - User authentication
   ⚡ Check function: backend/auth_service.py::authenticate_user at line 45

📄 Top File Matches:
   backend/auth_service.py (score: 8.5)
      └─ filename match, purpose match, authentication domain
   backend/login_controller.py (score: 6.2)
      └─ filename match, authentication domain
   backend/session_manager.py (score: 4.1)
      └─ purpose match, authentication domain

⚡ Top Function Matches:
   backend/auth_service.py::authenticate_user (score: 9.3)
      └─ async def authenticate_user(username, password)
   backend/auth_service.py::validate_token (score: 7.8)
      └─ async def validate_token(token)
   backend/session_manager.py::create_session (score: 5.5)
      └─ async def create_session(user_id)

📝 Related Commits:
   a1b2c3d4 - Optimize login response time
      └─ 2025-10-28
   e5f6g7h8 - Fix async token validation
      └─ 2025-10-25
   i9j0k1l2 - Add session caching
      └─ 2025-10-20

============================================================
```

---

### **Integrated CLI:**

```bash
python3 brain_cli.py

🧠 > intent fix login lag
# Shows same results as above

🧠 > intent add apple pay support
# Finds payment-related files, functions, commits

🧠 > intent optimize screenshot quality
# Finds screenshot service, quality checker, related commits
```

---

## 💡 Example Use Cases

### **Use Case 1: Performance Debugging**

```bash
🧠 > intent fix login lag

# Returns:
# - Files: auth_service.py, login_controller.py
# - Functions: authenticate_user(), validate_token()
# - Insights: "Found 3 async functions - check await bottlenecks"
# - Commits: Recent performance-related changes
```

**What you learn:**
- Where authentication code lives
- Which functions are async (potential bottlenecks)
- Recent changes that might have caused the lag
- Specific line numbers to investigate

---

### **Use Case 2: Adding New Feature**

```bash
🧠 > intent add apple pay support

# Returns:
# - Files: payment_service.py, checkout_controller.py
# - Functions: process_payment(), validate_payment_method()
# - Insights: "Primary hotspot: backend/payment_service.py"
# - Commits: How other payment methods were added
```

**What you learn:**
- Where payment code lives
- How existing payment methods are implemented
- Patterns to follow from git history
- Which files need modification

---

### **Use Case 3: Bug Investigation**

```bash
🧠 > intent fix screenshot capture error

# Returns:
# - Files: screenshot_service.py, browser_manager.py
# - Functions: capture_screenshot(), handle_browser_error()
# - Insights: "Check function: capture_screenshot at line 123"
# - Commits: Recent bug fixes in screenshot code
```

**What you learn:**
- Where the bug likely is
- Related error handling code
- How similar bugs were fixed before
- Specific functions to debug

---

### **Use Case 4: Code Refactoring**

```bash
🧠 > intent refactor authentication code

# Returns:
# - Files: All auth-related files
# - Functions: All auth functions
# - Insights: "Found 12 files in authentication domain"
# - Commits: Previous refactoring patterns
```

**What you learn:**
- Scope of refactoring (how many files)
- All related functions
- How previous refactors were done
- Dependencies to consider

---

## 🔧 How Scoring Works

### **Keyword Matching (Fast)**

```python
# File name match: +3 points
"login" in "login_service.py" → +3

# Purpose match: +2 points
"authentication" in "User authentication service" → +2

# Category match: +1 point
intent category = "performance", file category = "production" → +1

# Domain match: +2 points
intent domain = "authentication", file purpose contains "auth" → +2

# Total: 8 points
```

---

### **Semantic Matching (Smart, requires OpenAI)**

```python
# Compute embeddings
intent_embedding = embed("fix login lag")
file_embedding = embed("User authentication service with async token validation")

# Cosine similarity
similarity = cosine_similarity(intent_embedding, file_embedding)
# Returns: 0.85 (high similarity)

# Add to score
score += similarity * 5  # Weight semantic similarity
# Total: 8 + 4.25 = 12.25 points
```

---

### **Hybrid Scoring (Best Results)**

Combines both approaches:
1. **Keyword matching** - Fast, catches obvious matches
2. **Semantic matching** - Smart, catches conceptual matches
3. **Weighted sum** - Balances speed and accuracy

**Example:**
```
File: backend/auth_service.py
- Keyword score: 8
- Semantic score: 4.25
- Total: 12.25

File: backend/user_controller.py
- Keyword score: 3
- Semantic score: 6.5
- Total: 9.5

Ranking: auth_service.py (12.25) > user_controller.py (9.5)
```

---

## 📊 What Gets Indexed

### **Files:**
- Path, name, category, purpose
- Size, preview (first 500 chars)
- Embedding (optional)

### **Functions:**
- Name, signature, docstring
- File location, line number
- Is async? (important for performance)
- Embedding (optional)

### **Commits:**
- Hash, author, date, message
- Changed files
- Embedding of message (optional)

### **Issues (Future):**
- Issue ID, title, description
- Labels, status, assignee
- Embedding (optional)

---

## 🎯 Intent Categories Detected

| Category | Keywords | Example Intent |
|----------|----------|----------------|
| **Performance** | slow, lag, optimize, speed, cache, async | "fix login lag" |
| **Bug** | fix, error, crash, issue, broken, fail | "fix screenshot error" |
| **Feature** | add, implement, create, new, support | "add apple pay" |
| **Refactor** | refactor, clean, improve, restructure | "refactor auth code" |
| **Security** | security, auth, login, vulnerability | "fix auth vulnerability" |
| **UI** | ui, interface, design, layout, component | "improve login UI" |
| **API** | api, endpoint, route, request, response | "add new API endpoint" |
| **Database** | database, query, sql, schema, migration | "optimize DB queries" |
| **Test** | test, testing, spec, coverage, unit | "add login tests" |

---

## 🔮 Advanced Features

### **1. Async Function Detection**

For performance intents, highlights async functions:

```
🔍 Found 3 async functions - check for await bottlenecks:
   - authenticate_user() - line 45
   - validate_token() - line 78
   - fetch_user_profile() - line 112
```

---

### **2. Git History Analysis**

Learns from past commits:

```
📝 Related Commits:
   a1b2c3d4 - Optimize login response time (2025-10-28)
   e5f6g7h8 - Fix async token validation (2025-10-25)

💡 Pattern detected: Recent performance work in auth
```

---

### **3. Embedding Cache**

Caches embeddings to avoid re-computing:

```json
{
  "md5_hash_of_text": [0.123, 0.456, ...],
  ...
}
```

Saved to `.brain_embeddings.json`

---

### **4. Multi-Domain Detection**

Detects when intent spans multiple domains:

```
🧠 > intent fix payment API error

📊 Detected domains:
   - payment (score: 3)
   - api (score: 2)
   - bug (category)

🎯 Searching in both payment and API code...
```

---

## 🚀 Performance

### **Without OpenAI (Keyword Only):**
- ⚡ **Speed:** <100ms
- 💰 **Cost:** $0
- 🎯 **Accuracy:** Good for obvious matches

### **With OpenAI (Hybrid):**
- ⚡ **Speed:** 1-3 seconds
- 💰 **Cost:** ~$0.001 per query
- 🎯 **Accuracy:** Excellent for conceptual matches

### **Caching:**
- First query: 1-3 seconds (computes embeddings)
- Subsequent queries: <100ms (uses cache)

---

## 📖 Command Reference

### **Standalone:**

```bash
python3 brain_intent.py "your intent here"
```

### **Integrated CLI:**

```bash
python3 brain_cli.py

🧠 > intent <your intent>
```

### **Examples:**

```bash
# Performance
🧠 > intent fix login lag
🧠 > intent optimize screenshot quality
🧠 > intent speed up API response

# Features
🧠 > intent add apple pay support
🧠 > intent implement dark mode
🧠 > intent create user dashboard

# Bugs
🧠 > intent fix screenshot capture error
🧠 > intent debug payment failure
🧠 > intent resolve auth timeout

# Refactoring
🧠 > intent refactor authentication code
🧠 > intent clean up payment service
🧠 > intent improve error handling
```

---

## 🎉 Summary

**The Intent Engine provides:**

✅ **Natural language understanding** - "fix login lag" → finds auth code  
✅ **Semantic search** - Understands concepts, not just keywords  
✅ **Code hotspot mapping** - Files ↔ Functions ↔ Commits graph  
✅ **Actionable insights** - Specific files, functions, line numbers  
✅ **Git history learning** - Learns from past commits  
✅ **Performance optimization** - Caching, hybrid scoring  
✅ **Multi-domain detection** - Handles complex intents  
✅ **CLI integration** - Built into brain_cli.py  

**Your project now understands what you want to do!** 🎯✨

---

## 🚀 Try It Now!

```bash
cd screenshot-app

# Standalone
python3 brain_intent.py "fix login lag"

# Integrated
python3 brain_cli.py
🧠 > intent add payment support
```

**The Intent Engine knows exactly where to look!** 🧠🔍

