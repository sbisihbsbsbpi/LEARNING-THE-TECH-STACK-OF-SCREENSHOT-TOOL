# 🔐 Authentication Setup Guide

This guide explains how to save your authentication state so the screenshot tool can capture screenshots from login-protected pages.

---

## 🎯 **Two Options Available**

### **Option 1: Use the Built-in UI (Recommended)** ⭐

The easiest way - everything is built into the app!

#### **Steps:**

1. **Start the app** (if not already running):
   ```bash
   cd screenshot-app
   # Terminal 1: Start backend
   cd backend && python main.py
   
   # Terminal 2: Start frontend
   cd frontend && npm run dev
   ```

2. **Open the app** in your browser:
   - http://localhost:1420

3. **Go to 🔐 Auth Data tab**

4. **Click "🔓 Login & Save Auth State"**

5. **Enter the login URL** in the modal (e.g., `https://preprodapp.tekioncloud.com/home`)

6. **Click "Start Login"**

7. **Browser window opens** - Complete your login:
   - Enter credentials
   - Complete MFA/2FA
   - Wait for dashboard to load

8. **Wait for auto-detection**:
   - Tool checks every 5 seconds
   - Waits for auth tokens to appear
   - Waits for all errors to clear
   - Waits 60 more seconds for full initialization

9. **Auth state saved!** ✅
   - Browser stays open for you to verify
   - Close it manually when satisfied

10. **Capture screenshots!** 🎉
    - Go to 📸 Main tab
    - Paste URLs
    - Click "Capture Screenshots"
    - Tool automatically uses saved auth state

#### **Pros:**
- ✅ No coding required
- ✅ Built into the app
- ✅ Enhanced detection (waits for errors to clear)
- ✅ 60-second wait for full initialization
- ✅ Visual feedback in the UI
- ✅ Separate browser instance (won't interfere with captures)

---

### **Option 2: Manual Script** 🛠️

If you prefer more control or want to automate this outside the app.

#### **JavaScript Version:**

```bash
cd screenshot-app
node save-auth-manual.js
```

**What it does:**
1. Opens Chrome browser
2. Navigates to login page
3. Waits for you to log in manually
4. You press ENTER when ready
5. Saves auth state to `backend/auth_state.json`
6. Closes browser

#### **Python Version:**

```bash
cd screenshot-app
python save-auth-manual.py
```

**What it does:**
- Same as JavaScript version
- Uses Python + Playwright

#### **Pros:**
- ✅ More control over timing
- ✅ Can be automated/scripted
- ✅ Can customize the login URL
- ✅ Can run outside the app

#### **Cons:**
- ❌ Requires manual ENTER press
- ❌ No auto-detection of login completion
- ❌ No error checking
- ❌ You must verify dashboard is ready yourself

---

## 📁 **Where is the Auth State Saved?**

Both options save to the same file:
```
screenshot-app/backend/auth_state.json
```

This file contains:
- 🍪 **Cookies** (session cookies, auth cookies, etc.)
- 💾 **localStorage** (JWT tokens, user data, etc.)
- 📦 **sessionStorage** (temporary session data)

---

## 🔄 **When to Re-save Auth State?**

You need to re-save the auth state when:

1. **Tokens expire** ⏰
   - Most JWT tokens expire after 24 hours or 7 days
   - You'll see login pages in screenshots again

2. **Password changed** 🔑
   - After changing your password

3. **Session invalidated** 🚫
   - After logging out from the browser
   - After clearing browser data

4. **Role changed** 👤
   - If your role/permissions change in the app

---

## 🧪 **Testing the Auth State**

After saving the auth state, test it:

1. **Go to 📸 Main tab**
2. **Paste a login-protected URL**
3. **Click "Capture Screenshots"**
4. **Check the screenshot**:
   - ✅ Should show the authenticated page (dashboard, data, etc.)
   - ❌ Should NOT show the login page

If you see the login page, the auth state didn't work. Try:
- Re-saving with a longer wait time
- Making sure all errors cleared before saving
- Checking if the app uses different auth for different URLs

---

## 🔍 **Troubleshooting**

### **Problem: Screenshots still show login page**

**Possible causes:**
1. Auth state saved too early (before errors cleared)
2. Tokens expired
3. Different domain/subdomain requires different auth
4. App uses additional security (IP restrictions, device fingerprinting)

**Solutions:**
1. Delete `backend/auth_state.json` and re-save
2. Wait longer before saving (use manual script and wait 2-3 minutes)
3. Check if the URL domain matches the login URL domain
4. Try using "Real Browser" mode instead of headless

### **Problem: "Your role has been changed" error**

**Cause:** Auth state was saved before role initialization completed

**Solution:**
1. Delete `backend/auth_state.json`
2. Re-save auth state
3. Wait for the "Your role has been changed" message to disappear
4. Wait for all "Unable to fetch" errors to disappear
5. Wait 60+ seconds after errors clear
6. Then save (or press ENTER if using manual script)

### **Problem: Browser closes immediately when capturing**

**Cause:** This was a bug in earlier versions (now fixed)

**Solution:**
1. Make sure you're using the latest code
2. Login browser and screenshot browser are now separate instances
3. They won't interfere with each other

---

## 💡 **Tips for Best Results**

1. **Wait for full page load** ⏰
   - Don't save auth state immediately after login
   - Wait for all data to load (dealer info, language, location, etc.)
   - Wait for all error messages to disappear

2. **Verify in the browser** 👀
   - Before saving, visually confirm the dashboard looks perfect
   - No error messages
   - No loading spinners
   - All data loaded

3. **Use the same URL** 🔗
   - Save auth state from the same URL you'll be capturing
   - Example: If capturing `/inventory`, log in to `/inventory` or `/home`

4. **Check token expiry** ⏱️
   - If captures start failing after a few days, re-save auth state
   - Some tokens expire after 24 hours, others after 7 days

5. **Keep the auth window open** 🪟
   - After saving, the browser stays open
   - Verify the dashboard looks good
   - Try navigating to different pages to test
   - Close manually when satisfied

---

## 🔐 **Security Notes**

⚠️ **Important:**

1. **Don't commit `auth_state.json` to git**
   - It contains your session tokens
   - Anyone with this file can access your account
   - Already added to `.gitignore`

2. **Don't share `auth_state.json`**
   - Treat it like a password
   - It gives full access to your account

3. **Tokens expire automatically**
   - Most tokens expire after 24 hours to 7 days
   - This limits the risk if the file is compromised

4. **Logout invalidates tokens**
   - If you suspect the file was compromised, log out
   - This invalidates all session tokens

---

## 📚 **How It Works (Technical)**

### **Playwright Storage State:**

Playwright's `storageState()` API captures the entire browser state:

```javascript
// Save
await context.storageState({ path: 'auth_state.json' });

// Load
const context = await browser.newContext({
  storageState: 'auth_state.json'
});
```

### **What's Captured:**

1. **Cookies:**
   - All cookies from all domains visited
   - Includes HttpOnly cookies (inaccessible to JavaScript)
   - Session cookies, auth cookies, tracking cookies

2. **localStorage:**
   - Key-value pairs stored by the website
   - JWT tokens (e.g., `t_token` in Tekion app)
   - User preferences, settings, cached data

3. **sessionStorage:**
   - Temporary session data
   - Cleared when browser closes (but captured in the file)

### **How It's Used:**

When capturing screenshots:
1. Tool creates a new browser context
2. Loads the saved storage state
3. Browser now has all cookies + localStorage + sessionStorage
4. Navigates to the URL
5. Website sees the auth tokens and allows access
6. Screenshot captured! ✅

---

## 🎉 **Summary**

**Recommended workflow:**

1. **Save auth state once** (using built-in UI)
2. **Capture screenshots** (as many as you want)
3. **Re-save when tokens expire** (every few days)

**That's it!** No need to log in for every screenshot. 🚀

