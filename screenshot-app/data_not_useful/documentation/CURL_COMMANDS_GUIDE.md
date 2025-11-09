# 🔗 cURL Commands - Practical Guide

**Date**: 2025-11-08  
**Status**: ✅ READY TO USE

---

## 🎯 What Can You Do With cURL Commands?

### 1. **Test APIs Manually**
```bash
# Copy the cURL command and run it
curl -X GET -H 'Authorization: Bearer token123' 'https://api.example.com/data'

# See the response
# {"data": [...], "status": "success"}
```

### 2. **Debug API Issues**
```bash
# Run with verbose output to see headers and response
curl -v -X GET -H 'Authorization: Bearer token123' 'https://api.example.com/data'

# Output shows:
# > GET /api/data HTTP/1.1
# > Authorization: Bearer token123
# < HTTP/1.1 200 OK
# < Content-Type: application/json
```

### 3. **Test Different Scenarios**
```bash
# Test with different parameters
curl -X GET 'https://api.example.com/data?limit=10'
curl -X GET 'https://api.example.com/data?limit=50'
curl -X GET 'https://api.example.com/data?limit=100'
```

### 4. **Measure Performance**
```bash
# Time how long the request takes
curl -w "Time: %{time_total}s\n" -X GET 'https://api.example.com/data'

# Output: Time: 0.234s
```

### 5. **Save Response to File**
```bash
# Save API response to file
curl -X GET 'https://api.example.com/data' > response.json

# View the file
cat response.json
```

### 6. **Chain Multiple Requests**
```bash
# Run multiple API calls in sequence
curl -X GET 'https://api.example.com/users' > users.json
curl -X GET 'https://api.example.com/data' > data.json
curl -X GET 'https://api.example.com/config' > config.json
```

---

## 📋 Common cURL Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-X` | HTTP method | `curl -X POST` |
| `-H` | Add header | `curl -H 'Authorization: Bearer token'` |
| `-d` | POST data | `curl -d '{"key":"value"}'` |
| `-v` | Verbose (show headers) | `curl -v` |
| `-i` | Include response headers | `curl -i` |
| `-o` | Save to file | `curl -o response.json` |
| `-w` | Show timing | `curl -w "Time: %{time_total}s"` |
| `-b` | Add cookies | `curl -b 'session=abc123'` |
| `-A` | User agent | `curl -A 'Mozilla/5.0'` |

---

## 🎯 Real-World Examples

### Example 1: Get Data from API
```bash
# Simple GET request
curl -X GET \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIs...' \
  'https://api.example.com/accounting/chains'

# Response:
# {
#   "data": [
#     {"id": 1, "name": "Chain A"},
#     {"id": 2, "name": "Chain B"}
#   ],
#   "total": 2
# }
```

### Example 2: Create New Record
```bash
# POST request with data
curl -X POST \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIs...' \
  -H 'Content-Type: application/json' \
  -d '{"name":"New Chain","type":"accounting"}' \
  'https://api.example.com/accounting/chains'

# Response:
# {
#   "id": 3,
#   "name": "New Chain",
#   "type": "accounting",
#   "created_at": "2025-11-08T12:34:56Z"
# }
```

### Example 3: Update Record
```bash
# PUT request to update
curl -X PUT \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIs...' \
  -H 'Content-Type: application/json' \
  -d '{"name":"Updated Chain"}' \
  'https://api.example.com/accounting/chains/3'

# Response:
# {
#   "id": 3,
#   "name": "Updated Chain",
#   "type": "accounting"
# }
```

### Example 4: Delete Record
```bash
# DELETE request
curl -X DELETE \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIs...' \
  'https://api.example.com/accounting/chains/3'

# Response:
# {"status": "deleted"}
```

### Example 5: Test with Different Parameters
```bash
# Get first 10 records
curl -X GET 'https://api.example.com/data?limit=10'

# Get records 10-20
curl -X GET 'https://api.example.com/data?limit=10&offset=10'

# Get sorted by name
curl -X GET 'https://api.example.com/data?sort=name'

# Get filtered by type
curl -X GET 'https://api.example.com/data?type=accounting'
```

---

## 🚀 Advanced Usage

### Run Multiple Requests in Sequence
```bash
#!/bin/bash
# Save as run_apis.sh

# Get users
echo "Getting users..."
curl -X GET 'https://api.example.com/users' > users.json

# Get data
echo "Getting data..."
curl -X GET 'https://api.example.com/data' > data.json

# Get config
echo "Getting config..."
curl -X GET 'https://api.example.com/config' > config.json

echo "Done!"
```

**Run it**:
```bash
bash run_apis.sh
```

### Performance Testing
```bash
#!/bin/bash
# Test API 10 times and measure performance

for i in {1..10}; do
  echo "Request $i:"
  curl -w "Time: %{time_total}s\n" \
    -X GET 'https://api.example.com/data'
  sleep 1  # Wait 1 second between requests
done
```

### Error Handling
```bash
#!/bin/bash
# Run API and check for errors

response=$(curl -X GET 'https://api.example.com/data')

if echo "$response" | grep -q "error"; then
  echo "❌ API returned error:"
  echo "$response"
else
  echo "✅ API call successful"
  echo "$response"
fi
```

---

## 🔐 Security Tips

### 1. **Use Environment Variables for Tokens**
```bash
# Don't hardcode tokens
# ❌ BAD:
curl -H 'Authorization: Bearer abc123def456' 'https://api.example.com/data'

# ✅ GOOD:
curl -H "Authorization: Bearer $AUTH_TOKEN" 'https://api.example.com/data'

# Set token before running:
export AUTH_TOKEN="abc123def456"
```

### 2. **Keep Scripts Private**
```bash
# Don't commit scripts with tokens to git
# Add to .gitignore:
echo "curl_commands.sh" >> .gitignore
```

### 3. **Use HTTPS**
```bash
# Always use HTTPS, not HTTP
# ❌ BAD:
curl 'http://api.example.com/data'

# ✅ GOOD:
curl 'https://api.example.com/data'
```

### 4. **Mask Sensitive Data**
```bash
# When sharing logs, mask tokens
# ❌ BAD:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ✅ GOOD:
Authorization: Bearer [REDACTED]
```

---

## 📊 Troubleshooting

### Issue: "Connection refused"
```bash
# API server is not running
# Solution: Check if server is running
curl http://localhost:8000/health
```

### Issue: "401 Unauthorized"
```bash
# Authentication token is missing or invalid
# Solution: Check token
curl -H "Authorization: Bearer $AUTH_TOKEN" 'https://api.example.com/data'
```

### Issue: "404 Not Found"
```bash
# Endpoint doesn't exist
# Solution: Check URL
curl -v 'https://api.example.com/data'  # Use -v to see full request
```

### Issue: "CORS error"
```bash
# Browser CORS issue (not applicable to cURL)
# cURL doesn't enforce CORS, so this shouldn't happen
# If it does, check API server configuration
```

---

## ✨ Summary

**cURL Commands** = Powerful tool to test and debug APIs

**Use Cases**:
- Test APIs manually
- Debug issues
- Measure performance
- Automate testing
- Share with team

**Key Options**:
- `-X` - HTTP method
- `-H` - Headers
- `-d` - POST data
- `-v` - Verbose
- `-w` - Timing

**Security**:
- Use environment variables for tokens
- Keep scripts private
- Always use HTTPS
- Mask sensitive data

**Status**: ✅ Ready to use

---

## 📚 Related Documents

- `NETWORK_EVENTS_TO_CURL.md` - How to export network events as cURL
- `NETWORK_EVENTS_EXPLAINED.md` - Network events overview

