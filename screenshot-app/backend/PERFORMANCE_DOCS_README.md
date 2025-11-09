# 📊 Performance Documentation System

## 🎯 Problem Solved

**Before:** Changing "60 seconds" to "90 seconds" required:
- ❌ 17 manual edits across 3 files
- ❌ Manual recalculation of totals, averages, speedups
- ❌ Error-prone and time-consuming

**After:** Change ONE value, everything updates automatically!
- ✅ Edit 1 line in `performance_metrics.py`
- ✅ Restart backend (or run script manually)
- ✅ All docs regenerate with correct calculations

---

## 🚀 How It Works

### **1. Single Source of Truth**

**File:** `backend/performance_metrics.py`

```python
@dataclass
class PerformanceMetrics:
    # ===== Batch Configuration =====
    batch_1_urls: int = 18
    batch_2_urls: int = 19
    batch_3_urls: int = 16
    
    # ===== Timing (seconds) =====
    batch_timeout: float = 90.0  # ← CHANGE THIS!
    ui_load_wait_min: float = 10.0
    ui_load_wait_max: float = 12.0
```

**All other values auto-calculate:**
- Total time = `batch_timeout × 3`
- Average per URL = `total_time ÷ total_urls`
- Speedup = `sequential_time ÷ total_time`
- etc.

### **2. Documentation Generator**

**File:** `backend/generate_docs.py`

Reads metrics and generates:
- `ACTUAL_PERFORMANCE_SUMMARY.md`
- `UI_LOAD_WAIT_TIME_GENERATED.md`
- (More can be added)

### **3. Auto-Generation on Startup**

**File:** `backend/main.py` (lines 197-212)

```python
@app.on_event("startup")
async def startup_event():
    # ... other startup tasks ...
    
    # 📝 Auto-generate performance documentation
    try:
        from generate_docs import main as generate_docs
        generate_docs()
        logger.info("📊 Performance documentation auto-generated")
    except Exception as e:
        logger.warning(f"⚠️ Failed to generate docs: {e}")
```

**Docs regenerate automatically every time backend starts!**

---

## 📝 How to Update Performance Metrics

### **Option 1: Auto-Update (Recommended)**

1. **Edit:** `backend/performance_metrics.py`
   ```python
   batch_timeout: float = 90.0  # Change to 120.0
   ```

2. **Restart backend:**
   ```bash
   # From screenshot-app/
   ./restart.sh
   # or
   ./r
   ```

3. **Done!** Docs auto-regenerate on startup ✅

### **Option 2: Manual Generation**

1. **Edit:** `backend/performance_metrics.py`

2. **Run generator:**
   ```bash
   cd screenshot-app
   python3 backend/generate_docs.py
   ```

3. **Done!** Docs updated ✅

---

## 🎯 What Gets Updated Automatically

When you change `batch_timeout` from 90 → 120:

| Metric | Before | After | Auto-Updated? |
|--------|--------|-------|---------------|
| Batch timeout | 90s | 120s | ✅ |
| Total time | 270s (4.5 min) | 360s (6 min) | ✅ |
| Avg per URL | 5s | 6.8s | ✅ |
| Speedup | 2.5x | 1.9x | ✅ |
| All tables | Old values | New values | ✅ |
| All examples | Old values | New values | ✅ |

**Everything updates automatically - no manual calculations needed!**

---

## 📂 Files in This System

```
screenshot-app/
├── backend/
│   ├── performance_metrics.py      ← EDIT THIS to change values
│   ├── generate_docs.py            ← Generator script
│   └── main.py                     ← Auto-runs generator on startup
│
├── ACTUAL_PERFORMANCE_SUMMARY.md   ← Auto-generated
└── UI_LOAD_WAIT_TIME_GENERATED.md  ← Auto-generated
```

---

## 💡 Benefits

| Before | After |
|--------|-------|
| 17 manual edits | 1 edit |
| 3 files to update | 1 file to edit |
| Manual calculations | Auto-calculated |
| Error-prone | Guaranteed consistent |
| 5 minutes work | 10 seconds work |
| Must remember to update all files | Just restart backend |

---

## 🔧 Adding More Generated Docs

To add more documentation files:

1. **Add template function in `generate_docs.py`:**
   ```python
   def generate_my_new_doc() -> str:
       m = metrics.to_dict()
       return f"""# My New Doc
       Batch timeout: {m['batch_timeout']}s
       Total time: {m['total_time']}s
       """
   ```

2. **Add to `main()` function:**
   ```python
   def main(verbose: bool = True):
       # ... existing code ...
       
       # Generate new doc
       new_doc_path = docs_dir / "MY_NEW_DOC.md"
       new_doc_content = generate_my_new_doc()
       new_doc_path.write_text(new_doc_content)
   ```

3. **Restart backend** - new doc auto-generates!

---

## 🎉 Summary

**You asked:** "can u introduce a variable that is unique when u have to change the secs change once it will change every where?"

**Answer:** ✅ YES!

1. Change `batch_timeout = 90.0` in `backend/performance_metrics.py`
2. Restart backend (or run `python3 backend/generate_docs.py`)
3. ALL docs update automatically with correct calculations!

**No more manual edits, no more hunting for values across files!** 🚀

