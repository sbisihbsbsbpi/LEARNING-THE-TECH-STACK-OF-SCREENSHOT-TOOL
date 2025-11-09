# 🍪 Complete Cookie & Token Management Libraries Research 2024-2025

**Research Date:** November 3, 2025  
**Purpose:** Find the best cookie/token libraries for Screenshot Tool to import browser cookies for authenticated sessions

---

## 📋 Table of Contents

1. [Python Libraries - Browser Cookie Extraction](#python-browser-cookie-extraction)
2. [Python Libraries - Cookie Management](#python-cookie-management)
3. [Python Libraries - Token/JWT Management](#python-token-jwt-management)
4. [JavaScript/TypeScript Libraries](#javascript-typescript-libraries)
5. [Browser Extensions](#browser-extensions)
6. [Playwright Native Solutions](#playwright-native-solutions)
7. [Recommendations for Your Use Case](#recommendations)

---

## 🐍 Python Libraries - Browser Cookie Extraction

### **1. rookiepy** ⭐ **RECOMMENDED**

**GitHub:** https://github.com/thewh1teagle/rookie  
**PyPI:** https://pypi.org/project/rookiepy/

**Why It's Best:**
- ✅ **Written in Rust** - Extremely fast and secure
- ✅ **Supports ALL major browsers** (Chrome, Firefox, Edge, Safari, Opera, Brave, etc.)
- ✅ **Cross-platform** (Windows, macOS, Linux)
- ✅ **Actively maintained** (2024)
- ✅ **Handles encrypted cookies** automatically
- ✅ **Simple API**

**Installation:**
```bash
pip install rookiepy
```

**Usage:**
```python
import rookiepy

# Extract cookies from Chrome
cookies = rookiepy.chrome()

# Extract cookies from specific domains
cookies = rookiepy.chrome(["google.com", "zomato.com"])

# Extract from Firefox
cookies = rookiepy.firefox()

# Extract from all browsers
cookies = rookiepy.any()

# Use with Playwright
for cookie in cookies:
    print(f"{cookie['name']}: {cookie['value']}")
```

**Pros:**
- Fastest performance (Rust-based)
- Most comprehensive browser support
- Handles Chrome's encrypted cookies on all platforms
- Active development

**Cons:**
- Relatively new (but well-tested)

---

### **2. browser-cookie3**

**GitHub:** https://github.com/borisbabic/browser_cookie3  
**PyPI:** https://pypi.org/project/browser-cookie3/

**Why Consider It:**
- ✅ Popular and well-established
- ✅ Supports Chrome, Firefox, Edge, Opera, Brave
- ✅ Cross-platform

**Installation:**
```bash
pip install browser-cookie3
```

**Usage:**
```python
import browser_cookie3

# Load cookies from Chrome
cookies = browser_cookie3.chrome(domain_name='.google.com')

# Load from all browsers
cookies = browser_cookie3.load()

# Use with requests
import requests
response = requests.get('https://example.com', cookies=cookies)
```

**Pros:**
- Well-tested and stable
- Good documentation
- Works with `requests` library

**Cons:**
- Slower than rookiepy (pure Python)
- Some issues with Chrome's latest encryption on macOS
- Less actively maintained

---

### **3. pycookiecheat**

**GitHub:** https://github.com/n8henrie/pycookiecheat  
**PyPI:** https://pypi.org/project/pycookiecheat/

**Why Consider It:**
- ✅ Specifically designed for Chrome
- ✅ Handles Chrome's encryption well

**Installation:**
```bash
pip install pycookiecheat
```

**Usage:**
```python
from pycookiecheat import chrome_cookies
import requests

url = 'https://example.com'
cookies = chrome_cookies(url)
response = requests.get(url, cookies=cookies)
```

**Pros:**
- Good for Chrome-specific use cases
- Handles encryption

**Cons:**
- **Chrome only** (no Firefox, Edge, etc.)
- Less flexible than rookiepy or browser-cookie3

---

## 🐍 Python Libraries - Cookie Management

### **4. http.cookiejar** (Built-in)

**Documentation:** https://docs.python.org/3/library/http.cookiejar.html

**Why Use It:**
- ✅ **Built into Python** - No installation needed
- ✅ Standard library for HTTP cookie handling
- ✅ Works with `urllib` and `requests`

**Usage:**
```python
import http.cookiejar
import urllib.request

# Create cookie jar
cookie_jar = http.cookiejar.CookieJar()

# Use with urllib
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cookie_jar)
)
response = opener.open('https://example.com')

# Save cookies to file
import http.cookiejar as cookielib
cookie_jar = cookielib.MozillaCookieJar('cookies.txt')
cookie_jar.save()

# Load cookies from file
cookie_jar.load()
```

**Pros:**
- No dependencies
- Standard Python library
- Persistent cookie storage

**Cons:**
- More verbose API
- Doesn't extract from browsers

---

### **5. requests.Session** (Built-in with requests)

**Documentation:** https://requests.readthedocs.io/

**Why Use It:**
- ✅ Automatic cookie handling
- ✅ Session persistence
- ✅ Simple API

**Usage:**
```python
import requests

# Create session (automatically handles cookies)
session = requests.Session()

# Cookies persist across requests
session.get('https://example.com/login')
session.post('https://example.com/api', data={'key': 'value'})

# Access cookies
print(session.cookies.get_dict())

# Save cookies
import pickle
with open('cookies.pkl', 'wb') as f:
    pickle.dump(session.cookies, f)

# Load cookies
with open('cookies.pkl', 'rb') as f:
    session.cookies.update(pickle.load(f))
```

**Pros:**
- Automatic cookie management
- Session persistence
- Simple and intuitive

**Cons:**
- Doesn't extract from browsers
- Requires manual save/load

---

## 🐍 Python Libraries - Token/JWT Management

### **6. PyJWT** ⭐ **RECOMMENDED FOR JWT**

**GitHub:** https://github.com/jpadilla/pyjwt  
**PyPI:** https://pypi.org/project/PyJWT/  
**Docs:** https://pyjwt.readthedocs.io/

**Why It's Best:**
- ✅ **Most popular** JWT library for Python
- ✅ Simple and clean API
- ✅ Actively maintained
- ✅ Supports all JWT algorithms
- ✅ Well-documented

**Installation:**
```bash
pip install PyJWT
```

**Usage:**
```python
import jwt
import datetime

# Encode JWT
payload = {
    'user_id': 123,
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}
token = jwt.encode(payload, 'secret_key', algorithm='HS256')

# Decode JWT
decoded = jwt.decode(token, 'secret_key', algorithms=['HS256'])
print(decoded['user_id'])  # 123

# Verify expiration
try:
    jwt.decode(token, 'secret_key', algorithms=['HS256'])
except jwt.ExpiredSignatureError:
    print('Token expired')
```

**Pros:**
- Industry standard
- Simple API
- Excellent documentation
- Active community

**Cons:**
- None for basic JWT use cases

---

### **7. python-jose**

**GitHub:** https://github.com/mpdavis/python-jose  
**PyPI:** https://pypi.org/project/python-jose/

**Why Consider It:**
- ✅ Supports JWS, JWE, JWK
- ✅ More features than PyJWT

**Installation:**
```bash
pip install python-jose
```

**Usage:**
```python
from jose import jwt

token = jwt.encode({'key': 'value'}, 'secret', algorithm='HS256')
decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
```

**Pros:**
- More comprehensive (JWS, JWE, JWK)
- Good for complex use cases

**Cons:**
- More complex API
- Less actively maintained than PyJWT

---

### **8. Authlib** ⭐ **RECOMMENDED FOR OAUTH**

**GitHub:** https://github.com/lepture/authlib  
**PyPI:** https://pypi.org/project/Authlib/  
**Docs:** https://docs.authlib.org/

**Why It's Best for OAuth:**
- ✅ **Complete OAuth 1.0/2.0 implementation**
- ✅ Supports OpenID Connect
- ✅ JWT, JWS, JWE, JWK support
- ✅ Works with FastAPI, Flask, Django
- ✅ Actively maintained

**Installation:**
```bash
pip install authlib
```

**Usage:**
```python
from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI

app = FastAPI()
oauth = OAuth()

# Configure OAuth provider
oauth.register(
    name='google',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
```

**Pros:**
- Most comprehensive auth library
- Excellent FastAPI integration
- Handles OAuth, JWT, everything

**Cons:**
- Overkill for simple JWT use cases

---

### **9. itsdangerous** ⭐ **RECOMMENDED FOR SECURE COOKIES**

**GitHub:** https://github.com/pallets/itsdangerous  
**PyPI:** https://pypi.org/project/itsdangerous/  
**Docs:** https://itsdangerous.palletsprojects.com/

**Why It's Best for Cookie Signing:**
- ✅ **Cryptographically sign data**
- ✅ Used by Flask for session cookies
- ✅ Prevents cookie tampering
- ✅ Simple API

**Installation:**
```bash
pip install itsdangerous
```

**Usage:**
```python
from itsdangerous import TimedSerializer

# Create serializer
serializer = TimedSerializer('secret_key')

# Sign data
signed_data = serializer.dumps({'user_id': 123})

# Verify and load (with expiration check)
try:
    data = serializer.loads(signed_data, max_age=3600)  # 1 hour
    print(data['user_id'])
except:
    print('Invalid or expired signature')
```

**Pros:**
- Perfect for secure cookie signing
- Prevents tampering
- Time-based expiration
- Used in production by Flask

**Cons:**
- Not for JWT (use PyJWT for that)

---

## 🌐 JavaScript/TypeScript Libraries

### **10. js-cookie** ⭐ **RECOMMENDED FOR VANILLA JS**

**GitHub:** https://github.com/js-cookie/js-cookie  
**NPM:** https://www.npmjs.com/package/js-cookie

**Installation:**
```bash
npm install js-cookie
```

**Usage:**
```typescript
import Cookies from 'js-cookie';

// Set cookie
Cookies.set('name', 'value', { expires: 7 });

// Get cookie
const value = Cookies.get('name');

// Delete cookie
Cookies.remove('name');

// Set with options
Cookies.set('token', 'abc123', {
  expires: 7,
  secure: true,
  sameSite: 'strict'
});
```

**Pros:**
- Simple and lightweight
- TypeScript support
- Most popular (20k+ stars)

**Cons:**
- Browser-only (not for Node.js)

---

### **11. universal-cookie** ⭐ **RECOMMENDED FOR REACT**

**GitHub:** https://github.com/reactivestack/cookies  
**NPM:** https://www.npmjs.com/package/universal-cookie

**Installation:**
```bash
npm install universal-cookie
npm install react-cookie  # For React hooks
```

**Usage:**
```typescript
import { useCookies } from 'react-cookie';

function MyComponent() {
  const [cookies, setCookie, removeCookie] = useCookies(['token']);

  const handleLogin = () => {
    setCookie('token', 'abc123', { path: '/', maxAge: 3600 });
  };

  return <div>Token: {cookies.token}</div>;
}
```

**Pros:**
- Works in browser AND Node.js
- React hooks support
- SSR compatible

**Cons:**
- Slightly larger than js-cookie

---

### **12. nookies** (For Next.js)

**GitHub:** https://github.com/maticzav/nookies  
**NPM:** https://www.npmjs.com/package/nookies

**Installation:**
```bash
npm install nookies
```

**Usage:**
```typescript
import { parseCookies, setCookie, destroyCookie } from 'nookies';

// Get cookies
const cookies = parseCookies(ctx);

// Set cookie
setCookie(ctx, 'token', 'value', {
  maxAge: 30 * 24 * 60 * 60,
  path: '/',
});

// Delete cookie
destroyCookie(ctx, 'token');
```

**Pros:**
- Perfect for Next.js
- SSR support
- Simple API

**Cons:**
- Next.js specific

---

## 🔌 Browser Extensions

### **13. Cookie-Editor** ⭐ **RECOMMENDED**

**Website:** https://cookie-editor.com/  
**Chrome:** https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm  
**Firefox:** Available on Firefox Add-ons

**Why It's Best:**
- ✅ **Open source**
- ✅ Available for Chrome, Firefox, Safari, Edge
- ✅ Export/import cookies (JSON, Netscape format)
- ✅ Clean UI
- ✅ **Privacy-focused** (no tracking)
- ✅ Actively maintained

**Features:**
- Create, edit, delete cookies
- Export cookies as JSON
- Import cookies from JSON
- Search and filter cookies
- Bulk operations

**Export Format (JSON):**
```json
[
  {
    "name": "session_id",
    "value": "abc123",
    "domain": ".example.com",
    "path": "/",
    "expires": 1735689600,
    "httpOnly": true,
    "secure": true,
    "sameSite": "Lax"
  }
]
```

---

### **14. EditThisCookie** (Alternative)

**Chrome:** https://chromewebstore.google.com/detail/editthiscookie/

**Note:** The legitimate version was temporarily removed from Chrome Web Store in Dec 2024 due to a malicious copycat. Use Cookie-Editor instead for safety.

---

### **15. J2TEAM Cookies**

**Chrome:** https://chromewebstore.google.com/detail/j2team-cookies/okpidcojinmlaakglciglbpcpajaibco

**Features:**
- Export/import cookies
- Share accounts without passwords
- Simple UI

---

## 🎭 Playwright Native Solutions

### **16. Playwright Storage State** ⭐ **RECOMMENDED FOR YOUR USE CASE**

**Docs:** https://playwright.dev/docs/auth

**Why It's Perfect:**
- ✅ **Built into Playwright** - No extra libraries needed
- ✅ Saves cookies + localStorage + IndexedDB
- ✅ Cross-browser compatible
- ✅ Simple API

**Usage:**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    
    # Login manually
    page.goto('https://example.com/login')
    page.fill('#username', 'user')
    page.fill('#password', 'pass')
    page.click('#submit')
    
    # Save storage state (cookies + localStorage)
    storage = context.storage_state(path='auth.json')
    
    browser.close()

# Later, reuse the auth state
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(storage_state='auth.json')
    page = context.new_page()
    
    # Already logged in!
    page.goto('https://example.com/dashboard')
```

**Storage State Format:**
```json
{
  "cookies": [
    {
      "name": "session",
      "value": "abc123",
      "domain": ".example.com",
      "path": "/",
      "expires": 1735689600,
      "httpOnly": true,
      "secure": true,
      "sameSite": "Lax"
    }
  ],
  "origins": [
    {
      "origin": "https://example.com",
      "localStorage": [
        {
          "name": "token",
          "value": "xyz789"
        }
      ]
    }
  ]
}
```

**Pros:**
- Native Playwright solution
- Saves everything (cookies + localStorage + IndexedDB)
- No extra dependencies
- Cross-browser

**Cons:**
- Doesn't extract from your real browser (need to login once in Playwright)

---

## 🎯 Recommendations for Your Use Case

### **Your Requirement:**
> Import cookies from logged-in browser to reuse sessions across headless captures for 56 URLs without manual login each time

---

### **🏆 Best Solution: Hybrid Approach**

**Combine:**
1. **rookiepy** - Extract cookies from your real browser
2. **Playwright storage_state** - Use cookies in headless captures

---

### **Implementation Plan:**

#### **Step 1: Extract Cookies from Browser**

```python
import rookiepy
import json

def extract_browser_cookies(domains=None):
    """Extract cookies from Chrome browser"""
    if domains:
        cookies = rookiepy.chrome(domains)
    else:
        cookies = rookiepy.chrome()
    
    return cookies

# Extract cookies for specific domains
domains = ["zomato.com", "swiggy.com", "example.com"]
cookies = extract_browser_cookies(domains)

# Save to file
with open('browser_cookies.json', 'w') as f:
    json.dump(cookies, f, indent=2)
```

#### **Step 2: Convert to Playwright Format**

```python
def convert_to_playwright_format(rookiepy_cookies):
    """Convert rookiepy cookies to Playwright storage_state format"""
    playwright_cookies = []
    
    for cookie in rookiepy_cookies:
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
    
    storage_state = {
        "cookies": playwright_cookies,
        "origins": []
    }
    
    return storage_state

# Convert and save
storage_state = convert_to_playwright_format(cookies)
with open('auth_state.json', 'w') as f:
    json.dump(storage_state, f, indent=2)
```

#### **Step 3: Use in Playwright**

```python
from playwright.sync_api import sync_playwright

def capture_with_auth(url, storage_state_path='auth_state.json'):
    """Capture screenshot with authenticated session"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Load auth state
        context = browser.new_context(storage_state=storage_state_path)
        page = context.new_page()
        
        # Navigate (already authenticated!)
        page.goto(url)
        page.screenshot(path='screenshot.png')
        
        browser.close()

# Capture all 56 URLs without logging in each time
urls = ["https://example.com/page1", "https://example.com/page2", ...]
for url in urls:
    capture_with_auth(url)
```

---

### **Alternative: Browser Extension + Manual Export**

If you prefer a UI-based approach:

1. Install **Cookie-Editor** extension
2. Login to your sites
3. Export cookies as JSON
4. Convert to Playwright format
5. Use in headless captures

---

## 📊 Comparison Table

| Library | Type | Best For | Platform | Active | Stars |
|---------|------|----------|----------|--------|-------|
| **rookiepy** | Browser Extract | Extracting cookies from browsers | All | ✅ Yes | 500+ |
| browser-cookie3 | Browser Extract | Python cookie extraction | All | ⚠️ Slow | 600+ |
| pycookiecheat | Browser Extract | Chrome-only extraction | All | ⚠️ Slow | 500+ |
| PyJWT | JWT | Token management | All | ✅ Yes | 5k+ |
| Authlib | OAuth/JWT | Complete auth solution | All | ✅ Yes | 4k+ |
| itsdangerous | Cookie Sign | Secure cookie signing | All | ✅ Yes | 2.8k+ |
| js-cookie | JS Cookie | Browser cookie management | Browser | ✅ Yes | 21k+ |
| universal-cookie | JS Cookie | React cookie management | All | ✅ Yes | 1.5k+ |
| Cookie-Editor | Extension | Manual cookie export | Browser | ✅ Yes | N/A |
| Playwright storage_state | Native | Playwright auth | All | ✅ Yes | Built-in |

---

## 🚀 Final Recommendation

### **For Your Screenshot Tool:**

**Use this stack:**

1. **rookiepy** - Extract cookies from your logged-in Chrome browser
2. **Playwright storage_state** - Use cookies in headless captures
3. **PyJWT** (optional) - If you need to handle JWT tokens
4. **Cookie-Editor** (backup) - Manual export if rookiepy fails

**Why:**
- ✅ Fully automated cookie extraction
- ✅ No manual export needed
- ✅ Works with all 56 URLs
- ✅ Fast and reliable
- ✅ Cross-platform

**Installation:**
```bash
pip install rookiepy
# Playwright already installed
```

---

## 📝 Next Steps

1. Install rookiepy
2. Create cookie extraction function
3. Create Playwright format converter
4. Integrate into your screenshot service
5. Test with your 56 URLs

---

**Need help implementing? Let me know!** 🎯

