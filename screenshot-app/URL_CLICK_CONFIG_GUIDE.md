# 🎯 URL-Specific Click Configuration Guide

## Overview

The screenshot tool now supports **URL-specific click configurations** that are automatically applied when capturing screenshots. This allows you to define click actions for specific URLs that are remembered and reused across sessions.

## ✅ Features

- **Automatic Click Actions**: Define click actions for specific URLs that are applied automatically
- **Backward Compatible**: Manual `click_elements` parameter still works when no configuration is found
- **Multiple Actions**: Support for sequential click actions with custom wait times
- **Flexible Matching**: Exact, contains, startswith, or regex URL matching
- **Enable/Disable**: Turn configurations on/off without deleting them
- **Easy to Edit**: Simple JSON configuration file

---

## 📋 Configuration File

### Location
`screenshot-app/backend/url_click_config.json`

### Structure

```json
{
  "version": "1.0",
  "description": "URL-specific click action configurations for screenshot tool",
  "url_patterns": [
    {
      "id": "unique-identifier",
      "name": "Human-readable name",
      "url_pattern": "https://example.com/page",
      "match_type": "exact",
      "actions": [
        {
          "type": "click",
          "text": "Button Text",
          "wait_after_ms": 2000,
          "description": "Optional description"
        }
      ],
      "enabled": true,
      "created_at": "2025-11-11",
      "notes": "Optional notes"
    }
  ]
}
```

---

## 🔧 Configuration Fields

### Pattern Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for this configuration |
| `name` | string | Yes | Human-readable name |
| `url_pattern` | string | Yes | URL pattern to match |
| `match_type` | enum | Yes | `"exact"`, `"contains"`, `"startswith"`, or `"regex"` |
| `actions` | array | Yes | List of actions to perform |
| `enabled` | boolean | Yes | Enable/disable this configuration |
| `created_at` | string | No | Creation date (for reference) |
| `notes` | string | No | Additional notes |

### Action Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | Yes | Action type: `"click"` (more types coming soon) |
| `text` | string | Yes | Text to search for and click |
| `wait_after_ms` | int | Yes | Milliseconds to wait after action (default: 2000) |
| `description` | string | No | Optional description of what this action does |

---

## 📝 Examples

### Example 1: Single Click Action

```json
{
  "id": "tekion-return-reasons-edit",
  "name": "Tekion - Return Reasons - Edit Customer Return",
  "url_pattern": "https://preprodapp.tekioncloud.com/parts/return-reasons",
  "match_type": "exact",
  "actions": [
    {
      "type": "click",
      "text": "Customer Return w/ Restocking",
      "wait_after_ms": 2000,
      "description": "Opens the Edit Reason modal"
    }
  ],
  "enabled": true
}
```

### Example 2: Multiple Sequential Clicks

```json
{
  "id": "dashboard-settings-advanced",
  "name": "Dashboard - Open Advanced Settings",
  "url_pattern": "https://example.com/dashboard",
  "match_type": "exact",
  "actions": [
    {
      "type": "click",
      "text": "Settings",
      "wait_after_ms": 1000,
      "description": "Opens settings menu"
    },
    {
      "type": "click",
      "text": "Advanced",
      "wait_after_ms": 1000,
      "description": "Opens advanced settings tab"
    },
    {
      "type": "click",
      "text": "Show Details",
      "wait_after_ms": 2000,
      "description": "Expands details section"
    }
  ],
  "enabled": true
}
```

### Example 3: Contains Matching

```json
{
  "id": "product-view-all",
  "name": "Product Pages - View All Items",
  "url_pattern": "/products/",
  "match_type": "contains",
  "actions": [
    {
      "type": "click",
      "text": "View All",
      "wait_after_ms": 1500
    }
  ],
  "enabled": true
}
```

### Example 4: Regex Matching

```json
{
  "id": "user-profile-edit",
  "name": "User Profile - Edit Mode",
  "url_pattern": "https://example\\.com/users/[0-9]+/profile",
  "match_type": "regex",
  "actions": [
    {
      "type": "click",
      "text": "Edit Profile",
      "wait_after_ms": 2000
    }
  ],
  "enabled": true
}
```

---

## 🚀 How It Works

### Priority Order

1. **URL Configuration** (if match found)
   - Checks `url_click_config.json` for matching URL pattern
   - Executes configured actions automatically
   
2. **Manual Parameter** (if no match found)
   - Falls back to `click_elements` parameter from API request
   - Maintains backward compatibility

### Matching Logic

```python
# Exact match
if url == "https://example.com/page":
    # Use this configuration

# Contains match
if "/products/" in url:
    # Use this configuration

# Startswith match
if url.startswith("https://example.com/dashboard"):
    # Use this configuration

# Regex match
if re.match(r"https://example\.com/users/[0-9]+", url):
    # Use this configuration
```

---

## 📊 Usage Examples

### Using URL Configuration (Automatic)

```python
import requests

# URL matches configuration - actions applied automatically
payload = {
    "urls": ["https://preprodapp.tekioncloud.com/parts/return-reasons"],
    "capture_mode": "viewport",
    "use_real_browser": True
}

response = requests.post("http://localhost:8000/api/screenshots/capture", json=payload)
```

**Output:**
```
📋 Found saved configuration: 'Tekion - Return Reasons - Edit Customer Return'
   🖱️  Action 1/1: Click 'Customer Return w/ Restocking'
      ℹ️  Opens the Edit Reason modal
   ✅ All configured actions completed
```

### Using Manual Parameter (Backward Compatible)

```python
import requests

# URL doesn't match any configuration - use manual parameter
payload = {
    "urls": ["https://example.com/other-page"],
    "capture_mode": "viewport",
    "use_real_browser": True,
    "click_elements": ["Button Text", "Another Button"]  # Manual
}

response = requests.post("http://localhost:8000/api/screenshots/capture", json=payload)
```

**Output:**
```
🖱️  Using manual click elements: ['Button Text', 'Another Button']
```

---

## 🔄 Adding New Configurations

### Step 1: Edit Configuration File

Open `screenshot-app/backend/url_click_config.json` and add a new pattern:

```json
{
  "version": "1.0",
  "url_patterns": [
    {
      "id": "my-new-config",
      "name": "My New Configuration",
      "url_pattern": "https://example.com/my-page",
      "match_type": "exact",
      "actions": [
        {
          "type": "click",
          "text": "Click Me",
          "wait_after_ms": 2000
        }
      ],
      "enabled": true
    }
  ]
}
```

### Step 2: Restart Backend

```bash
cd screenshot-app/backend
lsof -ti:8000 | xargs kill -9
python3 main.py
```

### Step 3: Test

```python
import requests

payload = {
    "urls": ["https://example.com/my-page"],
    "capture_mode": "viewport",
    "use_real_browser": True
}

response = requests.post("http://localhost:8000/api/screenshots/capture", json=payload)
```

---

## 🎯 Best Practices

### 1. Use Descriptive Names
```json
{
  "name": "Tekion - Return Reasons - Edit Customer Return",  // ✅ Good
  "name": "Config 1"  // ❌ Bad
}
```

### 2. Add Descriptions to Actions
```json
{
  "actions": [
    {
      "type": "click",
      "text": "Edit",
      "description": "Opens the edit modal"  // ✅ Helpful
    }
  ]
}
```

### 3. Use Appropriate Match Types
- **exact**: For specific pages (e.g., `/parts/return-reasons`)
- **contains**: For URL patterns (e.g., `/products/`)
- **startswith**: For URL prefixes (e.g., `https://example.com/dashboard`)
- **regex**: For complex patterns (e.g., `/users/[0-9]+/profile`)

### 4. Set Reasonable Wait Times
```json
{
  "wait_after_ms": 2000  // ✅ Good for modals
  "wait_after_ms": 500   // ✅ Good for simple clicks
  "wait_after_ms": 10000 // ⚠️  Too long
}
```

### 5. Disable Instead of Delete
```json
{
  "enabled": false  // ✅ Temporarily disable
  // Delete the whole object  // ❌ Lose configuration
}
```

---

## 🐛 Troubleshooting

### Configuration Not Loading

**Check logs:**
```bash
tail -50 backend.log | grep "📋"
```

**Expected output:**
```
📋 Loaded 1 URL-specific click configurations
```

### URL Not Matching

**Check match type:**
- Exact: URL must match exactly
- Contains: Pattern must be substring of URL
- Startswith: URL must start with pattern
- Regex: URL must match regex pattern

**Enable debug logging:**
```python
# In screenshot_service.py
print(f"   🔍 Checking URL: {url}")
print(f"   🔍 Pattern: {url_pattern}")
print(f"   🔍 Match type: {match_type}")
```

### Click Not Working

**Check element text:**
- Text must match exactly or be contained in element
- Text is case-sensitive
- Check for extra spaces or special characters

**Test manually:**
```python
await page.evaluate("""() => {
    const allElements = document.querySelectorAll('*');
    for (const el of allElements) {
        if (el.textContent.includes('Your Text')) {
            console.log('Found:', el);
        }
    }
}""")
```

---

## 📚 Summary

✅ **URL-specific configurations** are automatically applied when URL matches
✅ **Manual `click_elements`** parameter still works (backward compatible)
✅ **Easy to add** new configurations via JSON file
✅ **Flexible matching** (exact, contains, startswith, regex)
✅ **Multiple actions** supported with custom wait times
✅ **Enable/disable** configurations without deleting

**Configuration file:** `screenshot-app/backend/url_click_config.json`

