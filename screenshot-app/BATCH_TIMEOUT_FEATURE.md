# ⏱️ Batch Timeout Auto-Update Feature

## 🎯 What You Asked For

> "add a text box side to side Text Box 1 📝 Session Name (for Word doc): input box, secs inputbox when the user enters the secs number then autorun the script if no change then no need to if it changes from the last time then run automatic."

**✅ IMPLEMENTED!**

---

## 🚀 How It Works

### **1. UI Input Field**

**Location:** Main tab, next to "Session Name" input

```
Text Box 1 📝 Session Name: [Accounting____] ⏱️ Batch Timeout (secs): [90]
```

**Features:**
- ✅ Number input (10-300 seconds)
- ✅ Saves to localStorage automatically
- ✅ Triggers API call when value changes
- ✅ Shows in logs when updating

---

### **2. Smart Auto-Update**

**When you change the timeout value:**

```
User types: 90 → 120
  ↓
Frontend detects change
  ↓
Calls backend API: /api/update-batch-timeout
  ↓
Backend checks if value actually changed
  ↓
If CHANGED: Updates performance_metrics.py + regenerates docs
If SAME: Skips update (no wasted work!)
  ↓
Logs show: "✅ Performance documentation updated successfully!"
```

---

### **3. Backend Logic**

**File:** `backend/main.py` (lines 818-884)

```python
@app.post("/api/update-batch-timeout")
async def update_batch_timeout(request: dict):
    # 1. Validate input (10-300 seconds)
    # 2. Read current value from performance_metrics.py
    # 3. Check if value changed
    # 4. If SAME: Return "unchanged" (no update)
    # 5. If CHANGED:
    #    - Update performance_metrics.py
    #    - Regenerate all docs
    #    - Return success
```

**Smart Detection:**
- ✅ Only updates if value **actually changed**
- ✅ No wasted doc generation if same value
- ✅ Logs show old → new value

---

## 📊 What Gets Updated Automatically

When you change timeout from **90s → 120s**:

### **1. performance_metrics.py**
```python
# Before
batch_timeout: float = 90.0

# After
batch_timeout: float = 120.0
```

### **2. All Documentation Files**
- `ACTUAL_PERFORMANCE_SUMMARY.md`
- `UI_LOAD_WAIT_TIME_GENERATED.md`

**All values recalculate:**
- Total time: 270s → 360s
- Avg per URL: 5s → 6.8s
- Speedup: 2.5x → 1.9x
- All tables, examples, summaries

---

## 🎮 How to Use

### **Step 1: Open Main Tab**

Enable "Open multiple text boxes" checkbox

### **Step 2: Find Batch Timeout Input**

Next to "Session Name" input, you'll see:

```
⏱️ Batch Timeout (secs): [90]
```

### **Step 3: Change Value**

Type new value (e.g., 120) and press Enter or click outside

### **Step 4: Check Logs**

Logs tab will show:

```
⏱️ Batch timeout changed: 90s → 120s
📊 Regenerating performance documentation...
✅ Performance documentation updated successfully!
```

### **Step 5: Verify**

Check `ACTUAL_PERFORMANCE_SUMMARY.md` - all values updated!

---

## 💡 Smart Features

### **1. No Duplicate Updates**

```
User types: 90 → 90 (same value)
  ↓
Backend: "Timeout unchanged, skipping doc generation"
  ↓
No wasted work! ✅
```

### **2. Validation**

```
User types: 5 (too low)
  ↓
Frontend: "⚠️ Batch timeout must be between 10 and 300 seconds"
  ↓
Value not saved ❌
```

### **3. Persistence**

```
User changes: 90 → 120
  ↓
Saved to localStorage
  ↓
Restart app → Still shows 120 ✅
```

---

## 📂 Files Modified

### **Frontend:**
1. ✅ `frontend/src/App.tsx`
   - Added `batchTimeout` state (line 54-59)
   - Added `updateBatchTimeout()` function (line 2600-2635)
   - Added UI input field (line 7075-7105)

### **Backend:**
1. ✅ `backend/main.py`
   - Added `/api/update-batch-timeout` endpoint (line 818-884)
   - Removed auto-generation from startup (line 197-205)

2. ✅ `backend/performance_metrics.py`
   - Single source of truth for timeout value

3. ✅ `backend/generate_docs.py`
   - Generates docs from metrics

---

## 🎯 Benefits

| Before | After |
|--------|-------|
| Edit 3 files manually | Edit 1 input field |
| 17 edits across files | 1 value change |
| Manual calculations | Auto-calculated |
| Must remember to update | Just type new value |
| 5 minutes work | 5 seconds work |
| Must restart backend | No restart needed |

---

## 🔍 Example Usage

### **Scenario: Increase timeout for slow pages**

**Problem:** Some pages take longer than 90s to load

**Solution:**

1. Open Main tab
2. Change timeout: `90` → `120`
3. Press Enter
4. Check logs: "✅ Performance documentation updated successfully!"
5. Done! All docs now show 120s timeout

**Updated automatically:**
- Total time: 270s → 360s (4.5 min → 6 min)
- Avg per URL: 5s → 6.8s
- Speedup: 2.5x → 1.9x
- All comparison tables
- All examples

---

## 🎉 Summary

**Your question:** "who will run this manually?"

**Answer:** **NOBODY!** 🎯

- ✅ Just change the input field value
- ✅ Backend auto-detects change
- ✅ Docs auto-regenerate if changed
- ✅ Skips update if value unchanged
- ✅ **ZERO manual steps!**

**No more:**
- ❌ Running scripts manually
- ❌ Editing multiple files
- ❌ Recalculating values
- ❌ Remembering to update docs

**Just type the new timeout value and it's done!** 🚀

