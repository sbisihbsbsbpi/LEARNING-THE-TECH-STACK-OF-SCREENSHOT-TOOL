# 🦁 Brave CDP - Quick Start

## 🚀 Fastest Way to Enable CDP

### **Option 1: Use the Launch Script (Recommended)**

```bash
cd screenshot-app
./launch-brave-cdp.sh
```

The script will:
- ✅ Check if Brave is installed
- ✅ Ask which profile to use (temporary or real)
- ✅ Close existing Brave instances if needed
- ✅ Launch Brave with CDP on port 9222
- ✅ Verify CDP is working
- ✅ Show you next steps

---

### **Option 2: Manual Command (Quick & Simple)**

**Temporary Profile (Safe):**
```bash
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/brave-debug-profile" &
```

**Real Profile (Keep Your Sessions):**
```bash
# Close Brave first!
killall "Brave Browser"

# Launch with CDP
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/BraveSoftware/Brave-Browser" &
```

---

## ✅ Verify It's Working

Open this URL in any browser:
```
http://localhost:9222/json/version
```

**Or use curl:**
```bash
curl http://localhost:9222/json/version
```

**Expected output:**
```json
{
  "Browser": "Chrome/120.0.6099.109",
  "Protocol-Version": "1.3",
  ...
}
```

✅ If you see JSON output, CDP is working!

---

## 📸 Use with Screenshot Tool

1. **Launch Brave with CDP** (using one of the methods above)

2. **Open Screenshot Tool**

3. **Enable CDP Mode:**
   - Go to **Settings** section
   - Find **"🌐 Real Browser Mode (CDP Mode)"**
   - Check the box: ☑ **"Use real browser"**

4. **Start Capturing:**
   - Enter URLs in the text box
   - Click "Capture Screenshots"
   - Tool will open new tabs in Brave
   - Screenshots will be saved automatically

---

## 🎯 What Works with Brave CDP

- ✅ **Auto-scroll** (segmented capture)
- ✅ **Dropdown detection** (auto-expand collapsed sections)
- ✅ **Parallel processing** (1-10 tabs at once)
- ✅ **Cookie extraction** (import from Brave)
- ✅ **Session reuse** (stay logged in)
- ✅ **Real-time visibility** (see what's happening)

---

## 🛑 Stop CDP

**Close Brave normally**, or:

```bash
killall "Brave Browser"
```

---

## 📚 Full Documentation

See `BRAVE_CDP_SETUP.md` for:
- Detailed setup instructions
- Windows/Linux commands
- Troubleshooting guide
- Security notes
- Advanced configuration

---

## 🎉 That's It!

You're ready to use Brave with your screenshot tool!

**Quick recap:**
1. ✅ Run: `./launch-brave-cdp.sh`
2. ✅ Verify: `http://localhost:9222/json/version`
3. ✅ Enable CDP mode in screenshot tool
4. ✅ Start capturing!

**Happy screenshotting!** 🦁📸

