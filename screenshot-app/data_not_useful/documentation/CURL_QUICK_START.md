# 🚀 cURL Quick Start

**Date**: 2025-11-08  
**Status**: ✅ READY TO USE

---

## ⚡ 30-Second Overview

**What**: Convert network events to cURL commands  
**Why**: Test, debug, and share API calls  
**How**: Capture screenshot → Get cURL commands → Run in terminal

---

## 🎯 Quick Start

### 1. Capture Screenshot
```bash
curl -X POST http://localhost:8000/api/screenshots/capture \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "use_real_browser": true
  }'
```

### 2. See cURL Commands in Logs
```
🔗 cURL commands (102 API calls):
   1. curl -X GET -H 'Authorization: Bearer ...' 'https://api.example.com/...'
   2. curl -X POST -H 'Content-Type: application/json' -d '{"key":"value"}' 'https://api.example.com/...'
   ... and 100 more
```

### 3. Find Shell Script
```bash
ls -la screenshots/curl_commands.sh
```

### 4. Run All Commands
```bash
bash screenshots/curl_commands.sh
```

### 5. Run Individual Command
```bash
curl -X GET -H 'Authorization: Bearer token123' 'https://api.example.com/data'
```

---

## 📋 Common Commands

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

### Save Response to File
```bash
curl -X GET 'https://api.example.com/data' > response.json
```

### Show Timing
```bash
curl -w "Time: %{time_total}s\n" -X GET 'https://api.example.com/data'
```

### Verbose Output
```bash
curl -v -X GET 'https://api.example.com/data'
```

---

## 🔧 Useful Options

| Option | Purpose |
|--------|---------|
| `-X` | HTTP method (GET, POST, PUT, DELETE) |
| `-H` | Add header |
| `-d` | POST data |
| `-v` | Verbose (show headers) |
| `-i` | Include response headers |
| `-o` | Save to file |
| `-w` | Show timing |
| `-b` | Add cookies |

---

## 💡 Tips

### 1. Use Environment Variables
```bash
export AUTH_TOKEN="your_token_here"
curl -H "Authorization: Bearer $AUTH_TOKEN" 'https://api.example.com/data'
```

### 2. Run Multiple Commands
```bash
bash screenshots/curl_commands.sh
```

### 3. Debug Issues
```bash
curl -v -X GET 'https://api.example.com/data'
```

### 4. Measure Performance
```bash
curl -w "Time: %{time_total}s\n" -X GET 'https://api.example.com/data'
```

### 5. Save Responses
```bash
curl -X GET 'https://api.example.com/data' > response.json
cat response.json
```

---

## 🎯 Use Cases

| Use Case | Command |
|----------|---------|
| Test API | `curl -X GET 'https://api.example.com/data'` |
| Debug | `curl -v -X GET 'https://api.example.com/data'` |
| Performance | `curl -w "Time: %{time_total}s\n" -X GET 'https://api.example.com/data'` |
| Save Response | `curl -X GET 'https://api.example.com/data' > response.json` |
| Run All | `bash screenshots/curl_commands.sh` |

---

## 🔐 Security

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

## 📊 Example Workflow

```
1. Capture screenshot
   ↓
2. See cURL commands in logs
   ↓
3. Copy command to terminal
   ↓
4. Run: curl -X GET ...
   ↓
5. See response
   ↓
6. Debug if needed
```

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

## 📚 More Info

- `NETWORK_EVENTS_TO_CURL.md` - Full documentation
- `CURL_COMMANDS_GUIDE.md` - Detailed guide
- `NETWORK_TO_CURL_WORKFLOW.md` - Complete workflow

---

## ✨ Summary

**cURL** = Powerful tool to test APIs from terminal

**Quick Start**:
1. Capture screenshot
2. Get cURL commands
3. Run in terminal
4. Test/debug/share

**Status**: ✅ Ready to use


