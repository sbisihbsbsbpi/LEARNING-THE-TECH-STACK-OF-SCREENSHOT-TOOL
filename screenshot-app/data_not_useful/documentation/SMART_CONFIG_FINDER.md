# 🧭 Smart Config Finder - Complete Guide

**Self-learning configuration discovery engine for the modern codebase**

---

## 💡 The Problem

You've got dozens of config files:
- `.env`, `.env.local`, `.env.production`
- `config.yml`, `settings.json`
- Constants in `*.ts`, `*.py`, `*.js`
- Secret references in Vault, AWS, GCP

**And you can't remember where `paymentGatewayUrl` is defined.**

Instead of manually grepping your repo, **Smart Config Finder knows the layout of your configuration universe.**

---

## 🎯 What Is This?

The **Smart Config Finder** is a configuration discovery engine that:

✅ **Maps configuration topology** - All config patterns, not just filenames  
✅ **Multi-language parsing** - .env, .yml, .json, .ts, .py, .js  
✅ **Semantic search** - Understands variants (PAYMENT_URL, paymentUrl, payment_url)  
✅ **Shadow detection** - Finds duplicates and conflicts  
✅ **Natural language queries** - "Where is paymentGatewayUrl set?"  

**It's like having a configuration expert who knows every config in your codebase!**

---

## ⚙️ How It Works

### **1. Config Topology Learning**

Scans the codebase to map configuration patterns:

**File Types:**
- `.env` files (all variants)
- `.yml`, `.yaml` files
- `.json` files
- Python constants (`config.py`, `settings.py`, `constants.py`)
- TypeScript/JavaScript constants (`config.ts`, `settings.ts`, `constants.ts`)

**Builds a semantic map:**
```
paymentGatewayUrl → .env (line 12)
paymentGatewayUrl → config/payment.yml (path: services.gateway.url)
paymentGatewayUrl → src/appSettings.ts (const PAYMENT_GATEWAY_URL)
```

---

### **2. Multi-Language Parsing**

**ENV Files (.env):**
```bash
PAYMENT_GATEWAY_URL=https://api.payment.com
DATABASE_URL=postgresql://localhost/db
```

**YAML Files (.yml):**
```yaml
services:
  gateway:
    url: https://api.payment.com
  database:
    url: postgresql://localhost/db
```

**JSON Files (.json):**
```json
{
  "services": {
    "gateway": {
      "url": "https://api.payment.com"
    }
  }
}
```

**Python Constants:**
```python
PAYMENT_GATEWAY_URL = "https://api.payment.com"
DATABASE_URL = "postgresql://localhost/db"
```

**TypeScript/JavaScript Constants:**
```typescript
export const PAYMENT_GATEWAY_URL = "https://api.payment.com";
export const DATABASE_URL = "postgresql://localhost/db";
```

---

### **3. Semantic Search**

Understands variants using:

**Normalization:**
- `PAYMENT_GATEWAY_URL` → `paymentgatewayurl`
- `paymentGatewayUrl` → `paymentgatewayurl`
- `payment_gateway_url` → `paymentgatewayurl`

**Matching Strategies:**
1. **Exact match** - `PAYMENT_URL` = `PAYMENT_URL` (score: 10.0)
2. **Case-insensitive** - `payment_url` = `PAYMENT_URL` (score: 9.0)
3. **Variant match** - `paymentUrl` = `PAYMENT_URL` (score: 8.0)
4. **Partial match** - `payment` in `PAYMENT_URL` (score: 5.0)
5. **Semantic match** - With OpenAI embeddings (score: 0-10)

---

### **4. Shadow Config Detection**

**Duplicates:**
- Same key, same value, different files
- Example: `DATABASE_URL` in both `.env` and `config.yml`

**Conflicts:**
- Same key, different values
- Example: `API_TIMEOUT=30` in `.env` but `API_TIMEOUT=60` in `config.yml`

---

### **5. Natural Language Queries**

**Input:**
```
"Where is paymentGatewayUrl set?"
```

**Output:**
```
Found in 3 locations:
1️⃣ .env → line 12 (PAYMENT_GATEWAY_URL)
2️⃣ config/payment.yml → services.gateway.url
3️⃣ src/appSettings.ts → const PAYMENT_GATEWAY_URL
```

---

## 🚀 Quick Start

### **Standalone CLI:**

```bash
python3 brain_config.py <config_key>
```

**Example:**
```bash
python3 brain_config.py paymentGatewayUrl
```

---

### **Integrated CLI:**

```bash
python3 brain_cli.py

🧠 > config paymentGatewayUrl
🧠 > config list
🧠 > config shadows
🧠 > config stats
```

---

## 💡 Example Output

### **Example 1: Find Config**

```bash
🧠 > config paymentGatewayUrl

======================================================================
🧭 SMART CONFIG FINDER
======================================================================

Query: paymentGatewayUrl

✅ Found 3 match(es):

1. .env
   Key: PAYMENT_GATEWAY_URL
   Value: https://api.payment.com
   Type: env
   Line: 12
   Match: variant (score: 8.0)

2. config/payment.yml
   Key: services.gateway.url
   Value: https://api.payment.com
   Type: yaml
   Match: semantic (score: 7.5)

3. src/appSettings.ts
   Key: PAYMENT_GATEWAY_URL
   Value: "https://api.payment.com"
   Type: ts_const
   Line: 45
   Match: variant (score: 8.0)

======================================================================
```

---

### **Example 2: List All Keys**

```bash
🧠 > config list

📋 All Config Keys (87):

   • API_KEY
   • API_TIMEOUT
   • DATABASE_URL
   • DEBUG
   • LOG_LEVEL
   • PAYMENT_GATEWAY_URL
   • PORT
   • REDIS_URL
   • SECRET_KEY
   • SMTP_HOST
   ... and 77 more
```

---

### **Example 3: Detect Shadow Configs**

```bash
🧠 > config shadows

======================================================================
👥 SHADOW CONFIG DETECTION
======================================================================

🔄 Duplicates (3):
   (Same key, same value, different files)

   Key: DATABASE_URL
   Value: postgresql://localhost/db
   Locations:
      • .env (line 5)
      • config/database.yml (line 0)

   Key: API_TIMEOUT
   Value: 30
   Locations:
      • .env (line 8)
      • src/config.ts (line 12)

⚠️  Conflicts (2):
   (Same key, different values)

   Key: LOG_LEVEL
   Values: DEBUG, INFO
   Locations:
      • .env: DEBUG (line 10)
      • config/logging.yml: INFO (line 0)

   Key: MAX_CONNECTIONS
   Values: 100, 50
   Locations:
      • .env: 100 (line 15)
      • config/database.yml: 50 (line 0)

======================================================================
```

---

### **Example 4: Config Statistics**

```bash
🧠 > config stats

======================================================================
📊 CONFIG STATISTICS
======================================================================

📈 Overview:
   Total unique keys: 87
   Total entries: 142

📁 By Type:
   env: 45
   yaml: 38
   json: 25
   ts_const: 18
   python_const: 12
   js_const: 4

📄 Top Files:
   .env: 45 entries
   config/app.yml: 22 entries
   config/database.yml: 16 entries
   src/config.ts: 18 entries
   backend/settings.py: 12 entries

======================================================================
```

---

## 🧠 Algorithm Details

### **Repo Scan Phase**

```python
for file in repo:
    if file.is_config():
        # Parse based on type
        if file.name.startswith('.env'):
            configs = parse_env_file(file)
        elif file.suffix in ['.yml', '.yaml']:
            configs = parse_yaml_file(file)
        elif file.suffix == '.json':
            configs = parse_json_file(file)
        elif file.suffix == '.py':
            configs = parse_python_file(file)
        elif file.suffix in ['.ts', '.js']:
            configs = parse_typescript_file(file)
        
        # Index configs
        for config in configs:
            config_map[config['key']].append(config)
```

---

### **Query Phase**

```python
# Normalize query
normalized_query = normalize_key(query)  # Remove _, -, lowercase

# Exact and variant matching
for key, configs in config_map.items():
    normalized_key = normalize_key(key)
    
    if key == query:
        score = 10.0  # Exact match
    elif key.lower() == query.lower():
        score = 9.0   # Case-insensitive
    elif normalized_key == normalized_query:
        score = 8.0   # Variant match
    elif normalized_query in normalized_key:
        score = 5.0   # Partial match

# Semantic matching (optional, with OpenAI)
if openai_enabled:
    query_embedding = embed(query)
    for key, configs in config_map.items():
        key_embedding = embed(key)
        similarity = cosine_similarity(query_embedding, key_embedding)
        if similarity > 0.7:
            score = similarity * 10

# Sort by score
results.sort(key=lambda x: x['score'], reverse=True)
```

---

## 🔍 Parsing Details

### **ENV File Parsing**

```python
# Pattern: KEY=VALUE
match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$', line)

# Example:
PAYMENT_URL=https://api.com
# → key: PAYMENT_URL, value: https://api.com
```

---

### **YAML File Parsing**

```python
# Parse YAML
data = yaml.safe_load(file)

# Flatten nested structure
services:
  gateway:
    url: https://api.com

# → key: services.gateway.url, value: https://api.com
```

---

### **JSON File Parsing**

```python
# Parse JSON
data = json.load(file)

# Flatten nested structure
{
  "services": {
    "gateway": {
      "url": "https://api.com"
    }
  }
}

# → key: services.gateway.url, value: https://api.com
```

---

### **Python Constant Parsing**

```python
# Pattern: UPPERCASE = value
pattern = r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.+)$'

# Example:
PAYMENT_URL = "https://api.com"
# → key: PAYMENT_URL, value: "https://api.com"
```

---

### **TypeScript/JavaScript Constant Parsing**

```python
# Pattern: const UPPERCASE = value
pattern = r'(?:export\s+)?const\s+([A-Z_][A-Z0-9_]*)\s*[:=]\s*(.+?)(?:;|$)'

# Example:
export const PAYMENT_URL = "https://api.com";
# → key: PAYMENT_URL, value: "https://api.com"
```

---

## 🎯 Use Cases

### **Use Case 1: Finding Config Location**

```bash
# Problem: Where is the payment URL configured?

🧠 > config paymentUrl

# Shows all locations where payment URL is defined
# Across .env, YAML, JSON, TypeScript, Python
```

---

### **Use Case 2: Detecting Conflicts**

```bash
# Problem: Different environments have different values

🧠 > config shadows

# Shows:
# - Duplicates (same value, multiple files)
# - Conflicts (different values for same key)
```

---

### **Use Case 3: Config Audit**

```bash
# Problem: How many configs do we have?

🧠 > config stats

# Shows:
# - Total keys and entries
# - Breakdown by type
# - Top files with most configs
```

---

### **Use Case 4: Variant Matching**

```bash
# Problem: Config might be named differently

🧠 > config payment_gateway_url

# Finds:
# - PAYMENT_GATEWAY_URL (.env)
# - paymentGatewayUrl (config.ts)
# - payment.gateway.url (config.yml)
```

---

## 🧩 Tech Stack

| Purpose | Technology |
|---------|-----------|
| **Embeddings** | OpenAI text-embedding-3-small |
| **YAML Parsing** | PyYAML |
| **JSON Parsing** | Python stdlib json |
| **Regex Parsing** | Python re module |
| **Similarity** | Cosine similarity (NumPy or fallback) |
| **Caching** | JSON file (.brain_config_embeddings.json) |

---

## 🪄 Bonus Features

### **1. Shadow Config Detection**

Finds:
- **Duplicates** - Same key, same value, different files
- **Conflicts** - Same key, different values

**Why it matters:**
- Duplicates → Maintenance burden
- Conflicts → Production bugs

---

### **2. Variant Matching**

Understands:
- `PAYMENT_URL` (env style)
- `paymentUrl` (camelCase)
- `payment_url` (snake_case)
- `payment.url` (dot notation)

**All match the same concept!**

---

### **3. Semantic Search (Optional)**

With OpenAI embeddings:
- Understands conceptual similarity
- Finds related configs
- Works across naming conventions

---

## 📊 Performance

### **Without OpenAI (Keyword Only):**
- ⚡ **Speed:** <100ms
- 💰 **Cost:** $0
- 🎯 **Accuracy:** Good for exact/variant matches

### **With OpenAI (Semantic):**
- ⚡ **Speed:** 1-3 seconds (first query)
- ⚡ **Speed:** <100ms (cached)
- 💰 **Cost:** ~$0.001 per query
- 🎯 **Accuracy:** Excellent for conceptual matches

---

## 🎉 Summary

**The Smart Config Finder provides:**

✅ **Config Topology Learning** - Maps all config patterns  
✅ **Multi-Language Parsing** - .env, .yml, .json, .ts, .py, .js  
✅ **Semantic Search** - Understands variants  
✅ **Shadow Detection** - Finds duplicates and conflicts  
✅ **Natural Language Queries** - "Where is X set?"  
✅ **Statistics** - Config audit and analysis  
✅ **CLI Integration** - Built into brain_cli.py  
✅ **Standalone Mode** - Can run independently  

**Your project now knows where every config is!** 🧭✨

---

## 🚀 Try It Now!

```bash
cd screenshot-app

# Standalone
python3 brain_config.py paymentGatewayUrl

# Integrated
python3 brain_cli.py
🧠 > config DATABASE_URL
🧠 > config list
🧠 > config shadows
🧠 > config stats
```

**Never grep for configs again!** 🧭🔍

