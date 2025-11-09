# 🦊 Camoufox Cookie Management - Complete Research

**Research Date:** November 3, 2025  
**Focus:** Cookie management for Camoufox (Firefox-based) vs Playwright (Chromium-based)

---

## 🎯 Key Differences: Camoufox vs Playwright

### **Architecture**

| Feature | Playwright (Chromium) | Camoufox (Firefox) |
|---------|----------------------|-------------------|
| **Base Browser** | Chromium | Firefox (patched) |
| **Protocol** | CDP (Chrome DevTools Protocol) | Juggler (Firefox protocol) |
| **Cookie Storage** | Chrome format (encrypted) | Firefox format (cookies.sqlite) |
| **Persistent Context** | Optional | ✅ **Built-in** (recommended) |
| **Profile Directory** | `user_data_dir` | `user_data_dir` |
| **Storage Files** | Multiple files | `cookies.sqlite`, `webappsstore.sqlite` |

---

## 🍪 Cookie Extraction Methods

### **Method 1: rookiepy (RECOMMENDED for both)**

**Works with BOTH Chromium AND Firefox!**

```python
import rookiepy

# Extract from Chrome (for Playwright)
chrome_cookies = rookiepy.chrome(["zomato.com"])

# Extract from Firefox (for Camoufox)
firefox_cookies = rookiepy.firefox(["zomato.com"])

# Extract from ANY browser
any_cookies = rookiepy.any(["zomato.com"])
```

**Why rookiepy is perfect:**
- ✅ Supports **both Chrome AND Firefox**
- ✅ Handles Firefox's `cookies.sqlite` format
- ✅ Handles Chrome's encrypted cookies
- ✅ Same API for both browsers
- ✅ Rust-based (fast and secure)

---

### **Method 2: Camoufox Persistent Context (RECOMMENDED)**

**Camoufox's BEST feature: Built-in persistent context**

```python
from camoufox.async_api import AsyncCamoufox

# Launch with persistent context
async with AsyncCamoufox(
    persistent_context=True,
    user_data_dir='/path/to/profile',
    headless=False
) as context:
    page = await context.new_page()
    
    # Login manually or programmatically
    await page.goto('https://example.com/login')
    # ... login ...
    
    # Cookies are AUTOMATICALLY saved to profile!
    # No need to call storage_state()
```

**How it works:**
- ✅ Cookies saved to `user_data_dir/cookies.sqlite`
- ✅ localStorage saved to `user_data_dir/webappsstore.sqlite`
- ✅ sessionStorage saved to `user_data_dir/sessionstore.jsonlz4`
- ✅ IndexedDB saved to `user_data_dir/storage/default/`
- ✅ **Everything persists automatically!**

**Reuse the session:**

```python
# Later, just launch with same user_data_dir
async with AsyncCamoufox(
    persistent_context=True,
    user_data_dir='/path/to/profile',  # Same profile!
    headless=True
) as context:
    page = await context.new_page()
    
    # Already logged in! ✅
    await page.goto('https://example.com/dashboard')
```

---

### **Method 3: Firefox cookies.sqlite Direct Access**

**For advanced users who want direct database access**

```python
import sqlite3
import json
from pathlib import Path

def extract_firefox_cookies(profile_dir: str, domain: str = None):
    """
    Extract cookies from Firefox cookies.sqlite database
    
    Args:
        profile_dir: Path to Firefox profile directory
        domain: Optional domain filter (e.g., ".zomato.com")
    
    Returns:
        List of cookie dictionaries
    """
    cookies_db = Path(profile_dir) / "cookies.sqlite"
    
    if not cookies_db.exists():
        raise FileNotFoundError(f"cookies.sqlite not found in {profile_dir}")
    
    # Connect to SQLite database
    conn = sqlite3.connect(str(cookies_db))
    cursor = conn.cursor()
    
    # Query cookies
    if domain:
        query = "SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite FROM moz_cookies WHERE host LIKE ?"
        cursor.execute(query, (f"%{domain}%",))
    else:
        query = "SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite FROM moz_cookies"
        cursor.execute(query)
    
    cookies = []
    for row in cursor.fetchall():
        cookie = {
            "name": row[0],
            "value": row[1],
            "domain": row[2],
            "path": row[3],
            "expires": row[4],
            "secure": bool(row[5]),
            "httpOnly": bool(row[6]),
            "sameSite": ["None", "Lax", "Strict"][row[7]] if row[7] else "Lax"
        }
        cookies.append(cookie)
    
    conn.close()
    return cookies

# Usage
profile_dir = "browser_sessions/camoufox_profile"
cookies = extract_firefox_cookies(profile_dir, ".zomato.com")
```

**Pros:**
- ✅ Direct database access
- ✅ No dependencies
- ✅ Full control

**Cons:**
- ❌ More complex
- ❌ Need to handle SQLite format
- ❌ rookiepy does this automatically

---

## 🔄 Cookie Format Conversion

### **Camoufox → Playwright**

If you need to use Camoufox cookies in Playwright:

```python
def camoufox_to_playwright_cookies(camoufox_cookies):
    """Convert Camoufox/Firefox cookies to Playwright format"""
    playwright_cookies = []
    
    for cookie in camoufox_cookies:
        playwright_cookie = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie["domain"],
            "path": cookie.get("path", "/"),
            "expires": cookie.get("expires", -1),
            "httpOnly": cookie.get("httpOnly", False),
            "secure": cookie.get("secure", False),
            "sameSite": cookie.get("sameSite", "Lax")
        }
        playwright_cookies.append(playwright_cookie)
    
    return {
        "cookies": playwright_cookies,
        "origins": []
    }
```

### **Playwright → Camoufox**

If you need to use Playwright cookies in Camoufox:

```python
def playwright_to_camoufox_cookies(storage_state):
    """Convert Playwright storage_state to Camoufox format"""
    # Camoufox uses same format as Playwright!
    # Just extract cookies from storage_state
    return storage_state.get("cookies", [])
```

**Good news:** Camoufox and Playwright use **compatible cookie formats**!

---

## 🏗️ Your Current Implementation

### **What You're Already Doing (EXCELLENT!)**

From `screenshot_service.py`:

```python
# Camoufox with persistent context
persistent_profile_dir = Path("browser_sessions/camoufox_profile")

self.camoufox_browser = await AsyncCamoufox(
    headless=not use_real_browser,
    humanize=True,
    block_webrtc=True,
    config=camoufox_config,
    persistent_context=True,  # ✅ PERFECT!
    user_data_dir=str(persistent_profile_dir),  # ✅ PERFECT!
).__aenter__()
```

**This is the BEST approach!** ✅

**Why:**
- ✅ Cookies persist automatically
- ✅ No manual save/load needed
- ✅ Works across sessions
- ✅ Handles all storage types (cookies, localStorage, sessionStorage, IndexedDB)

---

## 🚀 Recommended Cookie Strategy

### **For Your 3-Tier Stealth System:**

```
Priority 1: Patchright (Chromium)
    ↓
Priority 2: Rebrowser (Chromium)
    ↓
Priority 3: Camoufox (Firefox)
```

### **Cookie Management Strategy:**

#### **Option A: Separate Profiles (RECOMMENDED)**

**Use different cookie sources for different browsers:**

```python
# For Patchright/Rebrowser (Chromium)
chrome_cookies = rookiepy.chrome(["zomato.com"])
playwright_storage_state = convert_to_playwright_format(chrome_cookies)

# For Camoufox (Firefox)
firefox_cookies = rookiepy.firefox(["zomato.com"])
# OR use persistent context (even better!)
```

**Why separate:**
- ✅ Chrome cookies work best with Chromium browsers
- ✅ Firefox cookies work best with Firefox browsers
- ✅ Avoids compatibility issues
- ✅ More realistic fingerprinting

---

#### **Option B: Universal Cookies (SIMPLER)**

**Use rookiepy.any() to extract from any browser:**

```python
# Extract from whatever browser user is logged in to
cookies = rookiepy.any(["zomato.com"])

# Use in both Playwright AND Camoufox
playwright_storage_state = convert_to_playwright_format(cookies)
camoufox_cookies = cookies  # Same format!
```

**Why universal:**
- ✅ Simpler implementation
- ✅ Works with any browser
- ✅ User doesn't need specific browser
- ✅ Cookie format is compatible

---

## 💻 Implementation for Your Tool

### **Update `cookie_extractor.py`**

Add Camoufox-specific methods:

```python
class CookieExtractor:
    def extract_for_camoufox(self, domains: Optional[List[str]] = None) -> List[Dict]:
        """
        Extract cookies optimized for Camoufox (Firefox-based)
        
        Priority:
        1. Firefox cookies (best match)
        2. Any browser cookies (fallback)
        """
        try:
            # Try Firefox first (best for Camoufox)
            cookies = rookiepy.firefox(domains) if domains else rookiepy.firefox()
            print(f"✅ Extracted {len(cookies)} cookies from Firefox (optimal for Camoufox)")
            return cookies
        except Exception as e:
            print(f"⚠️  Firefox not available, trying any browser...")
            try:
                cookies = rookiepy.any(domains) if domains else rookiepy.any()
                print(f"✅ Extracted {len(cookies)} cookies from browser")
                return cookies
            except Exception as e2:
                print(f"❌ Failed to extract cookies: {e2}")
                return []
    
    def extract_for_playwright(self, domains: Optional[List[str]] = None) -> List[Dict]:
        """
        Extract cookies optimized for Playwright (Chromium-based)
        
        Priority:
        1. Chrome cookies (best match)
        2. Any browser cookies (fallback)
        """
        try:
            # Try Chrome first (best for Playwright)
            cookies = rookiepy.chrome(domains) if domains else rookiepy.chrome()
            print(f"✅ Extracted {len(cookies)} cookies from Chrome (optimal for Playwright)")
            return cookies
        except Exception as e:
            print(f"⚠️  Chrome not available, trying any browser...")
            try:
                cookies = rookiepy.any(domains) if domains else rookiepy.any()
                print(f"✅ Extracted {len(cookies)} cookies from browser")
                return cookies
            except Exception as e2:
                print(f"❌ Failed to extract cookies: {e2}")
                return []
    
    def inject_cookies_to_camoufox_profile(
        self,
        cookies: List[Dict],
        profile_dir: str = "browser_sessions/camoufox_profile"
    ):
        """
        Inject cookies directly into Camoufox profile's cookies.sqlite
        
        This is an ALTERNATIVE to using persistent_context.
        Only use if you need manual cookie injection.
        """
        import sqlite3
        from pathlib import Path
        
        profile_path = Path(profile_dir)
        profile_path.mkdir(parents=True, exist_ok=True)
        
        cookies_db = profile_path / "cookies.sqlite"
        
        # Create cookies.sqlite if it doesn't exist
        # (Normally Camoufox creates this automatically)
        conn = sqlite3.connect(str(cookies_db))
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moz_cookies (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value TEXT,
                host TEXT,
                path TEXT,
                expiry INTEGER,
                lastAccessed INTEGER,
                creationTime INTEGER,
                isSecure INTEGER,
                isHttpOnly INTEGER,
                sameSite INTEGER
            )
        ''')
        
        # Insert cookies
        for cookie in cookies:
            cursor.execute('''
                INSERT OR REPLACE INTO moz_cookies
                (name, value, host, path, expiry, isSecure, isHttpOnly, sameSite)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cookie["name"],
                cookie["value"],
                cookie["domain"],
                cookie.get("path", "/"),
                cookie.get("expires", -1),
                1 if cookie.get("secure", False) else 0,
                1 if cookie.get("httpOnly", False) else 0,
                ["None", "Lax", "Strict"].index(cookie.get("sameSite", "Lax"))
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Injected {len(cookies)} cookies into Camoufox profile")
```

---

## 🎯 Best Practices

### **1. Use Persistent Context (RECOMMENDED)**

```python
# ✅ BEST: Let Camoufox handle cookies automatically
async with AsyncCamoufox(
    persistent_context=True,
    user_data_dir='browser_sessions/camoufox_profile'
) as context:
    # Cookies persist automatically!
    pass
```

### **2. Extract from Matching Browser**

```python
# For Camoufox (Firefox-based)
firefox_cookies = rookiepy.firefox()

# For Playwright (Chromium-based)
chrome_cookies = rookiepy.chrome()
```

### **3. Separate Profiles for Login vs Capture**

```python
# Login profile (your current implementation ✅)
login_profile = "browser_sessions/camoufox_profile_login"

# Main profile (your current implementation ✅)
main_profile = "browser_sessions/camoufox_profile"

# Copy login profile to main profile after successful login
shutil.copytree(login_profile, main_profile, dirs_exist_ok=True)
```

**This is EXACTLY what you're already doing!** ✅

---

## 📊 Comparison: Cookie Methods

| Method | Playwright | Camoufox | Complexity | Recommended |
|--------|-----------|----------|------------|-------------|
| **rookiepy** | ✅ Chrome | ✅ Firefox | Low | ✅ **YES** |
| **Persistent Context** | ✅ Yes | ✅ **Built-in** | Low | ✅ **YES** |
| **storage_state()** | ✅ Yes | ✅ Yes | Low | ✅ **YES** |
| **Direct SQLite** | ❌ Complex | ✅ Yes | High | ⚠️ Advanced |
| **Browser Extension** | ✅ Yes | ✅ Yes | Medium | ⚠️ Manual |

---

## ✅ Summary

### **What You Should Use:**

1. **rookiepy** - Extract cookies from browser
   - `rookiepy.chrome()` for Playwright
   - `rookiepy.firefox()` for Camoufox
   - `rookiepy.any()` for universal

2. **Camoufox persistent_context** - Automatic cookie persistence
   - Already implemented in your code ✅
   - Best approach for Camoufox

3. **Playwright storage_state** - Manual cookie save/load
   - Good for Patchright/Rebrowser
   - Compatible with Camoufox

### **Your Current Implementation: EXCELLENT!** ✅

You're already using:
- ✅ Persistent context for Camoufox
- ✅ Separate login profile
- ✅ Profile copying after login
- ✅ Automatic cookie persistence

**No changes needed for Camoufox!** Just add rookiepy for initial cookie extraction.

---

## 🚀 Next Steps

1. ✅ Install rookiepy: `pip install rookiepy`
2. ✅ Add `extract_for_camoufox()` method to `cookie_extractor.py`
3. ✅ Add `extract_for_playwright()` method to `cookie_extractor.py`
4. ✅ Keep your existing persistent context implementation (it's perfect!)
5. ✅ Test with both Playwright and Camoufox

---

**Your Camoufox implementation is already optimal!** 🎉  
**Just add rookiepy for initial cookie extraction and you're done!** 🚀

