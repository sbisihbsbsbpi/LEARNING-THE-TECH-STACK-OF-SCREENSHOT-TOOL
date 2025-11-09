# 🍪 Cookie Import Feature - Implementation Guide

**Based on:** Complete research in `COOKIE_TOKEN_LIBRARIES_RESEARCH.md`  
**Recommended Solution:** rookiepy + Playwright storage_state

---

## 🎯 Goal

Import cookies from your logged-in browser to reuse sessions across headless captures for 56 URLs without manual login each time.

---

## 📦 Installation

```bash
# Install rookiepy for cookie extraction
pip install rookiepy

# Playwright already installed ✅
```

---

## 🏗️ Architecture

```
┌─────────────────────┐
│  Your Browser       │
│  (Logged in to      │
│   Zomato, etc.)     │
└──────────┬──────────┘
           │
           │ rookiepy.chrome()
           ▼
┌─────────────────────┐
│  Extract Cookies    │
│  (Python)           │
└──────────┬──────────┘
           │
           │ Convert format
           ▼
┌─────────────────────┐
│  Playwright         │
│  storage_state.json │
└──────────┬──────────┘
           │
           │ Load in context
           ▼
┌─────────────────────┐
│  Headless Browser   │
│  (Already logged in)│
└─────────────────────┘
```

---

## 💻 Implementation

### **File 1: `backend/cookie_extractor.py`**

```python
"""
Cookie Extractor - Extract cookies from browser and convert to Playwright format
"""
import rookiepy
import json
from typing import List, Dict, Optional
from pathlib import Path


class CookieExtractor:
    """Extract cookies from browser and convert to Playwright storage_state format"""
    
    def __init__(self, storage_dir: str = "browser_sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def extract_from_chrome(self, domains: Optional[List[str]] = None) -> List[Dict]:
        """
        Extract cookies from Chrome browser
        
        Args:
            domains: List of domains to extract cookies for (e.g., ["zomato.com"])
                    If None, extracts all cookies
        
        Returns:
            List of cookie dictionaries
        """
        try:
            if domains:
                cookies = rookiepy.chrome(domains)
            else:
                cookies = rookiepy.chrome()
            
            print(f"✅ Extracted {len(cookies)} cookies from Chrome")
            return cookies
        except Exception as e:
            print(f"❌ Failed to extract cookies from Chrome: {e}")
            return []
    
    def extract_from_firefox(self, domains: Optional[List[str]] = None) -> List[Dict]:
        """Extract cookies from Firefox browser"""
        try:
            if domains:
                cookies = rookiepy.firefox(domains)
            else:
                cookies = rookiepy.firefox()
            
            print(f"✅ Extracted {len(cookies)} cookies from Firefox")
            return cookies
        except Exception as e:
            print(f"❌ Failed to extract cookies from Firefox: {e}")
            return []
    
    def extract_from_any(self, domains: Optional[List[str]] = None) -> List[Dict]:
        """Extract cookies from any available browser"""
        try:
            if domains:
                cookies = rookiepy.any(domains)
            else:
                cookies = rookiepy.any()
            
            print(f"✅ Extracted {len(cookies)} cookies from browser")
            return cookies
        except Exception as e:
            print(f"❌ Failed to extract cookies: {e}")
            return []
    
    def convert_to_playwright_format(self, rookiepy_cookies: List[Dict]) -> Dict:
        """
        Convert rookiepy cookies to Playwright storage_state format
        
        Args:
            rookiepy_cookies: List of cookies from rookiepy
        
        Returns:
            Playwright storage_state dictionary
        """
        playwright_cookies = []
        
        for cookie in rookiepy_cookies:
            playwright_cookie = {
                "name": cookie.get("name", ""),
                "value": cookie.get("value", ""),
                "domain": cookie.get("domain", ""),
                "path": cookie.get("path", "/"),
                "expires": cookie.get("expires", -1),
                "httpOnly": cookie.get("httpOnly", False),
                "secure": cookie.get("secure", False),
                "sameSite": cookie.get("sameSite", "Lax")
            }
            playwright_cookies.append(playwright_cookie)
        
        storage_state = {
            "cookies": playwright_cookies,
            "origins": []
        }
        
        return storage_state
    
    def save_storage_state(self, storage_state: Dict, filename: str = "auth_state.json") -> str:
        """
        Save storage_state to file
        
        Args:
            storage_state: Playwright storage_state dictionary
            filename: Output filename
        
        Returns:
            Path to saved file
        """
        filepath = self.storage_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(storage_state, f, indent=2)
        
        print(f"✅ Saved storage state to {filepath}")
        return str(filepath)
    
    def load_storage_state(self, filename: str = "auth_state.json") -> Optional[Dict]:
        """Load storage_state from file"""
        filepath = self.storage_dir / filename
        
        if not filepath.exists():
            print(f"❌ Storage state file not found: {filepath}")
            return None
        
        with open(filepath, 'r') as f:
            storage_state = json.load(f)
        
        print(f"✅ Loaded storage state from {filepath}")
        return storage_state
    
    def extract_and_save(
        self, 
        domains: Optional[List[str]] = None,
        browser: str = "chrome",
        filename: str = "auth_state.json"
    ) -> str:
        """
        Extract cookies from browser and save as Playwright storage_state
        
        Args:
            domains: List of domains to extract cookies for
            browser: Browser to extract from ("chrome", "firefox", "any")
            filename: Output filename
        
        Returns:
            Path to saved storage_state file
        """
        # Extract cookies
        if browser == "chrome":
            cookies = self.extract_from_chrome(domains)
        elif browser == "firefox":
            cookies = self.extract_from_firefox(domains)
        else:
            cookies = self.extract_from_any(domains)
        
        if not cookies:
            raise Exception("No cookies extracted")
        
        # Convert to Playwright format
        storage_state = self.convert_to_playwright_format(cookies)
        
        # Save to file
        filepath = self.save_storage_state(storage_state, filename)
        
        return filepath


# Example usage
if __name__ == "__main__":
    extractor = CookieExtractor()
    
    # Extract cookies for specific domains
    domains = ["zomato.com", "swiggy.com"]
    
    # Extract and save
    filepath = extractor.extract_and_save(
        domains=domains,
        browser="chrome",
        filename="food_delivery_auth.json"
    )
    
    print(f"✅ Done! Storage state saved to: {filepath}")
```

---

### **File 2: Update `backend/screenshot_service.py`**

Add method to use storage_state:

```python
async def capture_with_auth_state(
    self,
    url: str,
    storage_state_path: str,
    stealth_mode: str = "patchright",
    **kwargs
) -> dict:
    """
    Capture screenshot using saved authentication state
    
    Args:
        url: URL to capture
        storage_state_path: Path to storage_state.json file
        stealth_mode: Stealth mode to use
        **kwargs: Additional capture options
    
    Returns:
        Capture result dictionary
    """
    try:
        # Load storage state
        with open(storage_state_path, 'r') as f:
            storage_state = json.load(f)
        
        # Launch browser with storage state
        if stealth_mode == "patchright":
            browser = await self.patchright.chromium.launch(headless=True)
            context = await browser.new_context(storage_state=storage_state)
        elif stealth_mode == "rebrowser":
            browser = await self.rebrowser.chromium.launch(headless=True)
            context = await browser.new_context(storage_state=storage_state)
        else:  # camoufox
            # Camoufox uses persistent context, need different approach
            # For now, use patchright as fallback
            browser = await self.patchright.chromium.launch(headless=True)
            context = await browser.new_context(storage_state=storage_state)
        
        page = await context.new_page()
        
        # Navigate to URL (already authenticated!)
        await page.goto(url, wait_until="networkidle")
        
        # Capture screenshot
        screenshot_bytes = await page.screenshot(full_page=kwargs.get('full_page', True))
        
        # Close
        await browser.close()
        
        return {
            "success": True,
            "screenshot": screenshot_bytes,
            "url": url
        }
    
    except Exception as e:
        logger.error(f"Failed to capture with auth state: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url
        }
```

---

### **File 3: Add API Endpoint in `backend/main.py`**

```python
from cookie_extractor import CookieExtractor

# Initialize cookie extractor
cookie_extractor = CookieExtractor()


@app.post("/api/extract-cookies")
async def extract_cookies(
    domains: Optional[List[str]] = None,
    browser: str = "chrome"
):
    """
    Extract cookies from browser and save as storage_state
    
    Args:
        domains: List of domains to extract cookies for
        browser: Browser to extract from ("chrome", "firefox", "any")
    
    Returns:
        Success status and filepath
    """
    try:
        filepath = cookie_extractor.extract_and_save(
            domains=domains,
            browser=browser,
            filename="auth_state.json"
        )
        
        return {
            "success": True,
            "filepath": filepath,
            "message": f"Extracted cookies and saved to {filepath}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/capture-with-auth")
async def capture_with_auth(
    url: str,
    storage_state_file: str = "auth_state.json",
    stealth_mode: str = "patchright"
):
    """
    Capture screenshot using saved authentication state
    
    Args:
        url: URL to capture
        storage_state_file: Filename of storage_state (in browser_sessions/)
        stealth_mode: Stealth mode to use
    
    Returns:
        Screenshot capture result
    """
    storage_state_path = f"browser_sessions/{storage_state_file}"
    
    result = await screenshot_service.capture_with_auth_state(
        url=url,
        storage_state_path=storage_state_path,
        stealth_mode=stealth_mode
    )
    
    return result
```

---

## 🎨 Frontend Integration

Add UI buttons in `frontend/src/App.tsx`:

```typescript
// Add state
const [extractingCookies, setExtractingCookies] = useState(false);

// Add function
const handleExtractCookies = async () => {
  setExtractingCookies(true);
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/extract-cookies', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        domains: null,  // Extract all cookies
        browser: 'chrome'
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      alert(`✅ Cookies extracted successfully!\n\nSaved to: ${result.filepath}`);
    } else {
      alert(`❌ Failed to extract cookies: ${result.error}`);
    }
  } catch (error) {
    alert(`❌ Error: ${error}`);
  } finally {
    setExtractingCookies(false);
  }
};

// Add button in UI
<button
  onClick={handleExtractCookies}
  disabled={extractingCookies}
  className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
>
  {extractingCookies ? '⏳ Extracting...' : '🍪 Import Browser Cookies'}
</button>
```

---

## 🚀 Usage Workflow

### **Step 1: Login to Sites in Your Browser**

1. Open Chrome
2. Login to Zomato, Swiggy, etc.
3. Make sure you're logged in

### **Step 2: Extract Cookies**

Click **"🍪 Import Browser Cookies"** button in the UI

OR run Python script:

```python
from cookie_extractor import CookieExtractor

extractor = CookieExtractor()
extractor.extract_and_save(browser="chrome")
```

### **Step 3: Capture Screenshots**

Now all your captures will use the authenticated session!

```python
# Capture with auth
result = await screenshot_service.capture_with_auth_state(
    url="https://www.zomato.com/dashboard",
    storage_state_path="browser_sessions/auth_state.json"
)
```

---

## 🎯 Benefits

✅ **No manual login** for each URL  
✅ **Reuse sessions** across all 56 URLs  
✅ **One-click cookie import**  
✅ **Works with all browsers** (Chrome, Firefox, Edge, etc.)  
✅ **Secure** - Cookies stored locally  
✅ **Fast** - Rust-based extraction  

---

## 🔒 Security Notes

1. **Storage state files contain sensitive data** - Don't commit to git
2. Add to `.gitignore`:
   ```
   browser_sessions/
   *.json
   ```
3. **Cookies expire** - Re-extract periodically
4. **Use HTTPS** - Secure cookies require secure connections

---

## 📝 Next Steps

1. ✅ Install rookiepy: `pip install rookiepy`
2. ✅ Create `backend/cookie_extractor.py`
3. ✅ Update `backend/screenshot_service.py`
4. ✅ Add API endpoints in `backend/main.py`
5. ✅ Add UI button in frontend
6. ✅ Test with your 56 URLs

---

**Ready to implement? Let me know if you need help!** 🚀

