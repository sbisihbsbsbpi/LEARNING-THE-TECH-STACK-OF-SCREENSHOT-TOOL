# 🔗 cURL Export Feature - Complete Guide

**Date**: 2025-11-08  
**Status**: ✅ FULLY IMPLEMENTED  
**Feature**: Export network events as cURL commands

---

## 🎯 What Is This?

When you capture a screenshot, the tool captures **314 network events** (API calls made by the page). This feature converts those events into **cURL commands** that you can:

- ✅ Copy and paste into terminal
- ✅ Run manually to test APIs
- ✅ Save to shell script
- ✅ Share with team members
- ✅ Use for debugging and testing

---

## 🚀 Quick Start (30 seconds)

### 1. Capture Screenshot
```bash
curl -X POST http://localhost:8000/api/screenshots/capture \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "use_real_browser": true}'
```

### 2. See cURL Commands in Logs
```
🔗 cURL commands (102 API calls):
   1. curl -X GET -H 'Authorization: Bearer ...' 'https://api.example.com/...'
   2. curl -X POST -H 'Content-Type: application/json' -d '{"key":"value"}' 'https://api.example.com/...'
   ... and 100 more
```

### 3. Run All Commands
```bash
bash screenshots/curl_commands.sh
```

### 4. Run Individual Command
```bash
curl -X GET -H 'Authorization: Bearer token123' 'https://api.example.com/data'
```

---

## 📊 How It Works

```
1. Capture Screenshot
   ↓
2. Browser Loads Page
   ↓
3. Network Events Captured (314 events)
   ↓
4. Convert to cURL Commands (102 API calls)
   ↓
5. Export Options:
   - Print to logs
   - API endpoint
   - Shell script
   ↓
6. Use cURL Commands:
   - Test APIs
   - Debug issues
   - Measure performance
   - Share with team
```

---

## 🎯 Use Cases

### 1. Test APIs Manually
```bash
# Copy cURL command and run in terminal
curl -X GET -H 'Authorization: Bearer token123' 'https://api.example.com/data'
```

### 2. Debug API Issues
```bash
# Run with verbose output to see headers and response
curl -v -X GET -H 'Authorization: Bearer token123' 'https://api.example.com/data'
```

### 3. Measure Performance
```bash
# Time how long the request takes
curl -w "Time: %{time_total}s\n" -X GET 'https://api.example.com/data'
```

### 4. Share with Team
```bash
# Send curl_commands.sh to team members
# They can run the same API calls
bash curl_commands.sh
```

### 5. Automate Testing
```bash
# Use in CI/CD pipeline
bash screenshots/curl_commands.sh
```

---

## 📋 Common cURL Commands

### Get Data
```bash
curl -X GET 'https://api.example.com/data'
```

### Create Record
```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{"name":"John"}' \
  'https://api.example.com/users'
```

### Update Record
```bash
curl -X PUT \
  -H 'Content-Type: application/json' \
  -d '{"name":"Jane"}' \
  'https://api.example.com/users/1'
```

### Delete Record
```bash
curl -X DELETE 'https://api.example.com/users/1'
```

### With Authentication
```bash
curl -X GET \
  -H 'Authorization: Bearer token123' \
  'https://api.example.com/data'
```

---

## 🔧 Useful cURL Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-X` | HTTP method | `curl -X POST` |
| `-H` | Add header | `curl -H 'Authorization: Bearer token'` |
| `-d` | POST data | `curl -d '{"key":"value"}'` |
| `-v` | Verbose | `curl -v` |
| `-i` | Include headers | `curl -i` |
| `-o` | Save to file | `curl -o response.json` |
| `-w` | Show timing | `curl -w "Time: %{time_total}s"` |

---

## 📚 Documentation

### Quick References
- **[CURL_QUICK_START.md](CURL_QUICK_START.md)** - 30-second overview
- **[CURL_COMMANDS_GUIDE.md](CURL_COMMANDS_GUIDE.md)** - Practical guide
- **[CURL_DOCUMENTATION_INDEX.md](CURL_DOCUMENTATION_INDEX.md)** - Documentation index

### Detailed Guides
- **[NETWORK_EVENTS_TO_CURL.md](NETWORK_EVENTS_TO_CURL.md)** - Export guide
- **[NETWORK_TO_CURL_WORKFLOW.md](NETWORK_TO_CURL_WORKFLOW.md)** - Complete workflow
- **[CURL_EXPORT_IMPLEMENTATION.md](CURL_EXPORT_IMPLEMENTATION.md)** - Implementation details

### Summaries
- **[CURL_FEATURE_SUMMARY.md](CURL_FEATURE_SUMMARY.md)** - Feature summary
- **[CODE_CHANGES_SUMMARY.md](CODE_CHANGES_SUMMARY.md)** - Code changes

---

## 🔐 Security Tips

### ✅ DO
- Use environment variables for tokens
- Use HTTPS (not HTTP)
- Keep scripts private
- Mask sensitive data in logs

### ❌ DON'T
- Hardcode tokens in commands
- Use HTTP (use HTTPS)
- Commit scripts with tokens to git
- Share tokens publicly

---

## 🆘 Troubleshooting

### "Connection refused"
```bash
# Check if server is running
curl http://localhost:8000/health
```

### "401 Unauthorized"
```bash
# Check authentication token
curl -H "Authorization: Bearer $AUTH_TOKEN" 'https://api.example.com/data'
```

### "404 Not Found"
```bash
# Check URL
curl -v 'https://api.example.com/data'
```

---

## 📊 Example: Complete Workflow

### Step 1: Capture Screenshot
```bash
curl -X POST http://localhost:8000/api/screenshots/capture \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://preprodapp.tekioncloud.com/accounting/accountingChain/list",
    "use_real_browser": true
  }'
```

### Step 2: See Network Events in Logs
```
📡 Network events captured during page load: 314
   🌐 Network activity during page load (314 events):
      📄 Document requests: 2
      🔄 XHR/Fetch requests: 102
      ❌ Failed requests: 32
      🔗 cURL commands (102 API calls):
         1. curl -X GET -H 'Authorization: Bearer ...' 'https://api.example.com/...'
         2. curl -X POST -H 'Content-Type: application/json' -d '{"key":"value"}' 'https://api.example.com/...'
         ... and 100 more
```

### Step 3: Find Shell Script
```bash
ls -la screenshots/curl_commands.sh
```

### Step 4: Run All Commands
```bash
bash screenshots/curl_commands.sh > api_responses.txt
```

### Step 5: Check Responses
```bash
cat api_responses.txt
```

---

## ✨ Features

| Feature | Status |
|---------|--------|
| Capture network events | ✅ |
| Capture headers | ✅ |
| Capture POST data | ✅ |
| Generate cURL commands | ✅ |
| Print to logs | ✅ |
| API endpoint | ✅ |
| Shell script export | ✅ |
| Escape special characters | ✅ |
| Filter requests | ✅ |

---

## 🎉 Summary

**Feature**: Export network events as cURL commands

**What You Can Do**:
- ✅ Test APIs manually
- ✅ Debug issues
- ✅ Measure performance
- ✅ Share with team
- ✅ Automate testing

**Status**: ✅ Fully implemented and ready to use

**Next Steps**: Start using the feature!

---

## 📞 Need Help?

1. **Quick Start**: Read [CURL_QUICK_START.md](CURL_QUICK_START.md)
2. **Learn cURL**: Read [CURL_COMMANDS_GUIDE.md](CURL_COMMANDS_GUIDE.md)
3. **Understand Export**: Read [NETWORK_EVENTS_TO_CURL.md](NETWORK_EVENTS_TO_CURL.md)
4. **See Workflow**: Read [NETWORK_TO_CURL_WORKFLOW.md](NETWORK_TO_CURL_WORKFLOW.md)
5. **Implementation**: Read [CURL_EXPORT_IMPLEMENTATION.md](CURL_EXPORT_IMPLEMENTATION.md)

---

**Happy testing! 🚀**


