# 🔍 Cookie Analysis Guide

**How to inspect and understand your extracted cookies**

---

## 🎯 Quick Start

### **View Cookie Summary**
```bash
cd screenshot-app/backend
python3 analyze_cookies.py
```

**Shows:**
- Total cookies
- Unique domains
- Security statistics (Secure, HttpOnly, Session)
- Top 10 domains by cookie count
- Authentication cookies

---

## 📊 What You'll See

### **Example Output:**

```
📊 Statistics:
   Total Cookies: 326
   Unique Domains: 101
   Secure Cookies: 200 (61.3%)
   HttpOnly Cookies: 0 (0.0%)
   Session Cookies: 1 (0.3%)
   Auth Cookies: 77

🌐 Top 10 Domains by Cookie Count:
    1. .youtube.com                             ( 19 cookies)
    2. .google.com                              ( 18 cookies)
    3. .slack.com                               ( 16 cookies)
    4. .lovable.dev                             ( 16 cookies)
    5. .bobkinghyundai.com                      ( 12 cookies)

🔑 Authentication Cookies (77):
   🔒   cjUser                         | .slack.com                     | Expires: 2026-10-16
   🔒   sessionid                      | .rkdms.com                     | Expires: 2026-09-16
   🔒   __Secure-ROLLOUT_TOKEN         | .youtube.com                   | Expires: 2026-03-15
```

---

## 🔍 Search & Filter Commands

### **1. Filter by Domain**

Show only cookies from a specific domain:

```bash
python3 analyze_cookies.py --domain zomato
python3 analyze_cookies.py --domain google
python3 analyze_cookies.py --domain slack
```

### **2. Show Only Auth Cookies**

Show only authentication-related cookies:

```bash
python3 analyze_cookies.py --auth
```

**Auth keywords detected:**
- token, session, auth, sid, jsession
- login, user, jwt, bearer
- csrf, xsrf

### **3. Search Cookies**

Search by name, domain, or value:

```bash
python3 analyze_cookies.py --search token
python3 analyze_cookies.py --search session
python3 analyze_cookies.py --search zomato
```

### **4. Show All Cookies in Detail**

View every cookie with full details:

```bash
python3 analyze_cookies.py --all
```

**Shows for each cookie:**
- Name
- Domain
- Path
- Value (truncated if long)
- Expiry date
- Security flags (Secure, HttpOnly, SameSite)

### **5. Export to CSV**

Export cookies to a CSV file for Excel/Google Sheets:

```bash
# Export all cookies
python3 analyze_cookies.py --export csv

# Export only Google cookies
python3 analyze_cookies.py --domain google --export csv

# Export only auth cookies
python3 analyze_cookies.py --auth --export csv
```

**CSV includes:**
- name, value, domain, path
- expires (timestamp), expires_readable (human-readable)
- secure, httpOnly, sameSite
- is_auth (true/false)

---

## 🍪 Understanding Cookie Fields

### **Name**
The cookie's identifier (e.g., `sessionid`, `token`, `_ga`)

### **Value**
The cookie's data (often encrypted or encoded)

### **Domain**
Which website(s) can access this cookie
- `.google.com` = all Google subdomains
- `zomato.com` = only zomato.com

### **Path**
Which URL paths can access this cookie
- `/` = entire site
- `/api` = only /api/* paths

### **Expires**
When the cookie expires
- Timestamp (e.g., `1792604564`)
- `Session` = expires when browser closes
- `Invalid` = malformed timestamp

### **Secure** 🔒
- ✅ = Only sent over HTTPS (encrypted)
- ❌ = Can be sent over HTTP (insecure)

### **HttpOnly** 🚫
- ✅ = JavaScript cannot access (more secure)
- ❌ = JavaScript can access

### **SameSite**
Cross-site request protection:
- `Strict` = Never sent cross-site (most secure)
- `Lax` = Sent on top-level navigation (balanced)
- `None` = Always sent (least secure)

---

## 🔑 Identifying Important Cookies

### **Authentication Cookies**

Look for these patterns in cookie names:

| Pattern | Example | Purpose |
|---------|---------|---------|
| `session*` | `sessionid`, `session_token` | Session management |
| `*token*` | `auth_token`, `csrf_token` | Authentication tokens |
| `*auth*` | `auth_user`, `authenticated` | Auth status |
| `*sid*` | `sid`, `jsessionid` | Session IDs |
| `*user*` | `user_id`, `username` | User identification |
| `*jwt*` | `jwt_token` | JSON Web Tokens |
| `*csrf*` | `csrftoken`, `xsrf` | CSRF protection |

### **Tracking Cookies**

| Pattern | Example | Purpose |
|---------|---------|---------|
| `_ga*` | `_ga`, `_gid` | Google Analytics |
| `_fbp` | `_fbp` | Facebook Pixel |
| `*utm*` | `utm_source` | Campaign tracking |

### **Preference Cookies**

| Pattern | Example | Purpose |
|---------|---------|---------|
| `lang*` | `language`, `locale` | Language preference |
| `theme*` | `theme`, `dark_mode` | UI preferences |
| `tz*` | `timezone` | Timezone |

---

## 💡 Common Use Cases

### **Use Case 1: Find cookies for a specific website**

```bash
# You want to capture screenshots of zomato.com
# First, check what zomato cookies you have:
python3 analyze_cookies.py --domain zomato
```

### **Use Case 2: Check if you're logged in**

```bash
# Look for auth cookies for your target site:
python3 analyze_cookies.py --domain yoursite --auth
```

If you see auth cookies with future expiry dates, you're logged in!

### **Use Case 3: Debug login issues**

```bash
# Check all cookies for the problematic domain:
python3 analyze_cookies.py --domain problematic-site.com --all
```

Look for:
- Expired cookies (might need to re-extract)
- Missing auth cookies (might need to log in again)
- Secure cookies without HTTPS (won't work)

### **Use Case 4: Export for analysis**

```bash
# Export to CSV and open in Excel/Google Sheets:
python3 analyze_cookies.py --export csv
open cookies_all.csv  # macOS
```

### **Use Case 5: Find specific token**

```bash
# Search for a specific token or session:
python3 analyze_cookies.py --search "your-token-name"
```

---

## 📁 File Locations

### **Playwright Cookies**
```
screenshot-app/backend/browser_sessions/playwright_storage_state.json
```

### **Camoufox Cookies**
```
screenshot-app/backend/browser_sessions/camoufox_profile/cookies.sqlite
```

### **Exported CSV**
```
screenshot-app/backend/cookies_*.csv
```

---

## 🛠️ Advanced: Direct JSON Inspection

### **View raw JSON**
```bash
cd screenshot-app/backend
cat browser_sessions/playwright_storage_state.json | python3 -m json.tool | less
```

### **Count cookies**
```bash
cat browser_sessions/playwright_storage_state.json | python3 -c "import json, sys; print(len(json.load(sys.stdin)['cookies']))"
```

### **Extract specific domain**
```bash
cat browser_sessions/playwright_storage_state.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
zomato = [c for c in data['cookies'] if 'zomato' in c.get('domain', '')]
print(json.dumps(zomato, indent=2))
"
```

---

## 🎯 Quick Reference

| Command | What it does |
|---------|-------------|
| `python3 analyze_cookies.py` | Show summary |
| `python3 analyze_cookies.py --domain X` | Filter by domain |
| `python3 analyze_cookies.py --auth` | Show only auth cookies |
| `python3 analyze_cookies.py --all` | Show all cookies |
| `python3 analyze_cookies.py --search X` | Search cookies |
| `python3 analyze_cookies.py --export csv` | Export to CSV |

---

## 🔒 Security Tips

### **✅ Good Practices:**
- Re-extract cookies periodically (they expire)
- Add `browser_sessions/` to `.gitignore`
- Don't commit cookies to git
- Use HTTPS for sites with Secure cookies

### **⚠️ Warning Signs:**
- Many expired cookies → Re-extract
- No auth cookies for logged-in site → Log in again in browser
- HttpOnly=false for auth cookies → Less secure (but still works)

---

## 📚 Examples

### **Example 1: Zomato Screenshot Workflow**

```bash
# 1. Check if you have Zomato cookies
python3 analyze_cookies.py --domain zomato

# 2. If no cookies, log in to Zomato in Chrome, then extract:
#    (Use the UI: Cookies & Auth tab → Extract Cookies)

# 3. Verify extraction
python3 analyze_cookies.py --domain zomato --auth

# 4. Capture screenshots (they'll use the cookies automatically!)
```

### **Example 2: Debug Login Issues**

```bash
# 1. Check all cookies for the site
python3 analyze_cookies.py --domain problematic-site.com --all

# 2. Look for:
#    - Expired cookies
#    - Missing session/auth cookies
#    - Secure cookies (need HTTPS)

# 3. If cookies are expired, re-extract:
#    - Log in again in browser
#    - Extract cookies via UI
#    - Try screenshot again
```

### **Example 3: Bulk Analysis**

```bash
# Export all cookies to CSV
python3 analyze_cookies.py --export csv

# Open in Excel/Google Sheets
open cookies_all.csv

# Sort by:
#    - Domain (to group by site)
#    - Expires (to find expiring cookies)
#    - is_auth (to find auth cookies)
```

---

## 🎉 Summary

**You now have powerful cookie analysis tools!**

- ✅ View cookie summary
- ✅ Filter by domain
- ✅ Search cookies
- ✅ Export to CSV
- ✅ Identify auth cookies
- ✅ Debug login issues

**Use `python3 analyze_cookies.py --help` for all options!**

---

**Happy cookie analyzing!** 🍪🔍

