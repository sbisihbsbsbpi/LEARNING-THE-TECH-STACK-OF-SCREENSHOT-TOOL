# 🚀 Active Tab Mode - Quick Start

**Use your existing Chrome browser for screenshots!**

---

## ⚡ 3 Simple Steps

### **Step 1: Launch Chrome with Debugging**

**Close your current Chrome** (if it's open):

- Press `Cmd+Q` to quit Chrome completely

**Then launch Chrome with debugging:**

```bash
cd screenshot-app
./launch-chrome-debug.sh
```

**What this does:**

- Launches Chrome with remote debugging enabled on port 9222
- **Uses your normal Chrome profile** (all your logins, cookies, extensions preserved!)
- Allows the screenshot tool to connect to Chrome
- Chrome will open with a visible window

**Verify it's working:**

```bash
./check-chrome-debug.sh
```

You should see: `✅ Chrome is running with remote debugging on port 9222`

**Important:** This is your normal Chrome! You can browse, login, do anything you normally do. The tool will just connect to it when you capture screenshots.

---

### **Step 2: Enable Real Browser Mode**

1. Open the screenshot tool (if not already running):

   ```bash
   npm start
   ```

2. Click the **⚙️ Settings** button (top right)

3. Scroll to **"Real Browser"** option

4. Toggle it **ON** ✅

5. Click **Main** tab to go back

---

### **Step 3: Capture Screenshots**

1. Enter your URLs (one per line)

2. Click **"Capture Screenshots"**

3. **Watch** as each URL loads in your Chrome tab!

4. Screenshots are captured automatically

---

## 🎯 What You'll See

When you click "Capture Screenshots":

1. ✅ Your Chrome browser will come to the front
2. ✅ The active tab will navigate to each URL
3. ✅ You'll see the page load in real-time
4. ✅ Screenshot is captured
5. ✅ Next URL loads automatically
6. ✅ Repeat until all URLs are done

---

## 💡 Tips

### **Best Practices**

- ✅ Keep Chrome visible (don't minimize)
- ✅ Don't switch tabs during capture
- ✅ Let the tool control the active tab
- ✅ Watch for any errors or issues

### **Troubleshooting**

**Problem**: "Failed to connect to Chrome via CDP"

**Solution**: Make sure you ran `./launch-chrome-debug.sh` first

---

**Problem**: "No tabs found in Chrome"

**Solution**: Open at least one tab in Chrome (Cmd+T)

---

**Problem**: Screenshots are blank

**Solution**: Increase timeout in Settings or wait for pages to load

---

## 🆚 When to Use Active Tab Mode

### **Use Active Tab Mode When:**

- 🎯 You want to **see** what's being captured
- 🐛 You're **debugging** screenshot issues
- 🔐 You need to **login manually** first
- 🤝 Sites require **manual interaction**
- ✅ You want to **verify** content before capturing

### **Use Standard Mode When:**

- ⚡ You need **speed** (100+ URLs)
- 🤖 You want **automation** (no manual steps)
- 🌙 You want **headless** (background processing)
- 🔄 You're running in **CI/CD**

---

## 📚 More Information

- **Full Guide**: [ACTIVE_TAB_MODE.md](./ACTIVE_TAB_MODE.md)
- **Implementation**: [ACTIVE_TAB_IMPLEMENTATION.md](./ACTIVE_TAB_IMPLEMENTATION.md)
- **Main README**: [README.md](./README.md)

---

## 🎉 That's It!

You're now using Active Tab Mode! Enjoy watching your screenshots being captured in real-time! 🚀
