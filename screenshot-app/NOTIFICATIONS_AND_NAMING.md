# 🔔 Notifications & Naming Convention

## Features Implemented

### 1. Browser Notifications ✅

**When capturing 1 URL:**
- ✅ Shows notification immediately when screenshot is captured
- 📸 Title: "Screenshot Captured"
- 📝 Body: "Screenshot captured successfully for [URL]"

**When capturing multiple URLs:**
- ✅ Shows notification when ALL screenshots are captured
- 📸 Title: "Screenshots Captured"
- 📝 Body: "X of Y screenshots captured successfully"

---

## Implementation Details

### Notification Permission

**Auto-request on app load:**
```typescript
React.useEffect(() => {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }
}, []);
```

**When it triggers:**
- ✅ First time user opens the app
- ✅ Browser shows permission dialog
- ✅ User clicks "Allow" or "Block"
- ✅ Permission is saved for future sessions

---

### Notification Helper

```typescript
const showNotification = (title: string, body: string) => {
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, {
      body: body,
      icon: '/favicon.ico',
    });
  }
};
```

**Features:**
- ✅ Checks if notifications are supported
- ✅ Checks if permission is granted
- ✅ Shows notification with title, body, and icon
- ✅ Works even when app is in background

---

### Notification Logic

**Single URL (1 URL):**
```typescript
if (urlList.length === 1 && successCount === 1) {
  showNotification(
    '📸 Screenshot Captured',
    `Screenshot captured successfully for ${urlList[0]}`
  );
}
```

**Multiple URLs (2+ URLs):**
```typescript
else if (urlList.length > 1 && successCount > 0) {
  showNotification(
    '📸 Screenshots Captured',
    `${successCount} of ${urlList.length} screenshots captured successfully`
  );
}
```

---

## 2. Word Document Naming Convention ✅

### Naming Logic

**Uses the same naming as screenshots:**
- ✅ Takes first screenshot filename
- ✅ Removes segment numbers (_001, _002, etc.)
- ✅ Removes .png extension
- ✅ Adds .docx extension

### Examples

**Single Screenshot:**
```
Screenshot: Accounting_AutoPostingSettings.png
Document:   Accounting_AutoPostingSettings.docx
```

**Multiple Segments:**
```
Screenshots: Accounting_AutoPostingSettings_001.png
             Accounting_AutoPostingSettings_002.png
             Accounting_AutoPostingSettings_003.png
Document:    Accounting_AutoPostingSettings.docx
```

**Multiple URLs:**
```
Screenshots: Accounting_AutoPostingSettings.png
             Scheduling_General.png
             Parts_Inventory.png
Document:    Accounting_AutoPostingSettings.docx (uses first screenshot name)
```

---

### Implementation

```typescript
// Generate document name from first screenshot filename
const firstScreenshot = successfulScreenshots[0];
const firstFilename = firstScreenshot.split("/").pop() || "screenshots_report";
const documentName = firstFilename
  .replace(/_\d{3}\.png$/, "") // Remove _001.png, _002.png, etc.
  .replace(/\.png$/, "")       // Remove .png
  + ".docx";

// Output path
output_path: `~/Desktop/ARC DEALERS SCREENSHOT WORD DOCS/${documentName}`
```

---

## Naming Convention Reference

### Screenshot Naming (PascalCase)

**Format:** `Module_Feature.png` or `Module_Feature_001.png`

**Rules:**
1. ✅ PascalCase: Each word starts with capital letter
2. ✅ Underscore separator: Separates logical modules
3. ✅ Segment numbers: _001, _002, _003 for multiple segments
4. ✅ .png extension: All screenshots are PNG

**Examples:**
- `Accounting_AutoPostingSettings.png`
- `Scheduling_General.png`
- `Parts_Inventory_001.png`
- `Parts_Inventory_002.png`

---

### Word Document Naming (Same as Screenshots)

**Format:** `Module_Feature.docx`

**Rules:**
1. ✅ Same base name as screenshots
2. ✅ No segment numbers (even if screenshots have them)
3. ✅ .docx extension: Word document format

**Examples:**
- `Accounting_AutoPostingSettings.docx`
- `Scheduling_General.docx`
- `Parts_Inventory.docx`

---

### Base URL & Words to Remove

**Settings:**
- **Base URL**: `https://example.com/`
- **Words to Remove**: `dse-v2, api, v1` (comma-separated)

**Example:**
```
URL:        https://example.com/dse-v2/scheduling/general
Base URL:   https://example.com/
Path:       dse-v2/scheduling/general
Remove:     dse-v2
Result:     scheduling/general
Filename:   Scheduling_General.png
Document:   Scheduling_General.docx
```

---

## User Experience

### Notification Flow

**Single URL:**
```
1. User enters 1 URL
2. User clicks "Capture Screenshots"
3. Tool captures screenshot
4. ✅ Notification appears: "Screenshot Captured"
5. User sees notification even if app is in background
```

**Multiple URLs:**
```
1. User enters 5 URLs
2. User clicks "Capture Screenshots"
3. Tool captures all 5 screenshots
4. ✅ Notification appears: "5 of 5 screenshots captured successfully"
5. User sees notification even if app is in background
```

---

### Document Generation Flow

**Before:**
```
1. User clicks "Generate Word Document"
2. Document saved as: screenshots_report.docx
3. User has to rename manually
```

**After:**
```
1. User clicks "Generate Word Document"
2. Document saved as: Accounting_AutoPostingSettings.docx
3. ✅ Name matches screenshot name automatically!
```

---

## File Locations

### Screenshots
```
/Users/tlreddy/Documents/project 1/screenshot-app/screenshots/
├── Accounting_AutoPostingSettings.png
├── Scheduling_General_001.png
├── Scheduling_General_002.png
└── Parts_Inventory.png
```

### Word Documents
```
/Users/tlreddy/Desktop/ARC DEALERS SCREENSHOT WORD DOCS/
├── Accounting_AutoPostingSettings.docx
├── Scheduling_General.docx
└── Parts_Inventory.docx
```

---

## Browser Compatibility

### Notifications
- ✅ Chrome/Edge: Full support
- ✅ Firefox: Full support
- ✅ Safari: Full support (macOS 10.14+)
- ❌ IE: Not supported (but who uses IE?)

### Permission States
- **default**: Not asked yet (will ask on first load)
- **granted**: User allowed notifications
- **denied**: User blocked notifications

---

## Summary

### What Was Added

1. ✅ **Browser notifications** for screenshot capture
   - Single URL: Notify immediately
   - Multiple URLs: Notify when all done

2. ✅ **Smart document naming** based on screenshot names
   - Uses first screenshot name
   - Removes segment numbers
   - Matches screenshot naming convention

3. ✅ **Notification permission** auto-request on app load

4. ✅ **Background notifications** work even when app is minimized

### Status

✅ **IMPLEMENTED**
✅ **READY TO TEST**

**Now you'll get notifications when screenshots are captured, and Word documents will have the same names as your screenshots!** 🎉


