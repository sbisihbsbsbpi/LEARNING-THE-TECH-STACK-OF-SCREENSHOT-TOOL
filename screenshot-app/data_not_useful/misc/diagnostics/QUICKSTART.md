# 🚀 Quick Start - Fix Auth Issues in 5 Minutes

**Problem:** Screenshots show login page with "Your role has been changed" errors.

**Solution:** Follow these steps to capture and verify your auth session.

---

## ⚡ Step 0: Quick Test (If You Already Have Auth State)

**If you already saved auth state, test it first:**

```bash
cd screenshot-app/diagnostics
python test-auth-state.py
```

**What it does:**

- Opens a VISIBLE browser with your saved auth state
- Navigates to Tekion
- Checks if you get redirected to Okta (FAIL) or stay on Tekion (SUCCESS)
- Shows you exactly what's happening

**Results:**

- ✅ **Stays on Tekion** → Auth state works! Your screenshots should work.
- ❌ **Redirects to Okta** → Auth state is being rejected server-side. Re-save it!

---

## ⚡ Quick Steps

### **1. Install Dependencies**

```bash
cd screenshot-app/diagnostics
npm install
```

### **2. Capture Fresh Session**

```bash
npm run step1
```

**What to do:**

1. Browser opens to Tekion login
2. Log in with Okta + MFA
3. **WAIT 2-3 MINUTES** for dashboard to fully load
4. Make sure **NO errors** visible
5. Press **ENTER** in terminal
6. Session saved! ✅

### **3. Verify Session Works**

```bash
npm run step2
```

**Expected output:**

```
✅ SUCCESS! Session is working!
📸 Screenshot saved to test-screenshot.png
```

**Check:** Open `test-screenshot.png` - should show dashboard, not login page.

### **4. Test Real Captures**

```bash
npm run step5
```

**Expected output:**

```
🎉 ALL TESTS PASSED!
✅ Success: 3/3
```

### **5. Use Screenshot Tool**

Your auth state is now saved in `backend/auth_state.json`.

Go back to your screenshot tool and capture all 56 URLs! 🎉

---

## ❌ If Something Fails

### **Step 2 fails with "Redirected to login"**

**Cause:** Session expired or rejected

**Fix:**

```bash
# Re-capture and wait longer
npm run step1
# Wait 3-5 minutes before pressing ENTER
```

### **Step 2 fails with "Your role has been changed"**

**Cause:** Session captured too early

**Fix:**

```bash
# Re-capture and wait for errors to disappear
npm run step1
# Watch the browser - wait until NO errors visible
# Then wait 2 more minutes
# Then press ENTER
```

### **Step 2 fails with "Cookies expired"**

**Cause:** Old session

**Fix:**

```bash
# Just re-capture
npm run step1
```

### **Need more details?**

```bash
# Deep analysis of cookies and storage
npm run step3

# Test with stealth mode
npm run step4
```

---

## 📊 What Each Step Does

| Step | Script                       | Purpose               | Time    |
| ---- | ---------------------------- | --------------------- | ------- |
| 1    | `step1-capture-fresh.js`     | Capture auth session  | 3-5 min |
| 2    | `step2-verify-session.js`    | Verify session works  | 30 sec  |
| 3    | `step3-debug-cookies.js`     | Debug cookies/storage | 30 sec  |
| 4    | `step4-test-with-stealth.js` | Test stealth mode     | 30 sec  |
| 5    | `step5-test-real-capture.js` | Test real captures    | 1 min   |

---

## 🎯 Success Checklist

- ✅ Step 1: Session captured without errors
- ✅ Step 2: `test-screenshot.png` shows dashboard
- ✅ Step 5: All 3 test URLs captured successfully
- ✅ Screenshot tool works for all 56 URLs

---

## 💡 Pro Tips

### **Tip 1: Wait Longer**

The #1 cause of failures is capturing the session too early.
**Wait 3-5 minutes** after login before pressing ENTER.

### **Tip 2: Check for Errors**

Before pressing ENTER in Step 1, make sure:

- ❌ No "Your role has been changed"
- ❌ No "Unable to fetch"
- ❌ No JSON errors
- ✅ Dashboard fully loaded

### **Tip 3: Same Machine**

Run the screenshot tool on the **same machine** where you captured the session.
Okta may use device binding.

### **Tip 4: Re-capture Before Expiry**

Check cookie expiry with:

```bash
npm run step3
```

Re-capture before cookies expire.

### **Tip 5: Use Chrome Extension**

For even easier auth capture, use the Chrome extension:

```bash
cd ../chrome-extension
python create-icons.py
# Then load in chrome://extensions/
```

---

## 🆘 Still Not Working?

Read the full troubleshooting guide:

```bash
cat README.md
```

Or ask for help with these details:

1. Output from `npm run step2`
2. Output from `npm run step3`
3. Screenshot of the Tekion dashboard
4. Screenshot of `test-screenshot.png`

---

## 🎉 That's It!

**Total time:** 5-10 minutes

**Result:** Working auth state for all 56 URLs

**Happy screenshotting!** 🚀
