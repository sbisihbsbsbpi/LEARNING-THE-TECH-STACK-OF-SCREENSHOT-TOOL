# 📡 Network Events - Quick Reference

**Date**: 2025-11-08  
**Status**: ✅ QUICK REFERENCE GUIDE

---

## 🎯 What Are Network Events?

**Network Events** = All HTTP/WebSocket requests and responses that happen when a web page loads

---

## 📊 4 Types of Network Events

| Event Type | When It Fires | What It Captures |
|-----------|---------------|-----------------|
| **request** | When request starts | URL, method, headers, timing |
| **response** | When response received | Status code, headers, timing |
| **failed** | When request fails | Error reason, URL, timing |
| **finished** | When request completes | URL, timing |

---

## 🔍 Request Types Tracked

| Type | Example | What It Is |
|------|---------|-----------|
| **document** | Main HTML page | The web page itself |
| **xhr** | API call | XMLHttpRequest (AJAX) |
| **fetch** | API call | Fetch API call |
| **websocket** | Real-time connection | WebSocket for live updates |

---

## 📈 Tekion Example: 314 Events

```
📄 Document Requests: 2
   - Main page HTML load
   - Possible redirect/reload

🔄 XHR/Fetch Requests: 102
   - API calls to fetch data
   - GraphQL queries
   - REST endpoints

❌ Failed Requests: 32
   - Timeouts
   - 404 errors
   - 500 errors
   - Connection errors
```

---

## 📊 Event Data Structure

### Request Event
```python
{
    'event': 'request',
    'type': 'xhr',                    # document, xhr, fetch, websocket
    'method': 'GET',                  # HTTP method
    'url': 'https://api.example.com/data',
    'timestamp': 0.234,               # Seconds since page load started
    'headers': {...}                  # Request headers (document only)
}
```

### Response Event
```python
{
    'event': 'response',
    'type': 'xhr',
    'status': 200,                    # HTTP status code
    'statusText': 'OK',
    'url': 'https://api.example.com/data',
    'timestamp': 0.456,
    'headers': {...}                  # Response headers (document only)
}
```

### Failed Event
```python
{
    'event': 'failed',
    'type': 'xhr',
    'method': 'GET',
    'url': 'https://api.example.com/data',
    'timestamp': 0.789,
    'failure': 'net::ERR_TIMED_OUT'   # Error reason
}
```

### Finished Event
```python
{
    'event': 'finished',
    'type': 'xhr',
    'url': 'https://api.example.com/data',
    'timestamp': 1.234
}
```

---

## 🎯 Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| **200** | Success | API returned data |
| **301/302** | Redirect | Page moved to new URL |
| **400** | Bad Request | Invalid parameters |
| **401** | Unauthorized | Need authentication |
| **403** | Forbidden | Access denied |
| **404** | Not Found | Endpoint doesn't exist |
| **500** | Server Error | Server crashed |
| **503** | Service Unavailable | Server overloaded |

---

## 🔴 Common Network Errors

| Error | Meaning | Cause |
|-------|---------|-------|
| **ERR_TIMED_OUT** | Timeout | Request took too long |
| **ERR_CONNECTION_REFUSED** | Connection refused | Server not responding |
| **ERR_NAME_NOT_RESOLVED** | DNS error | Domain not found |
| **ERR_NETWORK_CHANGED** | Network changed | WiFi/connection switched |
| **ERR_BLOCKED_BY_CLIENT** | Blocked | Browser blocked request |

---

## 📊 How to Count Events

```python
# Count by event type
requests = sum(1 for e in events if e['event'] == 'request')
responses = sum(1 for e in events if e['event'] == 'response')
failed = sum(1 for e in events if e['event'] == 'failed')
finished = sum(1 for e in events if e['event'] == 'finished')

# Count by resource type
documents = sum(1 for e in events if e['type'] == 'document')
xhr_fetch = sum(1 for e in events if e['type'] in ['xhr', 'fetch'])
websockets = sum(1 for e in events if e['type'] == 'websocket')

# Count by status
success = sum(1 for e in events if e.get('status') == 200)
errors = sum(1 for e in events if e.get('status', 0) >= 400)
```

---

## 🎯 What to Look For

### ✅ Good Signs
- Document request: 200 OK
- Most API calls: 200 OK
- Few or no failed requests
- Reasonable request timing

### ⚠️ Warning Signs
- Many failed requests (32+)
- Slow API responses (>5 seconds)
- 404 or 500 errors
- Timeouts

### 🔴 Critical Issues
- Document request failed
- All API calls failed
- Page never finished loading
- Connection refused

---

## 🚀 Use Cases

| Use Case | What to Check |
|----------|---------------|
| **Debugging** | Failed requests, error messages |
| **Performance** | Request timing, slow endpoints |
| **Quality** | Success rate, required APIs |
| **Monitoring** | Error patterns, availability |
| **Stealth** | Bot detection, authentication |

---

## 📝 Implementation

**File**: `screenshot-app/backend/screenshot_service.py`

**Method**: `_create_network_event_handlers()`
- Lines 155-216
- Creates handlers for all 4 event types
- Returns dict with handlers and event list

**Usage**: `capture_segmented()` method
- Lines 2046-2082
- Attaches listeners BEFORE page load
- Prints network activity summary

---

## ✨ Summary

**Network Events** = All HTTP/WebSocket activity during page load

**4 Event Types**: request, response, failed, finished

**4 Resource Types**: document, xhr, fetch, websocket

**Example**: Tekion page = 314 events (2 documents, 102 API calls, 32 failed)

**Status**: ✅ Fully implemented and capturing events

---

## 📚 Related Documents

- `NETWORK_EVENTS_EXPLAINED.md` - Detailed explanation
- `NETWORK_EVENTS_EXAMPLES.md` - Real-world examples
- `NETWORK_EVENTS_FULLY_FIXED.md` - Implementation details

