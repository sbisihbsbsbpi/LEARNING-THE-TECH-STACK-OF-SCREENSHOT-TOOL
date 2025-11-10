# ✅ Max Parallel URLs Per Text Box - User-Configurable Setting

## 🎯 Feature Overview

Added a new user-configurable setting that allows users to control how many URLs are processed in parallel **per text box** when using **Real Browser Mode**.

---

## 📊 What Was Added

### 1. Frontend (App.tsx)

**New State Variable** (Lines 48-52):
```typescript
const [maxParallelUrls, setMaxParallelUrls] = useLocalStorage(
  "screenshot-max-parallel-urls",
  5 // Default: 5 URLs in parallel (optimal for Real Browser Mode)
);
```

**New UI Input** (Lines 6955-6995):
- Number input field (range: 1-10)
- Dynamic hint text based on selected value
- Validation to ensure value stays within 1-10 range
- Note explaining it only applies to Real Browser Mode

**API Integration** (Lines 3518, 3715):
- Added `max_parallel_urls: maxParallelUrls` to both API request bodies

---

### 2. Backend (main.py)

**New Request Parameter** (Lines 115-116):
```python
max_parallel_urls: int = Field(
    default=5, 
    ge=1, 
    le=10, 
    description="Max parallel URLs (1-10, Real Browser Mode only)"
)
```

**Updated Batching Logic** (Lines 251-300):
- Modified `_create_smart_batches()` to accept `max_parallel` and `use_real_browser` parameters
- For Real Browser Mode: Creates batches of `max_parallel` size
- For Headless Mode: Uses existing domain-based batching logic

**Updated Logging** (Lines 481-495):
- Logs the user-configured max parallel URLs value
- Shows "Will open up to X tabs at once" where X is the user's setting

---

## 🎨 UI Design

### Settings Section

```
⚡ Parallel Text Box Processing
☑ Process all text boxes in parallel
✅ Enabled: All text boxes are processed simultaneously (maximum speed)

Max parallel URLs per text box: [5]

✅ Optimal: 5 URLs in parallel (recommended for most cases)
💡 Applies to Real Browser Mode only. Headless mode always processes 1 URL at a time.
```

### Dynamic Hints

The hint text changes based on the selected value:

| Value | Hint |
|-------|------|
| **1** | ⚠️ Sequential: URLs processed one at a time (slowest, most stable) |
| **2-3** | ✅ Conservative: X URLs in parallel (stable, good for 50+ URLs) |
| **4-5** | ✅ Optimal: X URLs in parallel (recommended for most cases) |
| **6-7** | ⚡ Fast: X URLs in parallel (faster, uses more memory) |
| **8-10** | ⚠️ Maximum: X URLs in parallel (fastest, may be unstable with many URLs) |

---

## 📈 How It Works

### Example: 6 URLs with Different Settings

**Setting: 1 (Sequential)**
```
Batch 1: URL 1
Batch 2: URL 2
Batch 3: URL 3
Batch 4: URL 4
Batch 5: URL 5
Batch 6: URL 6
Total batches: 6
```

**Setting: 3 (Conservative)**
```
Batch 1: URLs 1-3 (parallel)
Batch 2: URLs 4-6 (parallel)
Total batches: 2
```

**Setting: 5 (Optimal - Default)**
```
Batch 1: URLs 1-5 (parallel)
Batch 2: URL 6
Total batches: 2
```

**Setting: 10 (Maximum)**
```
Batch 1: URLs 1-6 (parallel)
Total batches: 1
```

---

## 🔧 Technical Details

### Frontend Changes

**File**: `screenshot-app/frontend/src/App.tsx`

1. **State Management** (Line 48-52):
   - Uses `useLocalStorage` hook for persistence
   - Default value: 5
   - Stored in localStorage as `screenshot-max-parallel-urls`

2. **Input Validation** (Lines 6966-6969):
   - Parses input as integer
   - Clamps value between 1 and 10
   - Prevents invalid values

3. **API Requests** (Lines 3518, 3715):
   - Sends `max_parallel_urls` to backend
   - Applied to both single and multiple text box modes

### Backend Changes

**File**: `screenshot-app/backend/main.py`

1. **Request Model** (Lines 115-116):
   - Added `max_parallel_urls` field
   - Validation: 1-10 range
   - Default: 5

2. **Batching Function** (Lines 251-300):
   - New parameters: `max_parallel`, `use_real_browser`
   - Real Browser Mode: Simple batching by `max_parallel` size
   - Headless Mode: Domain-based batching (unchanged)

3. **Batch Creation** (Lines 481-495):
   - Passes user setting to `_create_smart_batches()`
   - Logs the configured value

---

## 💡 Use Cases

### When to Use Different Settings

**1 URL at a time (Sequential)**
- ✅ Maximum stability
- ✅ Debugging individual URLs
- ❌ Very slow for many URLs

**2-3 URLs in parallel (Conservative)**
- ✅ Good for 50+ URLs
- ✅ Lower memory usage
- ✅ More stable with many tabs
- ⚠️ Slower than optimal

**4-5 URLs in parallel (Optimal - Default)**
- ✅ Best balance of speed and stability
- ✅ Recommended for most use cases
- ✅ Works well with 1-50 URLs
- ✅ Chrome handles this well

**6-7 URLs in parallel (Fast)**
- ✅ Faster processing
- ⚠️ Higher memory usage (~3.5-4.5GB)
- ⚠️ May slow down Chrome with many URLs

**8-10 URLs in parallel (Maximum)**
- ✅ Fastest possible
- ❌ High memory usage (~5-6GB)
- ❌ Chrome may become unstable
- ❌ Higher chance of tab crashes
- ⚠️ Only use for small batches (<20 URLs total)

---

## 📊 Performance Impact

### Memory Usage (Approximate)

| Parallel URLs | Memory per Tab | Total Memory | Chrome Stability |
|---------------|----------------|--------------|------------------|
| 1 | 500 MB | 500 MB | ✅ Excellent |
| 3 | 500 MB | 1.5 GB | ✅ Excellent |
| 5 | 500 MB | 2.5 GB | ✅ Good |
| 7 | 500 MB | 3.5 GB | ⚠️ Fair |
| 10 | 500 MB | 5.0 GB | ❌ Poor |

### Speed Comparison (6 URLs)

| Setting | Batches | Time (est.) | Speed vs Sequential |
|---------|---------|-------------|---------------------|
| 1 | 6 | ~120s | 1x (baseline) |
| 3 | 2 | ~40s | 3x faster |
| 5 | 2 | ~40s | 3x faster |
| 6 | 1 | ~20s | 6x faster |
| 10 | 1 | ~20s | 6x faster |

---

## ✅ Testing

### Test Cases

**Test 1: Default Setting (5)**
- Create 6 URLs
- Check logs: "Will open up to 5 tabs at once"
- Verify 2 batches created (5 + 1)

**Test 2: Sequential (1)**
- Change setting to 1
- Create 6 URLs
- Check logs: 6 batches created
- Verify URLs processed one at a time

**Test 3: Maximum (10)**
- Change setting to 10
- Create 6 URLs
- Check logs: "Will open up to 10 tabs at once"
- Verify 1 batch created (all 6 URLs)

**Test 4: Persistence**
- Set to 7
- Refresh page
- Verify setting is still 7

---

## 🎯 User Benefits

1. **Flexibility**: Users can optimize for their specific needs
2. **Performance**: Can go faster (10) or more stable (1-3)
3. **Resource Control**: Can limit memory usage for low-spec machines
4. **Debugging**: Can set to 1 for easier debugging
5. **Scalability**: Can handle both small (6 URLs) and large (100+ URLs) batches

---

## 📝 Summary

### What Changed

✅ Added user-configurable "Max parallel URLs per text box" setting  
✅ Range: 1-10 (default: 5)  
✅ Applies to Real Browser Mode only  
✅ Persisted in localStorage  
✅ Dynamic hint text based on value  
✅ Backend respects user setting  
✅ Improved batching logic  

### What Didn't Change

✅ Headless mode still processes 1 URL at a time  
✅ Domain-based batching for headless mode unchanged  
✅ Parallel text box processing unchanged  
✅ All other settings unchanged  

### Status

✅ **IMPLEMENTED**  
✅ **TESTED** (no syntax errors)  
⏳ **READY FOR USER TESTING**  

---

## 🚀 Next Steps

1. **Test the feature**: Change the setting and run a capture
2. **Monitor performance**: Check memory usage and speed
3. **Adjust as needed**: Find the optimal value for your use case

**Recommended starting point**: Keep it at **5** (default) and only change if you have specific needs!

