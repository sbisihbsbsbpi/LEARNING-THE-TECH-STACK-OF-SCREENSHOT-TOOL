# Command Reference

Quick reference for all available commands.

## Installation

```bash
# Install all dependencies
npm install

# Verify environment and setup
npm run setup
```

## Running the Tool

```bash
# Start the interactive CLI
npm start

# Run automated test
npm test
```

## Project Scripts

All scripts defined in `package.json`:

| Command | Description |
|---------|-------------|
| `npm start` | Launch the interactive CLI tool |
| `npm test` | Run automated test with example.com |
| `npm run setup` | Verify environment and create directories |

## Manual Commands

### Run Specific Scripts

```bash
# Run CLI directly
node src/cli.js

# Run setup check
node src/setup.js

# Run test
node src/test.js
```

### Environment Variables

```bash
# Enable debug logging
DEBUG=1 npm start

# Use custom Chrome path
CHROME_PATH="/path/to/chrome" npm start

# Skip Puppeteer download during install
PUPPETEER_SKIP_DOWNLOAD=true npm install
```

## File Management

### View Generated Files

```bash
# List screenshots
ls -lh screenshots/

# List generated documents
ls -lh output/

# Open output directory
open output/
```

### Cleanup

```bash
# Remove screenshots
rm -rf screenshots/*

# Remove generated documents
rm -rf output/*

# Remove all temporary files
rm -rf screenshots/* output/* temp/*

# Full cleanup (including node_modules)
rm -rf node_modules screenshots output temp
npm install
```

## Testing & Debugging

### Run with Debug Output

```bash
DEBUG=1 npm start
```

### Test Individual Components

```javascript
// In Node REPL or a test file

// Test browser detection
import { findChrome } from './src/config.js';
console.log(findChrome());

// Test active tab detection
import { getActiveTabURL } from './src/activeTab.js';
const { url, browser } = await getActiveTabURL();
console.log(url, browser);

// Test screenshot capture
import { captureScreenshot } from './src/browser.js';
await captureScreenshot('https://example.com', 'test.png');
```

### Check Dependencies

```bash
# List installed packages
npm list

# Check for outdated packages
npm outdated

# Audit for vulnerabilities
npm audit

# Update packages
npm update
```

## macOS Specific

### Grant Permissions

```bash
# Open System Preferences
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation"

# Open Privacy & Security
open "x-apple.systempreferences:com.apple.preference.security"
```

### Test AppleScript

```bash
# Test Safari access
osascript -e 'tell application "Safari" to return URL of current tab of front window'

# Test Chrome access
osascript -e 'tell application "Google Chrome" to return URL of active tab of front window'

# Test System Events
osascript -e 'tell application "System Events" to return name of first application process whose frontmost is true'
```

## Development

### Watch for Changes (Manual)

```bash
# Install nodemon globally
npm install -g nodemon

# Run with auto-reload
nodemon src/cli.js
```

### Code Quality

```bash
# Format code (if you add prettier)
npx prettier --write src/

# Lint code (if you add eslint)
npx eslint src/
```

## Troubleshooting Commands

### Verify Node.js

```bash
node --version  # Should be v18+
npm --version
which node
which npm
```

### Verify Chrome

```bash
# Check if Chrome is installed
ls -la "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Get Chrome version
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version
```

### Check Permissions

```bash
# List automation permissions
tccutil reset AppleEvents

# Check file permissions
ls -la src/
chmod +x src/cli.js src/setup.js src/test.js
```

### Reset Everything

```bash
# Complete reset
rm -rf node_modules package-lock.json screenshots output temp
npm install
npm run setup
npm test
```

## Quick Workflows

### Capture Single URL

```bash
npm start
# Choose: Enter URLs manually
# Enter: https://example.com
# Choose: No (don't add more)
# Confirm: Yes
```

### Capture Active Tab

```bash
# 1. Open a website in your browser
# 2. Run:
npm start
# Choose: Capture active browser tab
# Confirm: Yes
```

### Batch Capture

```bash
npm start
# Choose: Paste multiple URLs
# In editor, paste URLs (one per line)
# Save and close editor
# Confirm: Yes
```

## Useful Aliases

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Quick start
alias screenshot='cd "/Users/tlreddy/Documents/project 1" && npm start'

# Quick test
alias screenshot-test='cd "/Users/tlreddy/Documents/project 1" && npm test'

# Open output
alias screenshot-output='open "/Users/tlreddy/Documents/project 1/output"'
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

## Package Management

### Install Specific Versions

```bash
npm install puppeteer-core@21.6.0
npm install docx@8.5.0
npm install sharp@0.33.0
```

### Add New Dependencies

```bash
npm install <package-name>
npm install --save-dev <dev-package>
```

### Remove Dependencies

```bash
npm uninstall <package-name>
```

## Documentation

### View Documentation

```bash
# Open README in browser
open README.md

# View in terminal
cat README.md
less README.md

# Search documentation
grep -r "keyword" *.md
```

## Export & Share

### Create Archive

```bash
# Create zip (excluding node_modules)
zip -r screenshot-tool.zip . -x "node_modules/*" "screenshots/*" "output/*"

# Create tarball
tar -czf screenshot-tool.tar.gz --exclude=node_modules --exclude=screenshots --exclude=output .
```

### Share Project

```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin <your-repo-url>
git push -u origin main
```

---

**Tip**: Run `npm start` to begin using the tool!

