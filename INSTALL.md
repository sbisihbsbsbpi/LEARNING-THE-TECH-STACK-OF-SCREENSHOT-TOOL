# Installation Guide

## Prerequisites

### 1. Install Node.js

Download and install Node.js v18 or higher from [nodejs.org](https://nodejs.org/)

Verify installation:
```bash
node --version  # Should show v18.0.0 or higher
npm --version
```

### 2. Install Google Chrome

Download from [google.com/chrome](https://www.google.com/chrome/)

The tool will automatically detect Chrome at:
- `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`

Alternatively, you can use:
- Chromium
- Brave Browser
- Microsoft Edge

## Installation Steps

### Step 1: Install Dependencies

```bash
npm install
```

This will install:
- `puppeteer-core` - Headless browser automation
- `docx` - Word document generation
- `sharp` - Image processing
- `inquirer` - Interactive CLI
- `ora` - Progress spinners
- `chalk` - Terminal colors

**Note**: We use `puppeteer-core` which does NOT download Chromium automatically, keeping the installation small.

### Step 2: Verify Setup

```bash
npm run setup
```

This will check:
- ✓ Node.js version
- ✓ Chrome/Chromium installation
- ✓ AppleScript availability
- ✓ System permissions
- ✓ Create required directories

### Step 3: Grant Permissions (macOS)

#### Automation Permission

When you first run the tool, macOS will ask for permission to control your browser.

**To grant manually**:
1. Open **System Preferences** (or **System Settings** on macOS 13+)
2. Go to **Privacy & Security** > **Automation**
3. Find **Terminal** or **VS Code** (whichever you're using)
4. Enable checkboxes for:
   - Safari
   - Google Chrome
   - Brave Browser
   - Microsoft Edge

#### Safari-Specific Setup

If using Safari's active tab feature:
1. Open Safari
2. Go to **Safari** > **Preferences** > **Advanced**
3. Enable **Show Develop menu in menu bar**
4. In the **Develop** menu, enable **Allow JavaScript from Apple Events**

## Troubleshooting Installation

### "Cannot find module" errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### "No Chrome found" error

Install Google Chrome or set a custom path:

```bash
export CHROME_PATH="/Applications/Chromium.app/Contents/MacOS/Chromium"
npm start
```

### Permission errors

```bash
# Make CLI executable
chmod +x src/cli.js src/setup.js
```

### Apple Silicon (M1/M2) Issues

All dependencies support Apple Silicon natively. If you encounter issues:

```bash
# Ensure you're using ARM64 Node.js
node -p "process.arch"  # Should show 'arm64'
```

## Uninstallation

```bash
# Remove dependencies
rm -rf node_modules

# Remove generated files
rm -rf screenshots output temp

# Remove the project
cd ..
rm -rf "project 1"
```

## Next Steps

After successful installation:

1. **Run the tool**:
   ```bash
   npm start
   ```

2. **Read the usage guide** in [README.md](README.md)

3. **Try a test capture**:
   - Choose "Enter URLs manually"
   - Enter: `https://example.com`
   - Check the `output/` directory for the generated Word document

## Getting Help

If you encounter issues:

1. Run the setup check: `npm run setup`
2. Enable debug mode: `DEBUG=1 npm start`
3. Check the [README.md](README.md) troubleshooting section
4. Verify all prerequisites are installed correctly

## System Requirements

- **OS**: macOS 10.15 (Catalina) or later
- **Node.js**: v18.0.0 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 500MB for dependencies and temporary files
- **Browser**: Chrome, Chromium, Brave, or Edge

## Optional: Global Installation

To use the tool from anywhere:

```bash
npm link
screenshot-tool  # Run from any directory
```

To unlink:
```bash
npm unlink -g headless-screenshot-tool
```

