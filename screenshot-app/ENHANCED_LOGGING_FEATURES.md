# Enhanced Real-Time Logging Features

**Date:** November 12, 2025  
**Feature:** Real-time monitoring in Log Output section

---

## 🎯 **Overview**

Enhanced the screenshot tool's frontend Log Output section to provide **comprehensive real-time monitoring** during the capture process. This allows you to:

1. **Track URL processing times** - See exactly how long each URL takes
2. **Detect timeout warnings** - Get alerts when URLs approach timeout thresholds
3. **Monitor batch progress** - Track which batch is running and overall progress
4. **Identify problematic URLs** - Spot slow or failing URLs immediately

---

## ✨ **New Features**

### **1. Detailed Batch Information**

**Before:**
```
⚡ Batch 1/10: Processing 5 URLs
```

**After:**
```
⚡ Batch 1/10: Processing 5 URLs
   📝 Text boxes in this batch: Accounting, Parts
   ⏱️ Batch timeout: 240s (120s per URL)
   📋 URLs in this batch:
      1. https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=...
      2. https://preprodapp.tekioncloud.com/accounting/accountPayable
      3. https://preprodapp.tekioncloud.com/parts/parts-settings/pdf-configuration
      4. https://preprodapp.tekioncloud.com/parts/void-reasons
      5. https://preprodapp.tekioncloud.com/ro/opcode
   🚀 Sending batch to backend...
```

**Benefits:**
- See exactly which URLs are being processed
- Know the timeout limits upfront
- Understand which text boxes are involved

---

### **2. Per-URL Processing Time & Results**

**Before:**
```
   ✅ Success: 4, ❌ Failed: 1
```

**After:**
```
   ⏱️ Batch completed in 187.3s
   📊 Per-URL Results:
      ✅ https://preprodapp.tekioncloud.com/accounting/glaccountmapping... (45.2s, 1 screenshot)
      ✅ https://preprodapp.tekioncloud.com/accounting/accountPayable (67.8s, 3 screenshots)
      ✅ https://preprodapp.tekioncloud.com/parts/parts-settings/pdf-c... (52.1s, 1 screenshot)
      ❌ https://preprodapp.tekioncloud.com/parts/void-reasons - Screenshot capture timed out after 120.0s (real browser mode)
      ✅ https://preprodapp.tekioncloud.com/ro/opcode (22.4s, 1 screenshot)
   📈 Batch Summary: ✅ 4 succeeded, ❌ 1 failed
```

**Benefits:**
- See exactly how long each URL took to process
- Identify which URLs are slow (approaching timeout)
- See how many screenshots were captured per URL
- Get detailed error messages for failures

---

### **3. Timeout Warnings**

**New Feature:**
```
   ⚠️ Warning: 2 URL(s) took >80% of timeout (96s)
      ⏱️ https://preprodapp.tekioncloud.com/accounting/accountPayable took 115.7s
      ⏱️ https://preprodapp.tekioncloud.com/parts/parts-settings/pdf-c... took 108.3s
```

**Benefits:**
- Get early warnings when URLs are approaching timeout
- Identify URLs that need longer timeout settings
- Proactively adjust settings before failures occur

**Threshold:** URLs taking >80% of the per-URL timeout are flagged

---

### **4. Overall Progress Tracking**

**New Feature:**
```
   📊 Overall Progress: 25/175 URLs (14.3%)
```

**Benefits:**
- See total progress across all text boxes
- Estimate remaining time
- Track completion percentage

**Updates:** After every batch completes

---

### **5. Batch Timing**

**New Feature:**
```
   ⏱️ Batch completed in 187.3s
```

**Benefits:**
- See actual batch processing time
- Compare against batch timeout setting
- Identify if batches are completing efficiently

---

## 🔧 **Technical Implementation**

### **Frontend Changes (App.tsx)**

1. **Added batch start time tracking:**
   ```typescript
   const batchStartTime = Date.now();
   ```

2. **Enhanced batch logging:**
   - List all URLs in batch
   - Show per-URL timeout calculation
   - Display text boxes involved

3. **Added per-URL result logging:**
   - Processing time for each URL
   - Screenshot count
   - Detailed error messages

4. **Added timeout warnings:**
   - Detect URLs >80% of timeout
   - List slow URLs with times

5. **Added overall progress tracking:**
   - Calculate total processed vs total URLs
   - Show percentage complete

### **Backend Changes (main.py)**

1. **Added `processing_time` field to `ScreenshotResult` model:**
   ```python
   processing_time: Optional[float] = None  # Time in seconds
   ```

2. **Track timing in `_capture_single_url` function:**
   ```python
   url_start_time = datetime.now()
   # ... capture logic ...
   url_end_time = datetime.now()
   processing_time = (url_end_time - url_start_time).total_seconds()
   ```

3. **Include processing time in all result types:**
   - Success results
   - Error results
   - Cancelled results
   - Timeout results

---

## 📊 **Example Log Output**

Here's what you'll see in the Log Output section during a capture:

```
⚡ Batch 1/35: Processing 5 URLs
   📝 Text boxes in this batch: Clark Chevrolet Buick GMC- 7117
   ⏱️ Batch timeout: 240s (120s per URL)
   📋 URLs in this batch:
      1. https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=...
      2. https://preprodapp.tekioncloud.com/accounting/accountPayable
      3. https://preprodapp.tekioncloud.com/accounting/accountReceivable/setup
      4. https://preprodapp.tekioncloud.com/accounting/accountSettings
      5. https://preprodapp.tekioncloud.com/accounting/autoPostingSettings
   🚀 Sending batch to backend...
   ⏱️ Batch completed in 234.7s
   📊 Per-URL Results:
      ✅ https://preprodapp.tekioncloud.com/accounting/glaccountmapping... (78.3s, 1 screenshot)
      ✅ https://preprodapp.tekioncloud.com/accounting/accountPayable (112.5s, 3 screenshots)
      ❌ https://preprodapp.tekioncloud.com/accounting/accountReceivable... - Screenshot capture timed out after 120.0s (real browser mode)
      ✅ https://preprodapp.tekioncloud.com/accounting/accountSettings (43.9s, 1 screenshot)
      ✅ https://preprodapp.tekioncloud.com/accounting/autoPostingSettings (56.2s, 1 screenshot)
   📈 Batch Summary: ✅ 4 succeeded, ❌ 1 failed
   ⚠️ Warning: 1 URL(s) took >80% of timeout (96s)
      ⏱️ https://preprodapp.tekioncloud.com/accounting/accountPayable took 112.5s
   📊 Overall Progress: 5/175 URLs (2.9%)

⚡ Batch 2/35: Processing 5 URLs
   📝 Text boxes in this batch: Clark Chevrolet Buick GMC- 7117
   ⏱️ Batch timeout: 240s (120s per URL)
   📋 URLs in this batch:
      1. https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=...
      2. https://preprodapp.tekioncloud.com/accounting/journalMapping/list
      3. https://preprodapp.tekioncloud.com/accounting/setupFields
      4. https://preprodapp.tekioncloud.com/core/cashiering-settings
      5. https://preprodapp.tekioncloud.com/core/coupons
   🚀 Sending batch to backend...
   ⏱️ Batch completed in 198.4s
   📊 Per-URL Results:
      ✅ https://preprodapp.tekioncloud.com/accounting/glaccountmapping... (67.2s, 1 screenshot)
      ✅ https://preprodapp.tekioncloud.com/accounting/journalMapping/list (45.8s, 1 screenshot)
      ✅ https://preprodapp.tekioncloud.com/accounting/setupFields (38.1s, 1 screenshot)
      ✅ https://preprodapp.tekioncloud.com/core/cashiering-settings (24.7s, 1 screenshot)
      ✅ https://preprodapp.tekioncloud.com/core/coupons (22.6s, 1 screenshot)
   📈 Batch Summary: ✅ 5 succeeded, ❌ 0 failed
   📊 Overall Progress: 10/175 URLs (5.7%)
```

---

## 🎯 **How to Use**

### **1. Monitor Processing Times**

Watch the **Per-URL Results** section to see how long each URL takes:
- URLs taking **<60s** are fast ✅
- URLs taking **60-90s** are moderate ⚠️
- URLs taking **>90s** are slow 🔴

### **2. Watch for Timeout Warnings**

If you see:
```
⚠️ Warning: 3 URL(s) took >80% of timeout (96s)
```

**Action:** Consider increasing the batch timeout setting to give these URLs more time.

### **3. Track Overall Progress**

Use the **Overall Progress** line to estimate completion:
```
📊 Overall Progress: 50/175 URLs (28.6%)
```

**Calculation:** (50 URLs processed / 175 total) × 100 = 28.6%

### **4. Identify Problematic URLs**

Look for URLs that consistently fail or take too long:
```
❌ https://preprodapp.tekioncloud.com/accounting/accountReceivable... - Screenshot capture timed out after 120.0s
```

**Action:** 
- Increase timeout for these specific URLs
- Check if the page has issues (slow loading, errors)
- Consider capturing these URLs separately with higher timeout

---

## 📈 **Benefits**

1. **Early Problem Detection** - Spot issues immediately, not after all batches complete
2. **Informed Decisions** - Adjust timeout settings based on real data
3. **Better Debugging** - Detailed error messages help troubleshoot failures
4. **Progress Visibility** - Know exactly where you are in the capture process
5. **Performance Insights** - Identify slow URLs and optimize settings

---

## 🔄 **Compatibility**

- ✅ Works with **Real Browser Mode**
- ✅ Works with **Headless Mode**
- ✅ Works with **Cross-Text-Box Batching**
- ✅ Works with **Segmented Capture Mode**
- ✅ Backward compatible (no breaking changes)

---

## 📝 **Notes**

- Processing times include **all steps**: page load, network idle, clicks, screenshot capture, quality check
- Timeout warnings use **80% threshold** to give early warning before actual timeout
- Overall progress updates **after each batch completes**
- Log messages are **timestamped** for easy correlation with backend logs

---

**End of Documentation**

