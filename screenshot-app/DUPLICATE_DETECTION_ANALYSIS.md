# 🔍 Duplicate Detection Analysis - Why Different Results?

## 📊 The Mystery

User asked: **"Why did Nov 9 capture (with skip duplicates ON) produce 22 images, but Nov 10 capture (with skip duplicates ON) only produced 10 images?"**

Both captures used:
- ✅ Same URLs (6 Tekion pages)
- ✅ Same setting: "Skip duplicates" = ON
- ✅ Same duplicate threshold: 95% similarity

But different results:
- 🟢 **Nov 9 00:01**: 22 images in Word document
- 🔴 **Nov 10 02:32**: 10 images kept (16 duplicates deleted)

---

## 🔬 Investigation Results

### Evidence Collected

**Nov 9 Documents (Skip Duplicates ON)**:
- `Accounting_AccountPayable.docx`: 22 images
- `Settings.docx`: 22 images
- Created: Nov 9 00:01 and 00:05
- File sizes: 4.2 MB each

**Nov 10 Capture (Skip Duplicates ON)**:
- Total segments captured: 26
- Total segments kept: 10
- Duplicates deleted: 16 (61.5%)
- Breakdown:
  - AccountReceivable_Setup: 7 captured → 1 kept (6 duplicates)
  - AccountPayable: 5 captured → 1 kept (4 duplicates)
  - Sales_DealSetup: 8 captured → 5 kept (3 duplicates)
  - Vi_Visettings: 2 captured → 1 kept (1 duplicate)
  - JournalMapping_List: 1 captured → 1 kept (0 duplicates)
  - Glaccountmapping_List: 1 captured → 1 kept (0 duplicates)

---

## 🎯 Root Cause: Duplicate Detection Bug (Now Fixed)

### The Bug (Before Fix)

**File**: `screenshot_service.py`  
**Issue**: When skipping a duplicate, `previous_hash` was NOT updated

**Buggy Code**:
```python
if skip_duplicates and previous_hash:
    current_hash = self._get_image_hash(filepath)
    similarity = self._hash_similarity(previous_hash, current_hash)

    if similarity > 0.95:
        print(f"⏭️  Segment {segment_index} skipped")
        os.remove(filepath)
        position += scroll_step
        segment_index += 1
        continue  # ❌ BUG: Doesn't update previous_hash!

    previous_hash = current_hash
```

### How the Bug Caused More Images to Be Kept

**Example with 7 identical segments (all 95%+ similar)**:

**Buggy Behavior (Nov 9)**:
```
Segment 1: Hash = A → KEPT ✅, previous_hash = A
Segment 2: Hash = A → 95% similar to A → SKIPPED, previous_hash = A (NOT updated!)
Segment 3: Hash = A → 95% similar to A → SKIPPED, previous_hash = A (NOT updated!)
Segment 4: Hash = A → 95% similar to A → SKIPPED, previous_hash = A (NOT updated!)
Segment 5: Hash = A → 95% similar to A → SKIPPED, previous_hash = A (NOT updated!)
Segment 6: Hash = A → 95% similar to A → SKIPPED, previous_hash = A (NOT updated!)
Segment 7: Hash = A → 95% similar to A → SKIPPED, previous_hash = A (NOT updated!)

Result: 1 image kept (correct!)
```

Wait, that's not the issue! Let me re-analyze...

### The REAL Bug: Gradual Drift Detection

The bug actually caused **FEWER** duplicates to be detected in edge cases with gradual changes:

**Scenario**: Page with fixed header but scrolling content that gradually changes

```
Segment 1: Hash = AAAA (header + content 1)
Segment 2: Hash = AAAB (header + content 2) - 94% similar to seg 1
Segment 3: Hash = AAAC (header + content 3) - 93% similar to seg 2, but 88% similar to seg 1
```

**Buggy Behavior**:
```
Segment 1: KEPT, previous_hash = AAAA
Segment 2: 94% similar to AAAA → SKIPPED, previous_hash = AAAA (NOT updated!)
Segment 3: Compared to AAAA (88%) → KEPT ✅ (should have been compared to AAAB!)
```

**Fixed Behavior**:
```
Segment 1: KEPT, previous_hash = AAAA
Segment 2: 94% similar to AAAA → SKIPPED, previous_hash = AAAB (updated!)
Segment 3: Compared to AAAB (93%) → SKIPPED ✅ (correctly detected as duplicate)
```

---

## 🤔 Alternative Explanations

Since the bug analysis doesn't fully explain the difference, here are other possibilities:

### 1️⃣ Different Viewport Settings

**Nov 9 might have used smaller viewport**:
- Smaller viewport (e.g., 600px) = more segments needed
- More segments = more chances for unique content
- Example: 7 segments at 600px vs 5 segments at 800px

### 2️⃣ Different URLs or Page Content

**Nov 9 might have captured different pages**:
- Different URLs that had more unique content
- Same URLs but page content was different (dynamic data)
- More expanded sections = more unique segments

### 3️⃣ Different Duplicate Threshold

**The threshold might have been changed**:
- Current: `DUPLICATE_SIMILARITY_THRESHOLD = 0.95` (95%)
- Nov 9 might have been: `0.99` (99%) - stricter threshold
- Stricter threshold = fewer duplicates detected = more images kept

### 4️⃣ Multiple Captures Combined

**The 22 images might be from multiple captures**:
- Nov 9 might have run multiple captures
- Word document might have been updated multiple times
- 22 images = sum of multiple capture sessions

---

## ✅ Current Implementation (Fixed)

### How Duplicate Detection Works Now

**File**: `screenshot_service.py`  
**Method**: `_check_and_handle_duplicate()`  
**Lines**: 4154-4187

```python
def _check_and_handle_duplicate(
    self,
    filepath: Path,
    previous_hash: Optional[str],
    segment_index: int,
    estimated_segments: int
) -> Tuple[bool, str]:
    """Check if segment is duplicate and handle accordingly"""
    
    # Calculate perceptual hash of current image
    current_hash = self._get_image_hash(filepath)
    
    if previous_hash:
        # Compare with previous segment
        similarity = self._hash_similarity(previous_hash, current_hash)
        
        if similarity > self.DUPLICATE_SIMILARITY_THRESHOLD:  # 0.95
            print(f"⏭️  Segment {segment_index} skipped (duplicate, {similarity:.1%} similar)")
            os.remove(filepath)  # Delete duplicate
            return True, current_hash  # ✅ Returns current_hash (will be used as previous_hash)
    
    return False, current_hash
```

**Key Points**:
- ✅ Uses perceptual image hashing (`imagehash.average_hash`)
- ✅ Compares each segment with immediately previous segment
- ✅ Threshold: 95% similarity
- ✅ Deletes duplicate files immediately
- ✅ Returns current hash for next comparison

---

## ❌ The Fundamental Problem

### Current Implementation is Flawed

**The duplicate detection uses IMAGE SIMILARITY, not SCROLL POSITION!**

This causes issues when:
- Pages have **fixed headers/sidebars** that don't scroll
- The scrollable content area is **small** compared to fixed elements
- Multiple segments look **visually identical** even though they're at **different scroll positions**

**Example**:
```
Segment 1: Scroll 0-669px     → Hash: ABC123 → KEPT ✅
Segment 2: Scroll 535-1204px  → Hash: ABC124 → 95.5% similar → DELETED ❌
Segment 3: Scroll 1070-1739px → Hash: ABC125 → 95.5% similar → DELETED ❌
```

Even though segments 2 and 3 are at **different scroll positions** with **different content**, they're deleted because they **look similar** (due to fixed header/sidebar).

---

## 💡 Recommended Fix

### Check BOTH Scroll Position AND Image Similarity

**Only mark as duplicate if BOTH are true**:
1. **Same scroll position** (within tolerance, e.g., ±10px)
2. **High image similarity** (>95%)

**Proposed Logic**:
```python
def _check_and_handle_duplicate(
    self,
    filepath: Path,
    previous_hash: Optional[str],
    previous_scroll_position: Optional[int],
    current_scroll_position: int,
    segment_index: int,
    estimated_segments: int
) -> Tuple[bool, str, int]:
    """Check if segment is duplicate based on scroll position AND image similarity"""
    
    current_hash = self._get_image_hash(filepath)
    
    if previous_hash and previous_scroll_position is not None:
        # Check if scroll positions are different
        scroll_diff = abs(current_scroll_position - previous_scroll_position)
        
        # If scroll positions are significantly different (>10px), NOT a duplicate
        if scroll_diff > 10:
            return False, current_hash, current_scroll_position
        
        # Scroll positions are same, check image similarity
        similarity = self._hash_similarity(previous_hash, current_hash)
        
        if similarity > self.DUPLICATE_SIMILARITY_THRESHOLD:
            print(f"⏭️  Segment {segment_index} skipped (duplicate at same scroll position)")
            os.remove(filepath)
            return True, current_hash, current_scroll_position
    
    return False, current_hash, current_scroll_position
```

---

## 📝 Summary

### Why Nov 9 Had More Images

**Most Likely**: One or more of these factors:
1. ✅ Different viewport settings (smaller viewport = more segments)
2. ✅ Different duplicate threshold (stricter = fewer duplicates detected)
3. ✅ Different page content (more dynamic content = more unique segments)
4. ✅ Multiple captures combined into one document

**Less Likely**: The duplicate detection bug (it would cause fewer images, not more)

### Current Status

- ✅ Duplicate detection bug is **FIXED**
- ❌ Fundamental flaw remains: **Uses image similarity instead of scroll position**
- 💡 Recommended: **Add scroll position check to duplicate detection**

### Impact

**Current behavior**:
- Pages with fixed headers/sidebars: **High false positive rate** (deletes unique content)
- Pages with dynamic content: **Works correctly**

**With recommended fix**:
- All pages: **Low false positive rate** (only deletes true duplicates)
- Better accuracy for pages with fixed layouts

