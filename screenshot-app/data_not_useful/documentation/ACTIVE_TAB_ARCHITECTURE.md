# 🏗️ Active Tab Mode - Architecture

**How Active Tab Mode works under the hood**

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Screenshot Tool (Frontend)                   │
│                                                                   │
│  ┌──────────────┐                                                │
│  │   Settings   │  ← User enables "Real Browser" mode            │
│  └──────────────┘                                                │
│                                                                   │
│  ┌──────────────┐                                                │
│  │  Main Tab    │  ← User enters URLs and clicks "Capture"       │
│  └──────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP POST /api/capture
                              │ { use_real_browser: true }
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (main.py)                     │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         ScreenshotService (screenshot_service.py)        │   │
│  │                                                           │   │
│  │  if use_real_browser:                                    │   │
│  │    ┌─────────────────────────────────────────────────┐  │   │
│  │    │  1. _connect_to_chrome_cdp()                    │  │   │
│  │    │     - Connect via CDP on port 9222              │  │   │
│  │    └─────────────────────────────────────────────────┘  │   │
│  │                      │                                   │   │
│  │                      ▼                                   │   │
│  │    ┌─────────────────────────────────────────────────┐  │   │
│  │    │  2. _get_active_tab()                           │  │   │
│  │    │     - Get first tab from first context          │  │   │
│  │    └─────────────────────────────────────────────────┘  │   │
│  │                      │                                   │   │
│  │                      ▼                                   │   │
│  │    ┌─────────────────────────────────────────────────┐  │   │
│  │    │  3. page.goto(url)                              │  │   │
│  │    │     - Load URL in active tab                    │  │   │
│  │    └─────────────────────────────────────────────────┘  │   │
│  │                      │                                   │   │
│  │                      ▼                                   │   │
│  │    ┌─────────────────────────────────────────────────┐  │   │
│  │    │  4. page.screenshot()                           │  │   │
│  │    │     - Capture screenshot                        │  │   │
│  │    └─────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ CDP Connection
                              │ (Chrome DevTools Protocol)
                              │ ws://localhost:9222
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Google Chrome Browser                         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Browser Window                        │   │
│  │                                                           │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Active Tab                                        │  │   │
│  │  │  ┌──────────────────────────────────────────────┐  │  │   │
│  │  │  │                                              │  │  │   │
│  │  │  │  URL loads here (visible to user)           │  │  │   │
│  │  │  │                                              │  │  │   │
│  │  │  │  Screenshot captured from this tab          │  │  │   │
│  │  │  │                                              │  │  │   │
│  │  │  └──────────────────────────────────────────────┘  │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  │  Other tabs (not used)                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Launched with: --remote-debugging-port=9222                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Sequence Diagram

```
User          Frontend       Backend        Chrome (CDP)
 │                │              │                │
 │  1. Launch Chrome with debugging               │
 │  ./launch-chrome-debug.sh                      │
 │────────────────────────────────────────────────▶
 │                │              │                │
 │                │              │                │ Chrome starts
 │                │              │                │ with port 9222
 │                │              │                │
 │  2. Enable "Real Browser" mode                 │
 │────────────────▶              │                │
 │                │              │                │
 │  3. Click "Capture"           │                │
 │────────────────▶              │                │
 │                │              │                │
 │                │  POST /api/capture            │
 │                │  use_real_browser=true        │
 │                ├──────────────▶                │
 │                │              │                │
 │                │              │  connect_over_cdp()
 │                │              ├────────────────▶
 │                │              │                │
 │                │              │◀────────────────┤
 │                │              │  Connected!    │
 │                │              │                │
 │                │              │  get_active_tab()
 │                │              ├────────────────▶
 │                │              │                │
 │                │              │◀────────────────┤
 │                │              │  Active tab    │
 │                │              │                │
 │                │              │  goto(url)     │
 │                │              ├────────────────▶
 │                │              │                │
 │                │              │                │ URL loads
 │                │              │                │ (visible)
 │                │              │                │
 │                │              │◀────────────────┤
 │                │              │  Page loaded   │
 │                │              │                │
 │                │              │  screenshot()  │
 │                │              ├────────────────▶
 │                │              │                │
 │                │              │◀────────────────┤
 │                │              │  Screenshot    │
 │                │              │                │
 │                │◀──────────────┤                │
 │                │  Screenshot path               │
 │                │              │                │
 │◀────────────────              │                │
 │  Screenshot saved!            │                │
 │                │              │                │
```

---

## 🔌 CDP Connection Details

### **Chrome Launch**

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$HOME/Library/Application Support/Google/Chrome"
```

**What this does:**
- Starts Chrome with DevTools Protocol enabled
- Listens on `ws://localhost:9222` for connections
- Uses your normal Chrome profile (keeps cookies, history, etc.)

### **Playwright Connection**

```python
# Connect to Chrome via CDP
browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

# Get browser contexts (windows)
contexts = browser.contexts  # List of all open windows

# Get pages (tabs) from first context
pages = contexts[0].pages  # List of all tabs in first window

# Use first page as active tab
active_page = pages[0]
```

### **Page Control**

```python
# Navigate to URL
await active_page.goto(url, wait_until='domcontentloaded', timeout=30000)

# Take screenshot
await active_page.screenshot(path=filepath, full_page=True)
```

---

## 🔐 Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                        Local Machine                         │
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  Screenshot  │         │    Chrome    │                  │
│  │     Tool     │◀───────▶│   Browser    │                  │
│  └──────────────┘         └──────────────┘                  │
│         │                        │                           │
│         │                        │                           │
│         │  localhost:9222        │                           │
│         │  (CDP WebSocket)       │                           │
│         │                        │                           │
│         └────────────────────────┘                           │
│                                                               │
│  ❌ NOT accessible from outside                              │
│  ❌ NOT exposed to internet                                  │
│  ✅ Only local connections allowed                           │
└─────────────────────────────────────────────────────────────┘
```

**Security Features:**
- ✅ CDP only listens on `localhost` (127.0.0.1)
- ✅ No remote connections allowed
- ✅ No data sent outside local machine
- ✅ User maintains full browser control
- ✅ Can disconnect at any time

---

## 📦 Component Breakdown

### **1. Frontend (React)**
- Settings toggle for "Real Browser" mode
- Sends `use_real_browser: true` to backend
- Displays progress and results

### **2. Backend (FastAPI)**
- Receives capture request
- Checks `use_real_browser` flag
- Routes to appropriate capture method

### **3. ScreenshotService**
- `_connect_to_chrome_cdp()`: Establishes CDP connection
- `_get_active_tab()`: Finds active tab
- `capture()`: Loads URL and captures screenshot
- `capture_segmented()`: Captures multiple segments
- `close()`: Disconnects from Chrome

### **4. Chrome Browser**
- Runs with `--remote-debugging-port=9222`
- Exposes CDP WebSocket endpoint
- Accepts commands from Playwright
- Executes navigation and screenshot commands

---

## 🔄 Data Flow

```
User Input (URLs)
    │
    ▼
Frontend (React)
    │
    ▼
HTTP POST /api/capture
    │
    ▼
Backend (FastAPI)
    │
    ▼
ScreenshotService
    │
    ├─▶ Connect to Chrome (CDP)
    │
    ├─▶ Get Active Tab
    │
    ├─▶ Load URL in Tab
    │
    ├─▶ Capture Screenshot
    │
    └─▶ Save to File
    │
    ▼
Return Screenshot Path
    │
    ▼
Frontend Displays Result
    │
    ▼
User Sees Screenshot
```

---

## 🎯 Key Differences from Standard Mode

| Component | Standard Mode | Active Tab Mode |
|-----------|--------------|-----------------|
| **Browser Launch** | `chromium.launch()` | Already running |
| **Connection** | Direct | CDP WebSocket |
| **Tab Creation** | `context.new_page()` | Use existing tab |
| **Visibility** | Optional | Always visible |
| **Cleanup** | Close browser | Disconnect only |

---

## 🚀 Performance Characteristics

### **Advantages**
- ✅ Visual feedback (see what's happening)
- ✅ Manual interaction possible
- ✅ Uses existing browser state
- ✅ No browser startup time

### **Trade-offs**
- ⚠️ Slower than headless (visible rendering)
- ⚠️ Single tab (no parallelization)
- ⚠️ Requires manual Chrome launch
- ⚠️ User must not interfere

---

## 📚 References

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Playwright CDP Connection](https://playwright.dev/docs/api/class-browsertype#browser-type-connect-over-cdp)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

