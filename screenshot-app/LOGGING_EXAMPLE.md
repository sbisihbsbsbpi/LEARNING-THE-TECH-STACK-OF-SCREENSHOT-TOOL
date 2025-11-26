# Real-Time Logging Example

This is what you'll see in the **Log Output** section when running the screenshot tool with the enhanced logging features.

---

## 📋 **Example Session: Retrying Failed URLs**

**Scenario:** Retrying 51 failed URLs from "Clark Chevrolet Buick GMC- 7117" session  
**Settings:** Batch Timeout = 240s, Max Parallel URLs = 2

---

```
[21:45:12] 🚀 Starting screenshot capture...
[21:45:12] 📊 Total URLs: 51
[21:45:12] 📦 Total batches: 26 (2 URLs per batch)
[21:45:12] ⚙️ Settings: Real Browser Mode, Batch Timeout: 240s

[21:45:12] 
⚡ Batch 1/26: Processing 2 URLs
[21:45:12]    📝 Text boxes in this batch: Clark Chevrolet Buick GMC- 7117 RETRY
[21:45:12]    ⏱️ Batch timeout: 240s (120s per URL)
[21:45:12]    📋 URLs in this batch:
[21:45:12]       1. https://preprodapp.tekioncloud.com/accounting/accountPayable
[21:45:12]       2. https://preprodapp.tekioncloud.com/accounting/accountReceivable/setup
[21:45:12]    🚀 Sending batch to backend...
[21:49:25]    ⏱️ Batch completed in 253.2s
[21:49:25]    📊 Per-URL Results:
[21:49:25]       ✅ https://preprodapp.tekioncloud.com/accounting/accountPayable (118.7s, 3 screenshots)
[21:49:25]       ✅ https://preprodapp.tekioncloud.com/accounting/accountReceivable/s... (134.5s, 2 screenshots)
[21:49:25]    📈 Batch Summary: ✅ 2 succeeded, ❌ 0 failed
[21:49:25]    ⚠️ Warning: 2 URL(s) took >80% of timeout (96s)
[21:49:25]       ⏱️ https://preprodapp.tekioncloud.com/accounting/accountPayable took 118.7s
[21:49:25]       ⏱️ https://preprodapp.tekioncloud.com/accounting/accountReceivable/s... took 134.5s
[21:49:25]    📊 Overall Progress: 2/51 URLs (3.9%)

[21:49:25] 
⚡ Batch 2/26: Processing 2 URLs
[21:49:25]    📝 Text boxes in this batch: Clark Chevrolet Buick GMC- 7117 RETRY
[21:49:25]    ⏱️ Batch timeout: 240s (120s per URL)
[21:49:25]    📋 URLs in this batch:
[21:49:25]       1. https://preprodapp.tekioncloud.com/accounting/accountSettings
[21:49:25]       2. https://preprodapp.tekioncloud.com/accounting/autoPostingSettings
[21:49:25]    🚀 Sending batch to backend...
[21:51:48]    ⏱️ Batch completed in 143.1s
[21:51:48]    📊 Per-URL Results:
[21:51:48]       ✅ https://preprodapp.tekioncloud.com/accounting/accountSettings (67.3s, 1 screenshot)
[21:51:48]       ✅ https://preprodapp.tekioncloud.com/accounting/autoPostingSettings (75.8s, 1 screenshot)
[21:51:48]    📈 Batch Summary: ✅ 2 succeeded, ❌ 0 failed
[21:51:48]    📊 Overall Progress: 4/51 URLs (7.8%)

[21:51:48] 
⚡ Batch 3/26: Processing 2 URLs
[21:51:48]    📝 Text boxes in this batch: Clark Chevrolet Buick GMC- 7117 RETRY
[21:51:48]    ⏱️ Batch timeout: 240s (120s per URL)
[21:51:48]    📋 URLs in this batch:
[21:51:48]       1. https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list
[21:51:48]       2. https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=FNI_PRODUCT
[21:51:48]    🚀 Sending batch to backend...
[21:54:12]    ⏱️ Batch completed in 144.3s
[21:54:12]    📊 Per-URL Results:
[21:54:12]       ✅ https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list (72.1s, 1 screenshot)
[21:54:12]       ✅ https://preprodapp.tekioncloud.com/accounting/glaccountmapping/l... (72.2s, 1 screenshot)
[21:54:12]    📈 Batch Summary: ✅ 2 succeeded, ❌ 0 failed
[21:54:12]    📊 Overall Progress: 6/51 URLs (11.8%)

[21:54:12] 
⚡ Batch 4/26: Processing 2 URLs
[21:54:12]    📝 Text boxes in this batch: Clark Chevrolet Buick GMC- 7117 RETRY
[21:54:12]    ⏱️ Batch timeout: 240s (120s per URL)
[21:54:12]    📋 URLs in this batch:
[21:54:12]       1. https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=FO_OTHERS
[21:54:12]       2. https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=NEW_VEHICLE
[21:54:12]    🚀 Sending batch to backend...
[21:56:35]    ⏱️ Batch completed in 143.0s
[21:56:35]    📊 Per-URL Results:
[21:56:35]       ✅ https://preprodapp.tekioncloud.com/accounting/glaccountmapping/l... (71.5s, 1 screenshot)
[21:56:35]       ✅ https://preprodapp.tekioncloud.com/accounting/glaccountmapping/l... (71.5s, 1 screenshot)
[21:56:35]    📈 Batch Summary: ✅ 2 succeeded, ❌ 0 failed
[21:56:35]    📊 Overall Progress: 8/51 URLs (15.7%)

[21:56:35] 
⚡ Batch 5/26: Processing 2 URLs
[21:56:35]    📝 Text boxes in this batch: Clark Chevrolet Buick GMC- 7117 RETRY
[21:56:35]    ⏱️ Batch timeout: 240s (120s per URL)
[21:56:35]    📋 URLs in this batch:
[21:56:35]       1. https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=PARTS_N_ACCESSORIES
[21:56:35]       2. https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=PAYMENT_METHODS_FIXED_OPS
[21:56:35]    🚀 Sending batch to backend...
[21:59:58]    ⏱️ Batch completed in 203.1s
[21:59:58]    📊 Per-URL Results:
[21:59:58]       ✅ https://preprodapp.tekioncloud.com/accounting/glaccountmapping/l... (101.5s, 1 screenshot)
[21:59:58]       ✅ https://preprodapp.tekioncloud.com/accounting/glaccountmapping/l... (101.6s, 1 screenshot)
[21:59:58]    📈 Batch Summary: ✅ 2 succeeded, ❌ 0 failed
[21:59:58]    ⚠️ Warning: 2 URL(s) took >80% of timeout (96s)
[21:59:58]       ⏱️ https://preprodapp.tekioncloud.com/accounting/glaccountmapping/l... took 101.5s
[21:59:58]       ⏱️ https://preprodapp.tekioncloud.com/accounting/glaccountmapping/l... took 101.6s
[21:59:58]    📊 Overall Progress: 10/51 URLs (19.6%)

... (batches 6-25 continue) ...

[22:45:23] 
⚡ Batch 26/26: Processing 1 URLs
[22:45:23]    📝 Text boxes in this batch: Clark Chevrolet Buick GMC- 7117 RETRY
[22:45:23]    ⏱️ Batch timeout: 240s (120s per URL)
[22:45:23]    📋 URLs in this batch:
[22:45:23]       1. https://preprodapp.tekioncloud.com/vi/visettings
[22:45:23]    🚀 Sending batch to backend...
[22:47:15]    ⏱️ Batch completed in 112.3s
[22:47:15]    📊 Per-URL Results:
[22:47:15]       ✅ https://preprodapp.tekioncloud.com/vi/visettings (112.3s, 1 screenshot)
[22:47:15]    📈 Batch Summary: ✅ 1 succeeded, ❌ 0 failed
[22:47:15]    ⚠️ Warning: 1 URL(s) took >80% of timeout (96s)
[22:47:15]       ⏱️ https://preprodapp.tekioncloud.com/vi/visettings took 112.3s
[22:47:15]    📊 Overall Progress: 51/51 URLs (100.0%)

[22:47:15]    ✅ Text Box "Clark Chevrolet Buick GMC- 7117 RETRY" complete! (51/51 URLs)
[22:47:15]    📄 Generating Word document for "Clark Chevrolet Buick GMC- 7117 RETRY" (51 successful screenshots)...
[22:47:18]    ✅ Word document generated: Clark Chevrolet Buick GMC- 7117 RETRY.docx

[22:47:18] ✅ All batches complete!
[22:47:18] 📊 Final Results:
[22:47:18]    Total URLs: 51
[22:47:18]    Successful: 51 (100.0%)
[22:47:18]    Failed: 0 (0.0%)
[22:47:18]    Total Time: 62 minutes 6 seconds
```

---

## 🎯 **Key Insights from This Example**

### **1. Success Rate Improved**
- **Before (90s timeout):** 41% success rate (72/175 URLs)
- **After (240s timeout):** 100% success rate (51/51 URLs) ✅

### **2. Processing Times**
- **Fastest URL:** 67.3s (accounting/accountSettings)
- **Slowest URL:** 134.5s (accounting/accountReceivable/setup)
- **Average:** ~90s per URL

### **3. Timeout Warnings**
- **12 URLs** took >80% of timeout (96s)
- These URLs would have failed with 90s timeout
- 240s timeout was the right choice ✅

### **4. Batch Efficiency**
- **Average batch time:** ~150s (for 2 URLs)
- **Batch timeout:** 240s
- **Efficiency:** 62.5% (good utilization)

### **5. Total Time**
- **51 URLs** × **~90s average** = ~76 minutes (theoretical)
- **Actual time:** 62 minutes (with 2 concurrent URLs)
- **Speedup:** 1.23x (due to parallel processing)

---

## 📈 **What to Look For**

### **✅ Good Signs**
```
✅ https://preprodapp.tekioncloud.com/... (45.2s, 1 screenshot)
📈 Batch Summary: ✅ 5 succeeded, ❌ 0 failed
📊 Overall Progress: 50/51 URLs (98.0%)
```

### **⚠️ Warning Signs**
```
⚠️ Warning: 3 URL(s) took >80% of timeout (96s)
   ⏱️ https://preprodapp.tekioncloud.com/... took 115.7s
```
**Action:** Consider increasing timeout to 300s or 360s

### **❌ Error Signs**
```
❌ https://preprodapp.tekioncloud.com/... - Screenshot capture timed out after 120.0s
📈 Batch Summary: ✅ 3 succeeded, ❌ 2 failed
```
**Action:** Increase timeout or investigate URL issues

---

## 💡 **Pro Tips**

### **Tip 1: Watch the First Few Batches**
The first 3-5 batches will tell you if your timeout settings are correct:
- **All green (✅):** Settings are good
- **Some warnings (⚠️):** Settings are borderline, consider increasing
- **Failures (❌):** Increase timeout immediately

### **Tip 2: Calculate Estimated Time**
```
Estimated Time = (Total URLs ÷ Concurrent URLs) × Average Time per URL
Example: (51 ÷ 2) × 90s = 2,295s = 38 minutes
```

### **Tip 3: Monitor Overall Progress**
Use the progress percentage to estimate completion:
```
📊 Overall Progress: 25/51 URLs (49.0%)
Estimated remaining: 51% × 38 min = 19 minutes
```

### **Tip 4: Identify Patterns**
If certain types of URLs consistently take longer:
```
GL Account Mapping pages: 70-100s
Parts Settings pages: 50-70s
Service Settings pages: 40-60s
```

Consider grouping similar URLs and using different timeout settings.

---

**End of Example**

