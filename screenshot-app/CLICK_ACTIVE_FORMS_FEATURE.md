# 🎯 Click Active Forms Feature - Advanced Dynamic Action

## 📋 Overview

This feature implements **intelligent, dynamic form clicking** that:
- ✅ Finds **all** forms with a specific name (e.g., "MPI")
- ✅ Checks if each form has a required status (e.g., "Active")
- ✅ Clicks each matching form automatically
- ✅ Auto-scrolls the opened page/modal
- ✅ Navigates back/closes the form
- ✅ Repeats for all matching forms

---

## 🎯 Use Case: Tekion MPVI Settings

### **Problem:**
On the Tekion MPVI Settings page (`https://preprodapp.tekioncloud.com/ro/mpvi-settings/FORMS`), there are multiple inspection forms (MPI, STANDARD, etc.) in a table. Each form has a status (Active, Inactive, etc.). 

**Manual workflow:**
1. Find all "MPI" forms
2. Check if each is "Active" (green indicator)
3. Click each Active MPI
4. Scroll the opened form to see all content
5. Go back
6. Repeat for next Active MPI

**Automated workflow with this feature:**
1. Configure once in `url_click_config.json`
2. Screenshot tool automatically handles all steps
3. All Active MPI forms are clicked, scrolled, and captured

---

## 🔧 Configuration

### **File:** `screenshot-app/backend/url_click_config.json`

```json
{
  "id": "tekion-mpvi-forms-active-mpi",
  "name": "Tekion MPVI Settings - Click All Active MPI Forms",
  "url_pattern": "https://preprodapp.tekioncloud.com/ro/mpvi-settings/FORMS",
  "match_type": "exact",
  "actions": [
    {
      "type": "click_active_forms",
      "form_name": "MPI",
      "status_required": "Active",
      "scroll_opened_page": true,
      "close_after_scroll": true,
      "wait_after_click_ms": 2000,
      "wait_after_scroll_ms": 1000,
      "description": "Dynamically finds all Active MPI forms, clicks each, scrolls the opened page, and navigates back"
    }
  ],
  "enabled": true
}
```

---

## 📊 Action Parameters

### **Required Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `type` | string | Must be `"click_active_forms"` | `"click_active_forms"` |
| `form_name` | string | Name of the form to find | `"MPI"` |

### **Optional Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status_required` | string | `"Active"` | Required status text or indicator | `"Active"` |
| `scroll_opened_page` | boolean | `true` | Scroll the opened form/modal | `true` |
| `close_after_scroll` | boolean | `true` | Close/go back after scrolling | `true` |
| `wait_after_click_ms` | integer | `2000` | Wait time after clicking (ms) | `2000` |
| `wait_after_scroll_ms` | integer | `1000` | Wait time after scrolling (ms) | `1000` |
| `description` | string | `""` | Human-readable description | `"Click all Active MPIs"` |

---

## 🔍 How It Works

### **Step 1: Find All Matching Forms**

The JavaScript code searches the DOM for all table rows (`[role="row"]`) and:
1. Checks the first cell for form name (e.g., "MPI")
2. Checks other cells for status text or green indicator
3. Collects all rows that match both criteria

**HTML Structure Detected:**
```html
<div role="row">
  <div role="gridcell">
    <div class="root_content_blackNormalContent__9js3j3JV6N">MPI</div>
  </div>
  <div role="gridcell">
    <div class="root_statusRenderer_container__dpHKiWAuPE">
      <div class="root_statusRenderer_statusIcon__beFL1mPjCr root_statusRenderer_green__nYQ6xRCozZ"></div>
      <div class="root_label_label__fPnKtiGtmC">Active</div>
    </div>
  </div>
</div>
```

### **Step 2: Click Each Form**

For each matching form:
1. Click the row (or first cell if row click fails)
2. Wait for page/modal to load (`wait_after_click_ms`)

### **Step 3: Scroll Opened Content**

If `scroll_opened_page: true`:
1. Calls `_scroll_all_nested_elements()` to scroll all scrollable content
2. Waits for content to load (`wait_after_scroll_ms`)

### **Step 4: Navigate Back**

If `close_after_scroll: true`:
1. Tries to find and click close button (X, Close, Cancel, etc.)
2. Falls back to browser back navigation if no close button found
3. Waits for page to settle (1 second)

### **Step 5: Repeat**

Continues to next matching form until all are processed.

---

## 📝 Expected Log Output

### **When Forms Are Found:**

```log
📋 Found saved configuration: 'Tekion MPVI Settings - Click All Active MPI Forms'
   🎯 Action 1/1: Click Active Forms
      ℹ️  Dynamically finds all Active MPI forms, clicks each, scrolls the opened page, and navigates back
🎯 Finding all 'MPI' forms with status 'Active'...
   ✅ Found 3 matching form(s):
      1. MPI - Active
      2. MPI - Active
      3. MPI - Active

   🔄 Processing form 1/3: MPI
      ✅ Clicked: MPI
      📜 Scrolling opened form...
      🔄 Scrolling all nested scrollable elements...
      ✅ Scrolled 2 nested elements to bottom:
         - <DIV> class='scrollable-content' (450px scrolled, 810px total)
         - <DIV> class='form-body' (200px scrolled, 400px total)
      ✅ Nested elements scrolled, content loaded
      ⬅️  Navigating back...
      ✅ Closed form (close_button)

   🔄 Processing form 2/3: MPI
      ✅ Clicked: MPI
      📜 Scrolling opened form...
      ...

   ✅ Processed 3 form(s) successfully
   ✅ All configured actions completed
```

### **When No Forms Are Found:**

```log
🎯 Finding all 'MPI' forms with status 'Active'...
   ℹ️  No 'MPI' forms found with status 'Active'
   ✅ All configured actions completed
```

---

## 🚀 Testing Instructions

### **1. Restart Backend**

The backend needs to reload the new configuration:

```bash
cd screenshot-app/backend
python3 main.py
```

### **2. Test with Screenshot Tool**

1. Open the app at http://localhost:1420
2. Enter URL: `https://preprodapp.tekioncloud.com/ro/mpvi-settings/FORMS`
3. Enable "Use Real Browser" (to use your logged-in Chrome)
4. Click "Take Screenshot"

### **3. Check Logs**

Watch the terminal for:
- ✅ Configuration loaded
- ✅ Forms found
- ✅ Each form clicked
- ✅ Scrolling performed
- ✅ Navigation back

---

## 🎨 Customization Examples

### **Example 1: Click All Active Forms (Any Type)**

```json
{
  "type": "click_active_forms",
  "form_name": "",
  "status_required": "Active",
  "description": "Click all forms with Active status"
}
```

### **Example 2: Click STANDARD Forms (No Scrolling)**

```json
{
  "type": "click_active_forms",
  "form_name": "STANDARD",
  "status_required": "Active",
  "scroll_opened_page": false,
  "close_after_scroll": false,
  "description": "Click STANDARD forms but don't scroll or close"
}
```

### **Example 3: Click Inactive MPIs**

```json
{
  "type": "click_active_forms",
  "form_name": "MPI",
  "status_required": "Inactive",
  "description": "Click all Inactive MPI forms"
}
```

---

## 🔧 Technical Implementation

### **New Method:** `_click_active_forms()`

**Location:** `screenshot-app/backend/screenshot_service.py` (lines 4788-4988)

**Key Features:**
- Dynamic form detection using DOM traversal
- Status verification (text or CSS class)
- Robust clicking (tries row, then cell)
- Multiple close methods (button, browser back)
- Detailed logging for debugging

### **Integration Point:**

**Location:** `screenshot-app/backend/screenshot_service.py` (lines 3851-3898)

The action handler checks for `action_type == "click_active_forms"` and calls the new method with all parameters.

---

## ⚠️ Troubleshooting

### **Issue 1: Forms Not Found**

**Symptoms:** Log shows "No 'MPI' forms found"

**Solutions:**
- Check if form name is exact match (case-sensitive)
- Verify the page has loaded completely
- Check if table structure matches expected HTML

### **Issue 2: Click Fails**

**Symptoms:** Log shows "Failed to click"

**Solutions:**
- Increase `wait_after_click_ms` to allow more time for page load
- Check if form row is visible and clickable
- Verify no overlays or modals are blocking the click

### **Issue 3: Can't Navigate Back**

**Symptoms:** Log shows "Could not navigate back automatically"

**Solutions:**
- Set `close_after_scroll: false` to skip navigation
- Manually add a close button selector
- Check if modal has a different close mechanism

---

## 💡 Best Practices

1. **Test with one form first:** Set `form_name` to a specific form to test the workflow
2. **Adjust wait times:** Increase `wait_after_click_ms` if forms load slowly
3. **Check logs:** Always review logs to see what was found and clicked
4. **Use descriptive names:** Add clear `description` for debugging
5. **Disable when not needed:** Set `enabled: false` to temporarily disable

---

## 🎯 Summary

### **What's New:**
- 🆕 New action type: `"click_active_forms"`
- 🆕 Dynamic form detection
- 🆕 Status verification (Active/Inactive)
- 🆕 Auto-scroll opened forms
- 🆕 Auto-navigate back
- 🆕 Process multiple forms in sequence

### **Benefits:**
- ✅ Fully automated form clicking
- ✅ No manual intervention needed
- ✅ Captures all Active forms
- ✅ Works with any form type
- ✅ Configurable per URL

---

**The feature is now live and ready to use!** 🎉

