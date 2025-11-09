# 📡 Network Events Explained

**Date**: 2025-11-08  
**Status**: ✅ FULLY DOCUMENTED

---

## 🎯 What Are Network Events?

Network events are **all the HTTP/WebSocket requests and responses** that happen when a web page loads. They track:
- Page loads
- API calls (XHR/Fetch)
- WebSocket connections
- Failed requests
- Request timing

---

## 📊 Types of Network Events Captured

### 1. **Request Events** (`event: 'request'`)
Fired when a network request **starts**

**Captured for**:
- `document` - Main page HTML
- `xhr` - XMLHttpRequest (AJAX calls)
- `fetch` - Fetch API calls
- `websocket` - WebSocket connections

**Data captured**:
```python
{
    'event': 'request',
    'type': 'xhr',                    # Type of request
    'method': 'GET',                  # HTTP method
    'url': 'https://api.example.com/data',
    'timestamp': 0.234,               # Seconds since page load started
    'headers': {...}                  # Request headers (for document only)
}
```

### 2. **Response Events** (`event: 'response'`)
Fired when a network request **receives a response**

**Data captured**:
```python
{
    'event': 'response',
    'type': 'xhr',
    'status': 200,                    # HTTP status code
    'statusText': 'OK',
    'url': 'https://api.example.com/data',
    'timestamp': 0.456,
    'headers': {...}                  # Response headers (for document only)
}
```

### 3. **Failed Events** (`event: 'failed'`)
Fired when a network request **fails** (network error, timeout, etc.)

**Data captured**:
```python
{
    'event': 'failed',
    'type': 'xhr',
    'method': 'GET',
    'url': 'https://api.example.com/data',
    'timestamp': 0.789,
    'failure': 'net::ERR_CONNECTION_REFUSED'  # Error reason
}
```

### 4. **Finished Events** (`event: 'finished'`)
Fired when a network request is **completely finished**

**Data captured**:
```python
{
    'event': 'finished',
    'type': 'xhr',
    'url': 'https://api.example.com/data',
    'timestamp': 1.234
}
```

---

## 📈 Example: Tekion Page Load (314 Events)

When loading `https://preprodapp.tekioncloud.com/accounting/accountingChain/list`:

```
📡 Network events captured during page load: 314
   🌐 Network activity during page load (314 events):
      📄 Document requests: 2
      🔄 XHR/Fetch requests: 102
      ❌ Failed requests: 32
```

### Breakdown:

**Document Requests (2)**:
- Initial page HTML load
- Possible redirect or reload

**XHR/Fetch Requests (102)**:
- API calls to fetch data
- GraphQL queries
- REST API endpoints
- Asset loading (CSS, JS, images)

**Failed Requests (32)**:
- Network timeouts
- 404 errors (not found)
- 500 errors (server errors)
- CORS errors
- Connection refused

---

## 🔍 Why We Track Network Events

### 1. **Debugging**
- See what API calls the page makes
- Identify failed requests
- Check request timing

### 2. **Performance Analysis**
- Measure how long requests take
- Identify slow API endpoints
- Optimize page load time

### 3. **Quality Checks**
- Verify all required API calls succeeded
- Detect missing data
- Identify broken integrations

### 4. **Stealth Detection**
- Monitor for bot detection requests
- Track authentication flows
- Verify session handling

---

## 📊 Event Timeline Example

```
T=0ms:    Page starts loading
T=10ms:   request event - Main HTML document
T=50ms:   response event - HTML received (200 OK)
T=100ms:  request event - API call #1 (GET /api/data)
T=150ms:  request event - API call #2 (GET /api/users)
T=200ms:  response event - API call #1 received (200 OK)
T=250ms:  response event - API call #2 received (200 OK)
T=300ms:  request event - API call #3 (GET /api/config)
T=350ms:  failed event - API call #3 failed (timeout)
T=400ms:  finished event - All requests complete
```

---

## 🎯 How We Use This Data

### Current Implementation:
```python
# Count events by type
xhr_count = sum(1 for e in network_events 
                if e.get('type') in ['xhr', 'fetch'] 
                and e.get('event') == 'request')

doc_count = sum(1 for e in network_events 
                if e.get('type') == 'document' 
                and e.get('event') == 'request')

failed_count = sum(1 for e in network_events 
                   if e.get('event') == 'failed')

# Print summary
print(f"📄 Document requests: {doc_count}")
print(f"🔄 XHR/Fetch requests: {xhr_count}")
print(f"❌ Failed requests: {failed_count}")
```

---

## 🚀 Future Enhancements

1. **Export Network Events**
   - Save to JSON file
   - Include in screenshot metadata

2. **Network Filtering**
   - Filter by status code
   - Filter by URL pattern
   - Filter by request type

3. **Network Metrics**
   - Average request time
   - Slowest requests
   - Failed request analysis

4. **Network Validation**
   - Verify required API calls succeeded
   - Check for expected status codes
   - Validate response data

---

## ✨ Summary

**Network Events** = All HTTP/WebSocket activity during page load

**Types**:
- `request` - Request starts
- `response` - Response received
- `failed` - Request failed
- `finished` - Request complete

**Data Captured**:
- URL, method, status code
- Request/response headers
- Timing information
- Error details

**Use Cases**:
- Debugging
- Performance analysis
- Quality checks
- Stealth detection

**Current Status**: ✅ Fully implemented and capturing 314+ events per page load

