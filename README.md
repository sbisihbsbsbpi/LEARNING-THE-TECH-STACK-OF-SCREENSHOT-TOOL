# 📸 Screenshot Headless Tool

> Professional desktop application for automated screenshot capture with authentication state management, segmented capture, quality checking, and document generation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node](https://img.shields.io/badge/Node-16+-green.svg)](https://nodejs.org/)
[![Tauri](https://img.shields.io/badge/Tauri-1.5+-orange.svg)](https://tauri.app/)

---

## 🎯 Main Application: Desktop App (Tauri + React + FastAPI)

The main application is a modern desktop app located in the **`screenshot-app/`** directory.

👉 **[Go to Desktop App Documentation](screenshot-app/README.md)**

### Key Features

- 🖥️ **Desktop Application** - Built with Tauri (3-10 MB bundle)
- 🔐 **Authentication State Management** - Save and reuse login sessions
- 📸 **Segmented Capture** - Capture long pages in multiple segments
- 🥷 **Stealth Mode** - Anti-bot detection with playwright-stealth
- 📊 **Quality Checking** - Auto-detect blank/low-quality screenshots
- 📄 **Document Generation** - Export to Word (.docx)
- 📁 **URL Library** - Organize URLs in folders
- 💾 **Session History** - Track capture sessions

---

## 📦 Legacy CLI Tool (Node.js + Puppeteer)

This repository also contains the original CLI tool for quick screenshot captures.

## ✨ Features

- **Headless Browser Automation**: Uses Puppeteer with Chrome/Chromium for reliable, pixel-perfect screenshots
- **Multiple Input Methods**:
  - Manual URL entry
  - Capture active browser tab (Safari, Chrome, Brave, Edge)
  - Paste multiple URLs at once
- **Full-Page Screenshots**: Captures entire webpage, not just viewport
- **Word Document Generation**: Creates professional .docx files with:
  - Title page with metadata
  - Each screenshot on its own page
  - URL headings and capture timestamps
  - Automatic image optimization
- **Robust Error Handling**: Automatic retries, detailed logging, graceful failure handling
- **macOS Optimized**: Native AppleScript integration for browser tab detection

## 🚀 Quick Start

### Prerequisites

- **macOS** (10.15 or later)
- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Google Chrome** or Chromium ([Download](https://www.google.com/chrome/))

### Installation

1. **Install dependencies**:

   ```bash
   npm install
   ```

2. **Run setup check**:

   ```bash
   npm run setup
   ```

3. **Start the tool**:
   ```bash
   npm start
   ```

## 📖 Usage

### Interactive CLI

Run `npm start` and follow the prompts:

1. **Choose input method**:

   - Enter URLs manually (one at a time)
   - Capture the active browser tab
   - Paste multiple URLs (opens your default editor)

2. **Review and confirm** the URLs to capture

3. **Wait for processing**:

   - Screenshots are captured with progress indication
   - Word document is generated automatically

4. **Open the document** or find it in the `output/` directory

### Example Workflow

```bash
$ npm start

📸 Headless Screenshot Tool
Capture website screenshots and generate Word documents
────────────────────────────────────────────────────────────
✓ Found browser: Google Chrome
────────────────────────────────────────────────────────────

? How would you like to provide URLs?
  📝 Enter URLs manually
❯ 🌐 Capture active browser tab
  📋 Paste multiple URLs (one per line)
```

### Permissions

On first run, macOS may ask for permissions:

- **Automation**: Allow Terminal/VS Code to control your browser
  - Go to: **System Preferences > Privacy & Security > Automation**
  - Enable access for Terminal or VS Code

## 📁 Project Structure

```
headless-screenshot-tool/
├── src/
│   ├── cli.js           # Interactive command-line interface
│   ├── browser.js       # Puppeteer screenshot capture
│   ├── document.js      # Word document generation
│   ├── activeTab.js     # Browser tab detection (AppleScript)
│   ├── config.js        # Configuration and settings
│   ├── logger.js        # Logging utility
│   └── setup.js         # Environment setup script
├── assets/              # Favicon images
├── screenshots/         # Temporary screenshot storage
├── output/              # Generated Word documents
├── package.json
└── README.md
```

## ⚙️ Configuration

Edit `src/config.js` to customize:

- **Screenshot settings**: viewport size, quality, timeout
- **Document settings**: page size, margins, image width
- **Retry behavior**: max attempts, delay between retries
- **Browser paths**: additional Chrome/Chromium locations

## 🔧 Advanced Usage

### Environment Variables

```bash
# Enable debug logging
DEBUG=1 npm start

# Skip Puppeteer Chromium download (use system Chrome)
PUPPETEER_SKIP_DOWNLOAD=true npm install
```

### Programmatic Usage

```javascript
import { captureMultiple } from "./src/browser.js";
import { generateDocument } from "./src/document.js";

const urls = ["https://example.com", "https://github.com"];
const results = await captureMultiple(urls);
await generateDocument(results, "output.docx");
```

## 🐛 Troubleshooting

### "No Chrome/Chromium browser found"

**Solution**: Install Google Chrome from https://www.google.com/chrome/

### "Failed to get active tab"

**Causes**:

- Browser is not running or has no open tabs
- Permission not granted for automation

**Solution**:

1. Make sure your browser is open with an active tab
2. Grant automation permission in System Preferences
3. For Safari: Enable **Develop > Allow JavaScript from Apple Events**

### Screenshots are blank or incomplete

**Solutions**:

- Increase timeout in `config.js` (`screenshot.timeout`)
- Check if the website blocks headless browsers
- Try with a different URL to verify setup

### "Permission denied" errors

**Solution**: Grant Terminal/VS Code full disk access:

- **System Preferences > Privacy & Security > Full Disk Access**
- Add Terminal or VS Code to the list

## 📦 Dependencies

- **puppeteer-core**: Headless browser automation
- **docx**: Word document generation
- **sharp**: Image processing and optimization
- **inquirer**: Interactive CLI prompts
- **ora**: Terminal spinners
- **chalk**: Terminal colors

## 🎯 Use Cases

- **Web Development**: Document website states for clients
- **QA Testing**: Capture screenshots of different pages for bug reports
- **Archiving**: Create offline records of web content
- **Presentations**: Generate documentation with website screenshots
- **Compliance**: Record website states for audits

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## ⚡ Performance Tips

- **Parallel captures**: The tool processes URLs sequentially to avoid overwhelming your system
- **Image optimization**: Large screenshots are automatically resized for the document
- **Cleanup**: Screenshots are stored in `screenshots/` and can be deleted after document generation

## 🔐 Privacy & Security

- All processing happens **locally** on your machine
- No data is sent to external servers
- Screenshots are stored temporarily and can be deleted
- Browser automation uses standard Puppeteer APIs

## 📞 Support

For issues or questions:

1. Check the troubleshooting section above
2. Run `npm run setup` to verify your environment
3. Enable debug logging with `DEBUG=1 npm start`
4. [Open an issue](https://github.com/sbisihbsbsbpi/screenshot-headless-tool/issues) on GitHub

---

## 📁 Repository Structure

```
screenshot-headless-tool/
├── screenshot-app/          # 🎯 Main Desktop Application (Tauri + React + FastAPI)
│   ├── backend/            # Python FastAPI backend
│   ├── frontend/           # React + TypeScript frontend
│   └── README.md           # Desktop app documentation
├── src/                    # 📦 Legacy CLI Tool (Node.js + Puppeteer)
│   ├── cli.js
│   ├── browser.js
│   └── ...
├── LICENSE                 # MIT License
├── CONTRIBUTING.md         # Contribution guidelines
├── CHANGELOG.md            # Version history
└── README.md               # This file
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) - Browser automation
- [Tauri](https://tauri.app/) - Desktop framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Puppeteer](https://pptr.dev/) - Headless Chrome automation
- [playwright-stealth](https://github.com/AtuboDad/playwright_stealth) - Stealth library

---

**Built with ❤️ using Tauri + React + FastAPI + Playwright**
