# 📡 Network Events - Practical Examples

**Date**: 2025-11-08  
**Status**: ✅ DOCUMENTED WITH EXAMPLES

---

## 🎯 Real-World Example: Tekion Page Load

When capturing `https://preprodapp.tekioncloud.com/accounting/accountingChain/list`, here's what happens:

---

## 📊 Event #1: Main Page Document

```python
{
    'event': 'request',
    'type': 'document',
    'method': 'GET',
    'url': 'https://preprodapp.tekioncloud.com/accounting/accountingChain/list',
    'timestamp': 0.001,
    'headers': {
        'User-Agent': 'Mozilla/5.0...',
        'Accept': 'text/html,application/xhtml+xml...',
        'Accept-Language': 'en-US,en;q=0.9'
    }
}
```

**What it means**: Browser is requesting the main HTML page

---

## 📊 Event #2: Document Response

```python
{
    'event': 'response',
    'type': 'document',
    'status': 200,
    'statusText': 'OK',
    'url': 'https://preprodapp.tekioncloud.com/accounting/accountingChain/list',
    'timestamp': 0.234,
    'headers': {
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Length': '45678',
        'Server': 'nginx/1.21.0'
    }
}
```

**What it means**: Server successfully returned the HTML (200 = success)

---

## 📊 Event #3: API Call - Fetch Data

```python
{
    'event': 'request',
    'type': 'xhr',
    'method': 'GET',
    'url': 'https://preprodapp.tekioncloud.com/api/v1/accounting/chains?limit=50&offset=0',
    'timestamp': 0.456,
    'headers': {}
}
```

**What it means**: JavaScript is making an API call to fetch accounting data

---

## 📊 Event #4: API Response - Data Received

```python
{
    'event': 'response',
    'type': 'xhr',
    'status': 200,
    'statusText': 'OK',
    'url': 'https://preprodapp.tekioncloud.com/api/v1/accounting/chains?limit=50&offset=0',
    'timestamp': 0.678,
    'headers': {
        'Content-Type': 'application/json',
        'Content-Length': '12345'
    }
}
```

**What it means**: API successfully returned data (200 = success)

---

## 📊 Event #5: Failed Request - Timeout

```python
{
    'event': 'failed',
    'type': 'xhr',
    'method': 'GET',
    'url': 'https://preprodapp.tekioncloud.com/api/v1/analytics/report',
    'timestamp': 5.234,
    'failure': 'net::ERR_TIMED_OUT'
}
```

**What it means**: API call timed out (took too long to respond)

---

## 📊 Event #6: Failed Request - 404 Not Found

```python
{
    'event': 'failed',
    'type': 'xhr',
    'method': 'GET',
    'url': 'https://preprodapp.tekioncloud.com/api/v1/old-endpoint',
    'timestamp': 1.234,
    'failure': 'net::ERR_HTTP_RESPONSE_CODE_FAILURE'
}
```

**What it means**: API endpoint doesn't exist (404 = not found)

---

## 📊 Event #7: WebSocket Connection

```python
{
    'event': 'request',
    'type': 'websocket',
    'method': 'GET',
    'url': 'wss://preprodapp.tekioncloud.com/ws/notifications',
    'timestamp': 2.345,
    'headers': {}
}
```

**What it means**: Browser is establishing a WebSocket connection for real-time updates

---

## 📊 Event #8: Finished Event

```python
{
    'event': 'finished',
    'type': 'xhr',
    'url': 'https://preprodapp.tekioncloud.com/api/v1/accounting/chains',
    'timestamp': 0.789
}
```

**What it means**: API call is completely finished (all data received)

---

## 🔍 How to Interpret the 314 Events

### Document Requests (2)
```
1. GET https://preprodapp.tekioncloud.com/accounting/accountingChain/list
   → Response: 200 OK (main page HTML)

2. GET https://preprodapp.tekioncloud.com/accounting/accountingChain/list
   → Response: 200 OK (possible redirect or reload)
```

### XHR/Fetch Requests (102)
```
1. GET /api/v1/accounting/chains → 200 OK
2. GET /api/v1/accounting/chain/123 → 200 OK
3. GET /api/v1/users → 200 OK
4. POST /api/v1/analytics/track → 200 OK
5. GET /api/v1/config → 200 OK
... (97 more API calls)
```

### Failed Requests (32)
```
1. GET /api/v1/old-endpoint → 404 Not Found
2. GET /api/v1/analytics/report → Timeout
3. GET /api/v1/deprecated-api → 410 Gone
4. POST /api/v1/sync → 500 Server Error
... (28 more failed requests)
```

---

## 📈 What This Tells Us

### ✅ Good Signs
- Document request succeeded (200)
- Most API calls succeeded (200)
- Page loaded completely

### ⚠️ Warning Signs
- 32 failed requests (might indicate issues)
- Some API calls timing out
- Possible missing data

### 🔴 Critical Issues
- If document request failed (404, 500)
- If all API calls failed
- If page never finished loading

---

## 🎯 Use Cases

### 1. **Debugging**
"Why is the page showing no data?"
→ Check if API calls succeeded or failed

### 2. **Performance**
"Why is the page slow?"
→ Check request timing and identify slow endpoints

### 3. **Quality Checks**
"Is the page working correctly?"
→ Verify all required API calls succeeded

### 4. **Monitoring**
"Are there any errors?"
→ Check for failed requests and error codes

---

## 🚀 Next Steps

1. **Export Network Events** - Save to JSON for analysis
2. **Filter Events** - Show only failed requests
3. **Analyze Timing** - Find slowest API calls
4. **Generate Report** - Create network activity summary

---

## ✨ Summary

**Network Events** capture every HTTP/WebSocket request during page load

**Types**:
- `request` - Request starts
- `response` - Response received
- `failed` - Request failed
- `finished` - Request complete

**Example**: Tekion page load captured 314 events:
- 2 document requests
- 102 API calls
- 32 failed requests

**Use**: Debug, optimize, and verify page functionality

