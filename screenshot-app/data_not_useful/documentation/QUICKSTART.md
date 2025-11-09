# 🚀 Quick Start Guide

Get the Screenshot Tool running in **3 minutes**!

---

## ⚡ Super Quick Start (Recommended)

### **Option 1: One-Command Start**

```bash
cd screenshot-app
./start.sh
```

This will:
1. ✅ Check prerequisites
2. ✅ Start backend
3. ✅ Start frontend
4. ✅ Open the app

---

## 📋 Manual Start (If you prefer)

### **Step 1: Start Backend**

Open Terminal 1:
```bash
cd screenshot-app/backend
python3 main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### **Step 2: Start Frontend**

Open Terminal 2:
```bash
cd screenshot-app/frontend
npm run tauri dev
```

The desktop app will launch!

---

## 🎯 First Screenshot

1. **Enter a URL** in the text area:
   ```
   https://example.com
   ```

2. **Click "Capture Screenshots"**

3. **Wait** for the screenshot to complete

4. **Review** the result:
   - ✅ Green = Success
   - ❌ Red = Failed (click "🔄 Retry")

5. **Generate Document**:
   - Click "Generate Word Document"
   - Find it in `backend/output/screenshots_report.docx`

---

## 🧪 Test with Multiple URLs

Try these URLs:

```
https://example.com
https://google.com
https://github.com
https://stackoverflow.com
https://reddit.com
```

Paste them all at once (one per line) and click "Capture Screenshots"!

---

## 🐛 Troubleshooting

### **Backend won't start?**

```bash
# Install dependencies
cd screenshot-app/backend
pip3 install -r requirements.txt
playwright install chromium
```

### **Frontend won't start?**

```bash
# Install dependencies
cd screenshot-app/frontend
npm install
```

### **Rust not installed?**

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

---

## 📊 What's Next?

- ✅ Try capturing 10+ URLs at once
- ✅ Experiment with quality checks
- ✅ Generate a Word document
- ✅ Retry failed screenshots
- ✅ Check the API docs at `http://127.0.0.1:8000/docs`

---

## 💡 Pro Tips

1. **Use full URLs** - Always include `https://` or `http://`
2. **Quality scores** - Above 60% is good
3. **Screenshots location** - `backend/screenshots/`
4. **Documents location** - `backend/output/`
5. **API docs** - Visit `http://127.0.0.1:8000/docs` for interactive API testing

---

## 🎉 You're Ready!

The app is now running. Start capturing screenshots!

For more details, see [README.md](README.md)

