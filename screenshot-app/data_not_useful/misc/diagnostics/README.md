# 🔬 Authentication Diagnostics

Comprehensive diagnostic tools to troubleshoot and fix authentication issues with the screenshot tool.

---

## 🎯 The Problem

Your screenshots show the login page with errors like:
- ❌ "Your role has been changed"
- ❌ "Unable to fetch" errors
- ❌ JSON parsing errors

This means the **stored session is not being accepted** by Tekion/Okta.

---

## 🛠️ The Solution (4-Step Process)

### **Step 1: Capture Fresh Session** 🔓

**What it does:**
- Opens a visible Chrome browser
- Lets you log in manually (Okta + MFA)
- Waits for you to confirm the dashboard is fully loaded
- Saves complete session (cookies + localStorage + sessionStorage)

**Run:**
```bash
cd screenshot-app/diagnostics
npm install
npm run step1
```

**Instructions:**
1. Browser opens to Tekion login
2. Complete Okta login + MFA
3. **WAIT 2-3 MINUTES** for dashboard to fully load
4. Make sure you see **NO errors**:
   - No "Your role has been changed"
   - No "Unable to fetch"
   - No JSON errors
5. Press ENTER in terminal
6. Session saved to `backend/auth_state.json`

**Output:**
```
✅ Auth session saved to backend/auth_state.json

📊 Captured data:
   🍪 Cookies: 15
   💾 localStorage items: 25

🔑 Auth cookies found:
   - JSESSIONID (domain: .tekioncloud.com, expires: ...)
   - sid (domain: .tekioncloud.com, expires: ...)

💾 Auth localStorage items found:
   - t_token
   - dse_t_user
   - t_user
```

---

### **Step 2: Verify Session** ✅

**What it does:**
- Reads the saved `auth_state.json`
- Checks for expired cookies
- Tests session in headless browser
- Takes a test screenshot

**Run:**
```bash
npm run step2
```

**What to expect:**

**✅ SUCCESS:**
```
✅ SUCCESS! Session is working!

📝 Next steps:
  1. Check test-screenshot.png to verify it shows the dashboard
  2. If it looks good, your screenshot tool should work now!
```

**❌ FAILURE - Redirected to Login:**
```
❌ FAILED: Redirected to login page!
   The session was not accepted by the server.

Possible causes:
  1. Session expired server-side
  2. Okta device binding (requires same machine/browser)
  3. IP address changed
  4. Session was invalidated (logout, password change, etc.)
```

**❌ FAILURE - Role Change Error:**
```
❌ FAILED: "Your role has been changed" error detected!
   The session was captured too early (before role initialization).
   Re-run step1-capture-fresh.js and wait longer before pressing ENTER.
```

**❌ FAILURE - Expired Cookies:**
```
❌ Some cookies are EXPIRED! Re-capture the session with step1-capture-fresh.js
```

---

### **Step 3: Debug Cookies** 🔬

**What it does:**
- Deep analysis of all cookies and localStorage
- Shows what's in the file vs. what's loaded in browser
- Checks for Tekion-specific auth items
- Identifies missing or expired items

**Run:**
```bash
npm run step3
```

**Output:**
```
═══════════════════════════════════════════════════════
📄 FILE CONTENTS ANALYSIS
═══════════════════════════════════════════════════════

🍪 COOKIES IN FILE:

1. JSESSIONID
   Domain: .tekioncloud.com
   Path: /
   Value: A1B2C3D4E5F6...
   Expires: 12/25/2024, 10:30:00 AM ✅
   HttpOnly: ✅
   Secure: ✅
   SameSite: Lax

...

═══════════════════════════════════════════════════════
💾 LOCALSTORAGE IN FILE:
═══════════════════════════════════════════════════════

Origin: https://preprodapp.tekioncloud.com

1. t_token
   Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

2. dse_t_user
   Value: {"userId":"12345","name":"John Doe"...}

...

═══════════════════════════════════════════════════════
🔑 TEKION-SPECIFIC AUTH ITEMS:
═══════════════════════════════════════════════════════

✅ Found Tekion auth items:
   - t_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   - dse_t_user: {"userId":"12345"...
   - t_user: {"name":"John Doe"...
   - expiryTime: 1735142400000
```

**What to look for:**
- ✅ All Tekion auth items present (`t_token`, `dse_t_user`, `t_user`)
- ✅ No expired cookies
- ✅ Okta cookies present
- ✅ Cookies loaded match cookies in file

---

### **Step 4: Test with Stealth** 🥷

**What it does:**
- Tests session with anti-detection features
- Removes webdriver flags
- Adds realistic browser fingerprint
- Confirms if bot detection is the issue

**Run:**
```bash
npm run step4
```

**Output:**

**✅ If stealth works:**
```
✅ SUCCESS with stealth mode!
🎉 Your session is working with stealth mode!
   The screenshot tool should work now.
```

**❌ If stealth doesn't help:**
```
❌ FAILED: Still redirected to login even with stealth mode!

This confirms the issue is NOT bot detection.
The session itself is being rejected by the server.

Likely causes:
  1. Session expired server-side
  2. Okta device binding (requires same device)
  3. IP address restriction
```

---

## 📊 Diagnostic Decision Tree

```
Start
  │
  ├─ Run Step 1 (Capture Fresh Session)
  │   │
  │   ├─ ✅ Session captured
  │   │   │
  │   │   └─ Run Step 2 (Verify Session)
  │   │       │
  │   │       ├─ ✅ Session works
  │   │       │   │
  │   │       │   └─ 🎉 Done! Use screenshot tool
  │   │       │
  │   │       ├─ ❌ Redirected to login
  │   │       │   │
  │   │       │   └─ Run Step 3 (Debug Cookies)
  │   │       │       │
  │   │       │       ├─ Missing Tekion tokens
  │   │       │       │   └─ Re-run Step 1, wait longer
  │   │       │       │
  │   │       │       ├─ Expired cookies
  │   │       │       │   └─ Re-run Step 1
  │   │       │       │
  │   │       │       └─ Everything looks good
  │   │       │           └─ Run Step 4 (Test Stealth)
  │   │       │               │
  │   │       │               ├─ ✅ Works with stealth
  │   │       │               │   └─ Enable stealth in tool
  │   │       │               │
  │   │       │               └─ ❌ Still fails
  │   │       │                   └─ Server-side issue
  │   │       │                       (See Solutions below)
  │   │       │
  │   │       └─ ❌ "Role changed" error
  │   │           └─ Re-run Step 1, wait 3-5 minutes
  │   │
  │   └─ ❌ Errors during capture
  │       └─ Wait longer before pressing ENTER
```

---

## 🔧 Common Issues & Solutions

### **Issue 1: "Your role has been changed" error**

**Cause:** Session captured before Tekion app fully initialized

**Solution:**
1. Re-run Step 1
2. After logging in, **wait 3-5 minutes**
3. Watch for errors to disappear
4. Only press ENTER when dashboard is stable

---

### **Issue 2: Redirected to login page**

**Cause:** Session expired or rejected by server

**Solutions:**

**A. Session expired:**
- Re-capture session (Step 1)
- Check cookie expiry times (Step 3)

**B. Okta device binding:**
- Run headless browser on **same machine** where you logged in
- Use same Chrome profile
- Ask IT to disable device binding for automation account

**C. IP address changed:**
- Use VPN to maintain same IP
- Run automation from same network
- Ask IT to whitelist automation server IP

**D. Session invalidated:**
- Don't log out after capturing session
- Don't change password
- Don't clear browser cookies

---

### **Issue 3: Missing localStorage items**

**Cause:** Session captured too quickly

**Solution:**
1. Re-run Step 1
2. Wait for **all network requests** to complete
3. Open DevTools → Network tab
4. Make sure no pending requests
5. Then press ENTER

---

### **Issue 4: Cookies expired**

**Cause:** Tekion/Okta has short-lived sessions

**Solutions:**

**A. Auto-refresh (Recommended):**
Add session refresh logic to screenshot tool:
```javascript
if (page.url().includes('okta.com') || page.url().includes('login')) {
  console.log('⚠️ Session expired. Re-capturing...');
  // Re-run Step 1 automatically
}
```

**B. Extend session lifetime:**
- Ask IT to increase session timeout
- Use "Remember Me" option if available

**C. Use service account:**
- Ask IT for non-MFA automation account
- Service accounts often have longer sessions

---

### **Issue 5: Bot detection**

**Cause:** Tekion/Okta detects headless browser

**Solution:**
- Run Step 4 to test with stealth mode
- If it works, enable stealth in screenshot tool
- Use real Chrome (not Chromium)
- Use visible browser mode instead of headless

---

## 🎯 Best Practices

### **1. Capture Session Properly**
- ✅ Wait 3-5 minutes after login
- ✅ Verify no errors on page
- ✅ Check DevTools Network tab (no pending requests)
- ✅ Navigate to a few pages to warm up session

### **2. Test Session Immediately**
- ✅ Run Step 2 right after Step 1
- ✅ Verify test screenshot shows dashboard
- ✅ Don't wait days before testing

### **3. Monitor Session Health**
- ✅ Check cookie expiry times (Step 3)
- ✅ Re-capture before expiry
- ✅ Set up alerts for expired sessions

### **4. Use Same Environment**
- ✅ Same machine for capture and use
- ✅ Same network/IP address
- ✅ Same Chrome version

---

## 📝 Quick Reference

### **File Locations:**
```
screenshot-app/
├── backend/
│   └── auth_state.json          # Saved session (created by Step 1)
└── diagnostics/
    ├── step1-capture-fresh.js   # Capture session
    ├── step2-verify-session.js  # Test session
    ├── step3-debug-cookies.js   # Debug cookies
    ├── step4-test-with-stealth.js # Test stealth
    ├── test-screenshot.png      # Test output (Step 2)
    └── test-screenshot-stealth.png # Test output (Step 4)
```

### **Commands:**
```bash
npm run step1  # Capture fresh session
npm run step2  # Verify session works
npm run step3  # Debug cookies/storage
npm run step4  # Test with stealth mode
```

---

## 🆘 Still Not Working?

If you've tried everything and it still doesn't work:

### **Option 1: Use Service Account**
Ask IT for:
- Non-MFA automation account
- Longer session timeout
- API key/token instead of cookies

### **Option 2: Use Real Browser Mode**
Instead of headless:
```javascript
const browser = await chromium.launch({ 
  headless: false,  // Visible browser
  channel: 'chrome'
});
```

### **Option 3: Use Playwright Codegen**
Let Playwright record the login:
```bash
npx playwright codegen https://preprodapp.tekioncloud.com
```

### **Option 4: Contact Tekion Support**
Ask about:
- API access for automation
- Service accounts
- Automation-friendly authentication

---

## 🎉 Success Criteria

You know it's working when:
- ✅ Step 2 shows "SUCCESS! Session is working!"
- ✅ `test-screenshot.png` shows the dashboard (not login page)
- ✅ No "Your role has been changed" errors
- ✅ No "Unable to fetch" errors
- ✅ Screenshot tool captures all 56 URLs successfully

---

**Good luck! 🚀**

