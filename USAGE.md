# Usage Guide

## Quick Start

```bash
npm start
```

Follow the interactive prompts to capture screenshots and generate a Word document.

## Input Methods

### 1. Manual URL Entry

Enter URLs one at a time:

```
? How would you like to provide URLs? Enter URLs manually
? Enter URL 1: https://example.com
? Add another URL? Yes
? Enter URL 2: https://github.com
? Add another URL? No
```

**Best for**: Small number of URLs, careful selection

### 2. Active Browser Tab

Automatically capture the URL from your current browser tab:

```
? How would you like to provide URLs? Capture active browser tab
✓ Got URL from Google Chrome
URL: https://github.com/explore
```

**Best for**: Quick single-page captures, documenting current work

**Supported browsers**:
- Safari
- Google Chrome
- Brave Browser
- Microsoft Edge

### 3. Paste Multiple URLs

Opens your default text editor to paste multiple URLs:

```
? How would you like to provide URLs? Paste multiple URLs
# Editor opens with:
https://example.com
https://github.com
https://stackoverflow.com
```

**Best for**: Bulk captures, pre-prepared URL lists

## Workflow

### Step-by-Step Process

1. **Choose input method** → Select how to provide URLs
2. **Enter/select URLs** → Provide one or more URLs
3. **Confirm** → Review and confirm the list
4. **Capture** → Watch progress as screenshots are taken
5. **Generate** → Word document is created automatically
6. **Open** → Optionally open the document immediately

### Example Session

```bash
$ npm start

📸 Headless Screenshot Tool
────────────────────────────────────────────────────────────
✓ Found browser: Google Chrome
────────────────────────────────────────────────────────────

? How would you like to provide URLs? Enter URLs manually
? Enter URL 1: https://example.com
? Add another URL? Yes
? Enter URL 2: https://github.com
? Add another URL? No

────────────────────────────────────────────────────────────
ℹ Total URLs to capture: 2
────────────────────────────────────────────────────────────

? Proceed with screenshot capture? Yes

📸 Capturing Screenshots

✓ Capturing: https://example.com
✓ Screenshot saved: screenshot_1_1698765432.png (245.67 KB, 3421ms)
✓ Capturing: https://github.com
✓ Screenshot saved: screenshot_2_1698765436.png (512.34 KB, 4123ms)
✓ Captured 2 screenshots (0 failed)

────────────────────────────────────────────────────────────

📄 Generating Word Document

✓ Document created successfully

────────────────────────────────────────────────────────────

✅ Complete!

✓ Document saved to: output/screenshots_2024-10-31_1698765440.docx
ℹ Total screenshots: 2/2

────────────────────────────────────────────────────────────

? Open the document now? Yes
✓ Opening document...
```

## Output

### Screenshot Files

Temporary PNG files are saved to `screenshots/`:
- `screenshot_1_<timestamp>.png`
- `screenshot_2_<timestamp>.png`
- etc.

**Note**: These can be deleted after the Word document is generated.

### Word Document

Generated `.docx` file in `output/`:
- Filename: `screenshots_<date>_<timestamp>.docx`
- Contains:
  - Title page with metadata
  - Each URL on a separate page
  - Full-page screenshot
  - Capture timestamp and file size

### Document Structure

```
Page 1: Title Page
  - "Website Screenshots Report"
  - Generation date/time
  - Total URL count

Page 2: First URL
  - URL as heading
  - Capture metadata
  - Full-page screenshot

Page 3: Second URL
  - URL as heading
  - Capture metadata
  - Full-page screenshot

... (one page per URL)
```

## Advanced Usage

### Environment Variables

```bash
# Enable debug logging
DEBUG=1 npm start

# Use custom Chrome path
CHROME_PATH="/Applications/Chromium.app/Contents/MacOS/Chromium" npm start
```

### Programmatic API

```javascript
import { captureMultiple } from './src/browser.js';
import { generateDocument } from './src/document.js';
import { getActiveTabURL } from './src/activeTab.js';

// Capture screenshots
const urls = ['https://example.com', 'https://github.com'];
const results = await captureMultiple(urls, (current, total, url, success) => {
  console.log(`Progress: ${current}/${total}`);
});

// Generate document
await generateDocument(results, 'my-screenshots.docx');

// Get active tab
const { url, browser } = await getActiveTabURL();
console.log(`Active tab in ${browser}: ${url}`);
```

### Custom Configuration

Edit `src/config.js` to customize:

```javascript
// Screenshot settings
screenshot: {
  fullPage: true,           // Capture full page
  type: 'png',              // Image format
  quality: 90,              // JPEG quality (if type is 'jpeg')
  waitUntil: 'networkidle2', // Wait condition
  timeout: 60000,           // Max wait time (ms)
  viewport: {
    width: 1920,            // Viewport width
    height: 1080,           // Viewport height
    deviceScaleFactor: 1    // Pixel density
  }
}

// Document settings
document: {
  imageWidth: 6.5 * 914.4,  // Image width in document (twips)
  margins: {
    top: 720,               // 0.5 inch
    right: 720,
    bottom: 720,
    left: 720
  }
}

// Retry settings
retry: {
  maxAttempts: 3,           // Max retry attempts
  delayMs: 2000             // Delay between retries
}
```

## Tips & Best Practices

### For Best Results

1. **Use full URLs**: Always include `https://` or `http://`
2. **Wait for completion**: Don't interrupt the capture process
3. **Check permissions**: Grant automation access when prompted
4. **Stable internet**: Ensure good connection for reliable captures
5. **Close unnecessary tabs**: Reduce browser memory usage

### Performance

- **Sequential processing**: URLs are captured one at a time to avoid overwhelming the system
- **Automatic retries**: Failed captures are retried up to 3 times
- **Image optimization**: Large screenshots are automatically resized for the document
- **Memory management**: Browser instances are closed after each capture

### Common Patterns

**Document a website**:
```bash
# Capture multiple pages from the same site
https://example.com
https://example.com/about
https://example.com/contact
https://example.com/products
```

**Compare websites**:
```bash
# Capture the same page from different sites
https://site1.com/pricing
https://site2.com/pricing
https://site3.com/pricing
```

**Archive current work**:
```bash
# Use active tab capture repeatedly
1. Open tab → Run tool → Capture active tab
2. Switch tab → Run tool → Capture active tab
3. Repeat...
```

## Troubleshooting

### Screenshots are blank

**Cause**: Website may block headless browsers or take too long to load

**Solutions**:
- Increase timeout in `config.js`
- Check if the site requires authentication
- Try a different URL to verify setup

### "Failed to get active tab"

**Cause**: Browser not running or permission not granted

**Solutions**:
- Ensure browser is open with an active tab
- Grant automation permission in System Preferences
- For Safari: Enable "Allow JavaScript from Apple Events"

### Slow captures

**Cause**: Large pages, slow network, or many resources

**Solutions**:
- Reduce viewport size in `config.js`
- Use faster internet connection
- Capture fewer URLs at once

### Document too large

**Cause**: Many high-resolution screenshots

**Solutions**:
- Reduce `imageWidth` in `config.js`
- Lower `deviceScaleFactor` in viewport settings
- Capture fewer URLs per document

## Cleanup

### Remove temporary files

```bash
# Remove screenshots
rm -rf screenshots/*

# Remove generated documents
rm -rf output/*

# Remove all generated files
rm -rf screenshots/* output/* temp/*
```

### Reset to clean state

```bash
npm run setup  # Recreates directories
```

## Next Steps

- Read [README.md](README.md) for overview
- Check [INSTALL.md](INSTALL.md) for setup details
- Explore `src/config.js` for customization options
- Try different input methods and URLs

