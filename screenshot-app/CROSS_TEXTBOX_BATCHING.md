# Cross-Text-Box Batching Implementation

## 🎯 Overview

This document explains the **cross-text-box batching** feature that processes URLs from multiple text boxes in batches of 5 URLs (configurable via `maxParallelUrls` setting).

---

## 📊 How It Works

### **Before (Old Behavior):**

- Text Box 1 (7 URLs) → Process ALL 7 URLs → Generate Word doc
- Text Box 2 (8 URLs) → Process ALL 8 URLs → Generate Word doc

### **After (New Behavior):**

- **Batch 1:** Process 5 URLs from Text Box 1
- **Batch 2:** Process 2 URLs from Text Box 1 + 3 URLs from Text Box 2
  - ✅ Text Box 1 complete → Generate Word doc for Text Box 1
- **Batch 3:** Process 5 URLs from Text Box 2
  - ✅ Text Box 2 complete → Generate Word doc for Text Box 2

---

## 🔧 Implementation Details

### **Step 1: Collect URLs with Metadata**

All URLs from all text boxes are collected into a single array with metadata:

```typescript
{
  url: "https://example.com",
  textBoxId: "textbox-123",
  textBoxIndex: 0,
  sessionName: "My Session",
  batchTimeout: 90
}
```

### **Step 2: Create Batches**

URLs are divided into batches of `maxParallelUrls` size (default: 5):

```typescript
const batchSize = maxParallelUrls; // 5
const batches = [];
for (let i = 0; i < allUrls.length; i += batchSize) {
  batches.push(allUrls.slice(i, i + batchSize));
}
```

### **Step 3: Process Batches Sequentially**

Each batch is sent to the backend for processing:

```typescript
for (const batch of batches) {
  const batchUrls = batch.map((item) => item.url);
  const batchTimeout = Math.max(...batch.map((item) => item.batchTimeout));

  // Send to backend
  const response = await fetch("/api/screenshots/capture", {
    method: "POST",
    body: JSON.stringify({
      urls: batchUrls,
      batch_timeout: batchTimeout,
      max_parallel_urls: maxParallelUrls,
      // ... other settings
    }),
  });
}
```

### **Step 4: Track Results Per Text Box**

Results are distributed back to their original text boxes:

```typescript
const textBoxResults = {}; // Track results per text box
const textBoxProcessedCounts = {}; // Track completion

batch.forEach((item, index) => {
  const result = data.results[index];
  textBoxResults[item.textBoxId].push(result);
  textBoxProcessedCounts[item.textBoxId]++;

  // Check if text box is complete
  if (
    textBoxProcessedCounts[item.textBoxId] === textBoxUrlCounts[item.textBoxId]
  ) {
    // Generate Word document for this text box
    await generateWordDocumentForSession(
      item.sessionName,
      textBoxResults[item.textBoxId]
    );
  }
});
```

### **Step 5: Generate Word Documents**

Word documents are generated **only after ALL URLs** in a text box are processed:

```typescript
for (const textBox of validTextBoxes) {
  const results = textBoxResults[textBox.id];
  const successResults = results.filter((r) => r.status === "success");

  if (successResults.length > 0) {
    await generateWordDocumentForSession(textBox.sessionName, successResults);
  }
}
```

---

## 📋 Example Scenario

### **Input:**

- **Text Box 1:** 7 URLs (Session: "Box1", Timeout: 90s)
- **Text Box 2:** 8 URLs (Session: "Box2", Timeout: 120s)
- **Text Box 3:** 6 URLs (Session: "Box3", Timeout: 60s)
- **Batch Size:** 5 URLs

### **Processing:**

```
📦 Batch 1 (5 URLs):
   [TB1-URL1, TB1-URL2, TB1-URL3, TB1-URL4, TB1-URL5]
   Timeout: 90s (from TB1)

📦 Batch 2 (5 URLs):
   [TB1-URL6, TB1-URL7, TB2-URL1, TB2-URL2, TB2-URL3]
   Timeout: 120s (max of 90s and 120s)
   ✅ Text Box 1 complete! → Generate "Box1.docx"

📦 Batch 3 (5 URLs):
   [TB2-URL4, TB2-URL5, TB2-URL6, TB2-URL7, TB2-URL8]
   Timeout: 120s (from TB2)
   ✅ Text Box 2 complete! → Generate "Box2.docx"

📦 Batch 4 (5 URLs):
   [TB3-URL1, TB3-URL2, TB3-URL3, TB3-URL4, TB3-URL5]
   Timeout: 60s (from TB3)

📦 Batch 5 (1 URL):
   [TB3-URL6]
   Timeout: 60s (from TB3)
   ✅ Text Box 3 complete! → Generate "Box3.docx"
```

---

## 🎯 Key Features

### ✅ **Batch Size Control**

- Configurable via `maxParallelUrls` setting (default: 5)
- Prevents overwhelming the system with too many parallel requests

### ✅ **Smart Timeout Handling**

- Each batch uses the **maximum timeout** from all text boxes in that batch
- Ensures no URL times out prematurely

### ✅ **Progress Tracking**

- Real-time progress bar shows overall completion
- Logs show which text boxes are in each batch

### ✅ **Error Handling**

- If a batch fails, all URLs in that batch are marked as failed
- Processing continues with the next batch
- Failed URLs don't prevent Word document generation

### ✅ **Word Document Generation**

- Generated **only after ALL URLs** in a text box are processed
- One Word document per text box
- Only generated if at least one screenshot succeeded

### ✅ **Session Creation**

- One session per text box
- Sessions created after Word document generation
- Stored in Sessions tab for later review

---

## 📊 Logs Example

```
🚀 Starting cross-text-box batch capture for 3 text box(es)
   📦 Batching: 5 URLs per batch across all text boxes

📦 Text Box 1: "Box1" - 7 URLs
📦 Text Box 2: "Box2" - 8 URLs
📦 Text Box 3: "Box3" - 6 URLs

📊 Total URLs across all text boxes: 21
   🔢 Created 5 batches of up to 5 URLs each

⚡ Batch 1/5: Processing 5 URLs
   📝 Text boxes in this batch: Box1
   ⏱️ Batch timeout: 90s
   ✅ Success: 5, ❌ Failed: 0

⚡ Batch 2/5: Processing 5 URLs
   📝 Text boxes in this batch: Box1, Box2
   ⏱️ Batch timeout: 120s
   ✅ Success: 5, ❌ Failed: 0
   ✅ Text Box "Box1" complete! (7/7 URLs)

⚡ Batch 3/5: Processing 5 URLs
   📝 Text boxes in this batch: Box2
   ⏱️ Batch timeout: 120s
   ✅ Success: 5, ❌ Failed: 0
   ✅ Text Box "Box2" complete! (8/8 URLs)

⚡ Batch 4/5: Processing 5 URLs
   📝 Text boxes in this batch: Box3
   ⏱️ Batch timeout: 60s
   ✅ Success: 5, ❌ Failed: 0

⚡ Batch 5/5: Processing 1 URLs
   📝 Text boxes in this batch: Box3
   ⏱️ Batch timeout: 60s
   ✅ Success: 1, ❌ Failed: 0
   ✅ Text Box "Box3" complete! (6/6 URLs)

📄 Generating Word documents...
   📝 Generating document for "Box1" (7 successful screenshots)
   ✅ Document generated: Box1.docx
   📝 Generating document for "Box2" (8 successful screenshots)
   ✅ Document generated: Box2.docx
   📝 Generating document for "Box3" (6 successful screenshots)
   ✅ Document generated: Box3.docx

✅ Cross-text-box batch capture complete!
   📊 Processed 3 text box(es)
   📦 Total batches: 5
   🔗 Total URLs: 21
```

---

## 🔧 Configuration

### **Batch Size**

- **Setting:** "Batch size (URLs processed together)" in Settings tab → Performance Settings
- **Label:** `Batch size (URLs processed together):`
- **Default:** 5 URLs per batch
- **Range:** 1-10 URLs
- **Description:** Controls how many URLs are processed in each batch across all text boxes

### **Batch Timeout**

- **Setting:** Per text box (each text box has its own timeout)
- **Default:** 90 seconds
- **Range:** 10-300 seconds
- **Behavior:** Batch uses **maximum timeout** from all text boxes in that batch

---

## ⚠️ Important Notes

1. **Sequential Processing:** Batches are processed sequentially (one after another), not in parallel
2. **No Parallel Text Boxes:** The `enableParallelTextBoxes` setting is **ignored** in this mode
3. **Backward Compatible:** Existing functionality is preserved (single text box mode still works)
4. **Resource Efficient:** Prevents overwhelming the system with too many parallel requests
5. **Consistent Batch Size:** All batches have exactly `maxParallelUrls` URLs (except the last batch)

---

## 🎯 Benefits

✅ **Predictable Resource Usage:** Always processes exactly 5 URLs at a time  
✅ **Better Control:** Fine-grained control over parallel processing  
✅ **Efficient Batching:** No wasted resources on small batches  
✅ **Smart Timeout:** Uses appropriate timeout for each batch  
✅ **Clear Progress:** Easy to track which text box is being processed  
✅ **Error Resilience:** Failed batches don't stop the entire process

---

## 📝 Code Location

**File:** `screenshot-app/frontend/src/App.tsx`  
**Function:** `handleMultipleTextBoxesCapture()` (lines 3617-3917)  
**Modified:** 2025-11-12

---

## 🚀 Testing

To test the cross-text-box batching:

1. Enable "Open multiple text boxes" in Main tab
2. Add 3 text boxes with different numbers of URLs:
   - Text Box 1: 7 URLs
   - Text Box 2: 8 URLs
   - Text Box 3: 6 URLs
3. Set `maxParallelUrls` to 5 in Settings
4. Click "Capture Screenshots"
5. Check logs to verify batching behavior
6. Verify Word documents are generated for each text box

Expected: 5 batches total, Word docs generated after each text box completes.
