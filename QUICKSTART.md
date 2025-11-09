# Quick Start Guide

Get up and running in 3 minutes!

## 1. Install Dependencies

```bash
npm install
```

## 2. Verify Setup

```bash
npm run setup
```

You should see:
```
✅ Setup Complete!
✓ All checks passed. You can now run: npm start
```

## 3. Run the Tool

```bash
npm start
```

## 4. Follow the Prompts

### Option A: Quick Test (Active Tab)
1. Open a website in your browser (Chrome, Safari, Brave, or Edge)
2. Run `npm start`
3. Choose **"Capture active browser tab"**
4. Wait for processing
5. Open the generated Word document from `output/`

### Option B: Manual Entry
1. Run `npm start`
2. Choose **"Enter URLs manually"**
3. Enter: `https://example.com`
4. Choose "No" when asked to add more
5. Confirm and wait
6. Open the generated document

### Option C: Multiple URLs
1. Run `npm start`
2. Choose **"Paste multiple URLs"**
3. In the editor that opens, paste:
   ```
   https://example.com
   https://github.com
   https://stackoverflow.com
   ```
4. Save and close the editor
5. Confirm and wait
6. Open the generated document

## Expected Output

You'll find a Word document in the `output/` directory:
- Filename: `screenshots_YYYY-MM-DD_timestamp.docx`
- Contains: Title page + one page per URL with screenshot

## Troubleshooting

### "No Chrome found"
→ Install [Google Chrome](https://www.google.com/chrome/)

### "Permission denied"
→ Grant automation permission in **System Preferences > Privacy & Security > Automation**

### "Failed to get active tab"
→ Make sure your browser is open with an active tab

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [USAGE.md](USAGE.md) for advanced features
- Customize settings in `src/config.js`

## Test Command

Run a quick automated test:
```bash
npm test
```

This captures example.com and creates `output/test-output.docx`.

---

**Need help?** Check the troubleshooting sections in README.md and INSTALL.md

