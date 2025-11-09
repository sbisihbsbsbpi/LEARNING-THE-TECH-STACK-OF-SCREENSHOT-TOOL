# 🚀 Quick Start - Cookie Management

**Get started with automated cookie extraction in 5 minutes!**

---

## ⚡ Quick Install

### **Step 1: Install rookiepy**

```bash
cd screenshot-app/backend
pip install rookiepy
```

That's it! rookiepy is the only dependency needed.

---

## 🎯 Quick Test

### **Test 1: Check if rookiepy works**

```bash
cd screenshot-app/backend
python3 -c "import rookiepy; print('✅ rookiepy installed successfully!')"
```

### **Test 2: Detect available browsers**

```bash
python3 << 'EOF'
import rookiepy

print("🔍 Detecting browsers...")
browsers = {
    "Chrome": lambda: rookiepy.chrome([]),
    "Firefox": lambda: rookiepy.firefox([]),
    "Edge": lambda: rookiepy.edge([]),
    "Safari": lambda: rookiepy.safari([]),
    "Brave": lambda: rookiepy.brave([]),
    "Opera": lambda: rookiepy.opera([])
}

available = []
for name, func in browsers.items():
    try:
        func()
        available.append(name)
        print(f"  ✅ {name}")
    except:
        print(f"  ❌ {name} (not installed)")

print(f"\n✅ Available browsers: {', '.join(available)}")
EOF
```

### **Test 3: Extract cookies from Chrome**

```bash
python3 << 'EOF'
import rookiepy

print("🍪 Extracting cookies from Chrome...")
try:
    cookies = rookiepy.chrome()
    print(f"✅ Extracted {len(cookies)} cookies!")
    
    # Show first 3 cookies
    for i, cookie in enumerate(cookies[:3]):
        print(f"  {i+1}. {cookie['name']} ({cookie['domain']})")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

---

## 🎨 Quick UI Test

### **Step 1: Start the backend**

```bash
cd screenshot-app/backend
python3 main.py
```

### **Step 2: Start the frontend**

```bash
cd screenshot-app/frontend
npm run dev
```

### **Step 3: Open the UI**

Open http://localhost:1420 in your browser

### **Step 4: Test cookie extraction**

1. Go to **"Cookies & Auth"** tab
2. Find **"🍪 Import Browser Cookies (Best!)"** section
3. Select your browser (or use Auto-detect)
4. Click **"🍪 Extract Cookies from Browser"**
5. You should see: "✅ Cookies extracted successfully!"

---

## 🧪 Quick API Test

### **Test 1: Browser detection**

```bash
curl http://127.0.0.1:8000/api/cookies/browsers | python3 -m json.tool
```

Expected output:
```json
{
  "browsers": {
    "chrome": true,
    "firefox": true,
    "edge": false,
    ...
  },
  "available": ["chrome", "firefox"],
  "recommended_playwright": "chrome",
  "recommended_camoufox": "firefox"
}
```

### **Test 2: Extract cookies**

```bash
curl -X POST http://127.0.0.1:8000/api/cookies/extract \
  -H "Content-Type: application/json" \
  -d '{
    "domains": null,
    "browser": "auto",
    "engine": "playwright"
  }' | python3 -m json.tool
```

Expected output:
```json
{
  "success": true,
  "filepath": "browser_sessions/playwright_storage_state.json",
  "source_browser": "chrome",
  "cookie_count": 42,
  "domains": ["example.com", "google.com", ...]
}
```

### **Test 3: Check cookie status**

```bash
curl http://127.0.0.1:8000/api/cookies/status | python3 -m json.tool
```

Expected output:
```json
{
  "playwright": {
    "exists": true,
    "cookie_count": 42,
    "extracted_at": "2025-11-03T10:30:00"
  },
  "camoufox": {
    "exists": false,
    "cookie_count": 0
  }
}
```

---

## 📸 Quick Screenshot Test

### **Test with your 56 URLs:**

1. **Log in to your target website** in Chrome/Firefox
2. **Extract cookies** via UI (Cookies & Auth tab)
3. **Add your 56 URLs** in the URLs tab
4. **Click "Capture Screenshots"**
5. **Watch the magic!** ✨

All 56 screenshots will use the extracted cookies automatically!

---

## 🐛 Troubleshooting

### **Problem: "rookiepy not installed"**

```bash
cd screenshot-app/backend
pip install rookiepy
```

### **Problem: "No cookies extracted"**

**Solution:** Make sure you're logged in to the website in your browser first!

1. Open Chrome/Firefox
2. Navigate to your target website
3. Log in normally
4. Then extract cookies

### **Problem: "Browser not detected"**

**Solution:** Specify the browser manually instead of using "Auto-detect"

### **Problem: "Cookies expired"**

**Solution:** Re-extract cookies from your browser

1. Log in again in your browser
2. Click "🔄 Re-extract" in the UI

### **Problem: "Permission denied"**

**macOS/Linux:** rookiepy needs to read browser files. Make sure the browser is closed when extracting cookies.

**Windows:** Run as administrator if needed.

---

## 💡 Pro Tips

### **Tip 1: Extract for specific domains**

Instead of extracting ALL cookies, filter by domain:

```
Domains: zomato.com, swiggy.com
```

This is faster and more focused!

### **Tip 2: Use the right browser for the right engine**

- **Playwright** → Extract from **Chrome** (best match)
- **Camoufox** → Extract from **Firefox** (best match)

### **Tip 3: Re-extract periodically**

Cookies expire! Re-extract every few days or when you see login screens again.

### **Tip 4: Check cookie status before capturing**

Go to "Cookies & Auth" tab and verify:
- ✅ Cookies Imported!
- Count: 42 cookies
- Extracted: Today

---

## 📚 Next Steps

### **Learn More:**

1. **COOKIE_IMPLEMENTATION_COMPLETE.md** - Full implementation details
2. **CAMOUFOX_COOKIE_RESEARCH.md** - Camoufox-specific guide
3. **COOKIE_RESEARCH_SUMMARY.md** - Quick reference

### **Advanced Usage:**

- Extract cookies via API
- Automate cookie refresh
- Use different browsers for different domains
- Integrate with CI/CD pipelines

---

## ✅ Checklist

- [ ] Install rookiepy: `pip install rookiepy`
- [ ] Test browser detection
- [ ] Test cookie extraction
- [ ] Extract cookies via UI
- [ ] Verify cookie status
- [ ] Capture test screenshot
- [ ] Capture your 56 URLs!

---

## 🎉 You're Ready!

**Congratulations!** You now have:

- ✅ Automated cookie extraction
- ✅ Support for all major browsers
- ✅ Beautiful UI
- ✅ Production-ready implementation

**Time to capture those 56 URLs!** 🚀

---

**Questions?** Check the full documentation in `COOKIE_IMPLEMENTATION_COMPLETE.md`

**Issues?** See the Troubleshooting section above

**Ready?** Let's go! 🎊

