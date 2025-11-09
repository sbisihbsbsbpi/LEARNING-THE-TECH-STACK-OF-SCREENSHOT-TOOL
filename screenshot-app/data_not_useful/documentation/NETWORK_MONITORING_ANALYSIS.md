# 🌐 Network Monitoring Analysis - What's Happening

**Date**: 2025-11-08  
**Status**: IMPLEMENTED & WORKING  
**Location**: `screenshot-app/backend/screenshot_service.py` (lines 2371-2566)

---

## 📊 What Network Monitoring Does

The network monitoring system tracks **ALL network activity** during page capture:

### ✅ Tracked Events

1. **Document Requests** (Page navigations)
   - Initial page load
   - Redirects (301, 302, 307, 308)
   - Page reloads
   - Status codes (200, 404, 500, etc.)

2. **XHR/Fetch Requests** (AJAX calls)
   - API calls
   - Data fetches
   - Status codes
   - Request/response timing

3. **WebSocket Connections**
   - Real-time connections
   - Live data streams

4. **Failed Requests**
   - Network errors
   - Timeout errors
   - Connection refused
   - DNS failures

---

## 🔍 How It Works

### Step 1: Setup Event Listeners (Lines 2375-2424)

```python
# Create empty list to store all network events
network_events = []
start_time = asyncio.get_event_loop().time()

# Define 4 callback functions:
def log_request(request):          # When request STARTS
def log_response(response):        # When response RECEIVED
def log_request_failed(request):   # When request FAILS
def log_request_finished(request): # When request FINISHES

# Attach listeners to page
page.on('request', log_request)
page.on('response', log_response)
page.on('requestfailed', log_request_failed)
page.on('requestfinished', log_request_finished)
```

### Step 2: Monitor Page Reloads (Lines 2426-2486)

```python
# Wait up to 15 seconds for page to stabilize
# Check for URL changes (redirects/reloads)
# Wait for readyState = 'complete'
# Detect multiple reloads
```

### Step 3: Print Network Summary (Lines 2488-2566)

```python
# Remove listeners (stop tracking)
page.remove_listener('request', log_request)
page.remove_listener('response', log_response)
page.remove_listener('requestfailed', log_request_failed)
page.remove_listener('requestfinished', log_request_finished)

# Print summary:
# - Total events count
# - Document requests count
# - XHR/Fetch requests count
# - WebSocket connections
# - Failed requests
# - Detailed list of each type
```

---

## 📋 Output Format

### Example Output

```
🔄 Monitoring page for reloads/redirects...
📍 Initial URL: https://preprodapp.tekioncloud.com/accounting/autoPostingSettings
✅ Page stable for 5 seconds
✅ No page reloads detected

🌐 Network activity during page load (47 events):
   📄 Document requests: 1
   🔄 XHR/Fetch requests: 12
   ❌ Failed requests: 2

   📋 Document navigations (chronological):
      1. [0.1s] GET https://preprodapp.tekioncloud.com/accounting/autoPostingSettings
      2. [0.3s] ← 200 OK https://preprodapp.tekioncloud.com/accounting/autoPostingSettings

   📋 XHR/Fetch activity (last 10):
      1. [1.2s] → POST https://preprodapp.tekioncloud.com/api/auth/verify
      2. [1.4s] ← 200 https://preprodapp.tekioncloud.com/api/auth/verify
      3. [1.5s] → GET https://preprodapp.tekioncloud.com/api/settings
      4. [1.7s] ← 200 https://preprodapp.tekioncloud.com/api/settings

   ❌ Failed requests:
      1. [2.1s] https://preprodapp.tekioncloud.com/api/old-endpoint
         Error: ERR_HTTP_RESPONSE_CODE_FAILURE (404)
      2. [2.3s] https://preprodapp.tekioncloud.com/api/timeout
         Error: ERR_TIMED_OUT

   🔀 Redirects detected:
      1. [0.2s] 302 https://preprodapp.tekioncloud.com/login
         → https://preprodapp.tekioncloud.com/accounting/autoPostingSettings
```

---

## 🎯 When Network Monitoring Runs

### ✅ RUNS in these scenarios:

1. **CDP Active Tab Mode** (Real Browser Mode)
   - When `use_real_browser=True`
   - Calls `_capture_segments_from_page()`
   - Monitors network during segmented capture

### ❌ DOES NOT RUN in these scenarios:

1. **Normal Headless Mode**
   - When `use_real_browser=False`
   - Uses different code path in `capture_segmented()`
   - No network monitoring (lines 2241-2350)

2. **Single Screenshot Mode**
   - `capture()` method
   - No network monitoring

---

## 🔴 Current Issues

### Issue 1: Network Monitoring Only in CDP Mode
**Problem**: Network monitoring only works when using Active Tab Mode (CDP)  
**Impact**: Can't see network activity in normal headless mode  
**Solution**: Add network monitoring to normal headless capture too

### Issue 2: Listeners Attached AFTER Page Load
**Problem**: Network listeners attached after page is already loaded  
**Impact**: May miss some early network events  
**Solution**: Attach listeners BEFORE page load starts

### Issue 3: No Network Monitoring in Regular Segmented Capture
**Problem**: Lines 2241-2350 (normal segmented capture) have NO network monitoring  
**Impact**: Can't debug network issues in normal mode  
**Solution**: Add network monitoring to normal capture path

---

## 📍 Code Location

### File: `screenshot-app/backend/screenshot_service.py`

**Function**: `_capture_segments_from_page()` (lines 2351-2850)

**Network Monitoring Section**: Lines 2371-2566

**Key Components**:
- Event listeners setup: Lines 2375-2424
- Page reload detection: Lines 2426-2486
- Network summary printing: Lines 2488-2566

---

## 🔧 How to Enable Network Monitoring

### For CDP Mode (Already Enabled)
```python
# This automatically enables network monitoring:
screenshot_paths = await screenshot_service.capture_segmented(
    url="https://example.com",
    use_real_browser=True  # ← Enables CDP mode with network monitoring
)
```

### For Normal Headless Mode (NOT Currently Enabled)
```python
# Currently NO network monitoring:
screenshot_paths = await screenshot_service.capture_segmented(
    url="https://example.com",
    use_real_browser=False  # ← No network monitoring
)
```

---

## 📊 Data Collected

### For Each Request Event:
- **event**: 'request', 'response', 'failed', or 'finished'
- **type**: 'xhr', 'fetch', 'document', 'websocket'
- **method**: 'GET', 'POST', etc.
- **url**: Full URL
- **timestamp**: Seconds since monitoring started
- **status**: HTTP status code (200, 404, 500, etc.)
- **statusText**: Status text ('OK', 'Not Found', etc.)
- **failure**: Error message (if failed)
- **headers**: Request/response headers (for document requests)

---

## 🎯 Next Steps

### To Improve Network Monitoring:

1. **Add to Normal Headless Mode**
   - Copy network monitoring code to normal capture path
   - Attach listeners before page load
   - Print network summary after capture

2. **Add to Single Screenshot Mode**
   - Add network monitoring to `capture()` method
   - Track network activity during single screenshot

3. **Add Network Filtering**
   - Filter by status code (errors only)
   - Filter by resource type
   - Filter by URL pattern

4. **Add Network Metrics**
   - Total request count
   - Total response time
   - Slowest requests
   - Failed request percentage

5. **Add Network Logging to File**
   - Save network events to JSON
   - Include in debug output
   - Help with troubleshooting

---

## ✨ Summary

**Network monitoring is IMPLEMENTED and WORKING** in CDP Active Tab Mode. It tracks all network activity (documents, XHR/Fetch, WebSockets, failures) and prints a detailed summary to logs. However, it's only enabled in CDP mode and should be extended to normal headless mode for better debugging.

