# ✅ Improved Duplicate Detection - Scroll Position + Image Similarity

## 🎯 Problem Solved

**Previous behavior**: Duplicate detection only checked **image similarity**, which caused false positives for pages with fixed headers/sidebars.

**New behavior**: Duplicate detection checks **BOTH scroll position AND image similarity**, preventing false positives.

---

## 📊 The Issue

### Example: Page with Fixed Header/Sidebar

**Page Layout**:
```
┌─────────────────────────────────────┐
│  FIXED HEADER (200px)               │  ← Doesn't scroll
├─────────────────────────────────────┤
│ SIDEBAR │  Scrollable Content       │
│ (300px) │  (changes as you scroll)  │
│ Fixed   │                           │
│         │                           │
└─────────────────────────────────────┘
```

**Old Behavior** (Image Similarity Only):
```
Segment 1: Scroll 0-669px     → Hash: ABC123 → KEPT ✅
Segment 2: Scroll 535-1204px  → Hash: ABC124 → 95.5% similar → DELETED ❌ (WRONG!)
Segment 3: Scroll 1070-1739px → Hash: ABC125 → 95.5% similar → DELETED ❌ (WRONG!)
```

**Why it's wrong**: Segments 2 and 3 have **different content** in the scrollable area, but they look 95%+ similar because the fixed header/sidebar takes up most of the image.

**New Behavior** (Scroll Position + Image Similarity):
```
Segment 1: Scroll 0-669px     → Hash: ABC123 → KEPT ✅
Segment 2: Scroll 535-1204px  → Hash: ABC124 → Different scroll position (535px diff) → KEPT ✅
Segment 3: Scroll 1070-1739px → Hash: ABC125 → Different scroll position (535px diff) → KEPT ✅
```

**Why it's correct**: Even though images look similar, the scroll positions are different, so they contain different content.

---

## 🔧 Implementation

### Changes Made

**File**: `screenshot-app/backend/screenshot_service.py`

#### 1. Updated `_check_and_handle_duplicate()` Method (Lines 4154-4219)

**New Parameters**:
- `current_scroll_position: Optional[int] = None` - Current scroll position in pixels
- `previous_scroll_position: Optional[int] = None` - Previous scroll position in pixels
- `scroll_position_tolerance: int = 10` - Tolerance for scroll position comparison (default: 10px)

**New Logic**:
```python
def _check_and_handle_duplicate(
    self,
    filepath: Path,
    previous_hash: Optional[str],
    segment_index: int,
    estimated_segments: int,
    current_scroll_position: Optional[int] = None,
    previous_scroll_position: Optional[int] = None,
    scroll_position_tolerance: int = 10
) -> Tuple[bool, str]:
    """Check if segment is duplicate based on BOTH scroll position AND image similarity"""
    
    current_hash = self._get_image_hash(filepath)
    
    if previous_hash:
        # ✅ NEW: Check scroll position first (if provided)
        if current_scroll_position is not None and previous_scroll_position is not None:
            scroll_diff = abs(current_scroll_position - previous_scroll_position)
            
            # If scroll positions are significantly different, NOT a duplicate
            if scroll_diff > scroll_position_tolerance:
                print(f"   ✅ Segment {segment_index} kept (different scroll position: {scroll_diff}px difference)")
                return False, current_hash
            
            # Scroll positions are same, now check image similarity
            similarity = self._hash_similarity(previous_hash, current_hash)
            
            if similarity > self.DUPLICATE_SIMILARITY_THRESHOLD:
                print(f"⏭️  Segment {segment_index} skipped (duplicate: same scroll position + {similarity:.1%} similar)")
                os.remove(filepath)
                return True, current_hash
        else:
            # ✅ FALLBACK: Old behavior (image similarity only) if scroll positions not provided
            similarity = self._hash_similarity(previous_hash, current_hash)
            
            if similarity > self.DUPLICATE_SIMILARITY_THRESHOLD:
                print(f"⏭️  Segment {segment_index} skipped (duplicate, {similarity:.1%} similar)")
                os.remove(filepath)
                return True, current_hash
    
    return False, current_hash
```

#### 2. Updated Non-CDP Capture Loop (Lines 3264-3434)

**Added**:
- `previous_scroll_position = None` - Track previous scroll position
- Pass `actual_scroll` to duplicate check
- Update `previous_scroll_position` after each segment

**Code**:
```python
# Initialize tracking variables
previous_hash = None
previous_scroll_position = None  # ✅ NEW

# In the loop, after capturing screenshot:
if skip_duplicates:
    is_duplicate, current_hash = self._check_and_handle_duplicate(
        filepath=filepath,
        previous_hash=previous_hash,
        segment_index=segment_index,
        estimated_segments=estimated_segments,
        current_scroll_position=actual_scroll,  # ✅ NEW
        previous_scroll_position=previous_scroll_position,  # ✅ NEW
        scroll_position_tolerance=10
    )
    
    if is_duplicate:
        previous_hash = current_hash
        previous_scroll_position = actual_scroll  # ✅ NEW
        continue
    
    previous_hash = current_hash
    previous_scroll_position = actual_scroll  # ✅ NEW
```

#### 3. Updated CDP Capture Loop (Lines 3904-4088)

**Same changes as non-CDP version**, using `final_scroll_check['scrollTop']` instead of `actual_scroll`.

---

## ✅ Backward Compatibility

### Old Code Still Works!

**If scroll positions are NOT provided**, the method falls back to the old behavior (image similarity only):

```python
# Old code (still works):
is_duplicate, current_hash = self._check_and_handle_duplicate(
    filepath, previous_hash, segment_index, estimated_segments
)

# New code (improved):
is_duplicate, current_hash = self._check_and_handle_duplicate(
    filepath=filepath,
    previous_hash=previous_hash,
    segment_index=segment_index,
    estimated_segments=estimated_segments,
    current_scroll_position=actual_scroll,
    previous_scroll_position=previous_scroll_position
)
```

**Both work!** The old code uses default values (`None`) for scroll positions, which triggers the fallback behavior.

---

## 📊 Expected Results

### Before (Image Similarity Only)

**Tekion AccountPayable page** (7 segments):
- Segment 1: KEPT
- Segments 2-7: DELETED (95%+ similar due to fixed header/sidebar)
- **Result**: 1 image (86% deletion rate)

### After (Scroll Position + Image Similarity)

**Tekion AccountPayable page** (7 segments):
- Segment 1: KEPT (scroll 0px)
- Segment 2: KEPT (scroll 535px - different position)
- Segment 3: KEPT (scroll 1070px - different position)
- Segment 4: KEPT (scroll 1605px - different position)
- Segment 5: KEPT (scroll 2140px - different position)
- Segment 6: KEPT (scroll 2675px - different position)
- Segment 7: KEPT (scroll 3210px - different position)
- **Result**: 7 images (0% deletion rate)

---

## 🔍 When Duplicates ARE Detected

### True Duplicates (Same Scroll Position + Similar Image)

**Scenario**: Browser scrolls to same position twice (e.g., scroll gets stuck)

```
Segment 1: Scroll 0px     → Hash: ABC123 → KEPT ✅
Segment 2: Scroll 0px     → Hash: ABC123 → Same position (0px diff) + 100% similar → DELETED ✅
```

**This is correct!** If we're at the same scroll position and the image looks the same, it's a true duplicate.

---

## 🎯 Duplicate Detection Logic

### Decision Tree

```
Is previous_hash available?
├─ NO → Keep segment (first segment)
└─ YES → Are scroll positions provided?
    ├─ NO → Check image similarity only (old behavior)
    │   └─ Similarity > 95%?
    │       ├─ YES → DELETE (duplicate)
    │       └─ NO → KEEP (unique)
    └─ YES → Check scroll position first
        └─ Scroll difference > 10px?
            ├─ YES → KEEP (different position = different content)
            └─ NO → Check image similarity
                └─ Similarity > 95%?
                    ├─ YES → DELETE (same position + similar = duplicate)
                    └─ NO → KEEP (same position but different content)
```

---

## 📝 Configuration

### Scroll Position Tolerance

**Default**: 10px

**Why 10px?**: Allows for minor scroll position variations due to:
- Browser rounding errors
- Scroll position not sticking exactly
- Sub-pixel rendering differences

**Can be changed** by passing `scroll_position_tolerance` parameter:

```python
is_duplicate, current_hash = self._check_and_handle_duplicate(
    filepath=filepath,
    previous_hash=previous_hash,
    segment_index=segment_index,
    estimated_segments=estimated_segments,
    current_scroll_position=actual_scroll,
    previous_scroll_position=previous_scroll_position,
    scroll_position_tolerance=20  # ✅ Custom tolerance
)
```

### Image Similarity Threshold

**Default**: 0.95 (95%)

**Defined in**: `ScreenshotService.DUPLICATE_SIMILARITY_THRESHOLD`

**Can be changed** by modifying the class constant:

```python
class ScreenshotService:
    DUPLICATE_SIMILARITY_THRESHOLD = 0.99  # Stricter (99%)
```

---

## 🧪 Testing

### Test Case 1: Page with Fixed Header/Sidebar

**Expected**: All segments kept (different scroll positions)

**Command**:
```bash
# Capture Tekion AccountPayable page with skip duplicates ON
# Should keep all 7 segments (not just 1)
```

### Test Case 2: Static Page (No Scrolling)

**Expected**: Only 1 segment kept (same scroll position + similar images)

**Command**:
```bash
# Capture a static page that doesn't scroll
# Should keep only 1 segment (rest are true duplicates)
```

### Test Case 3: Gradually Changing Content

**Expected**: All segments kept (different scroll positions, even if similar)

**Command**:
```bash
# Capture a page with gradually changing content
# Should keep all segments (scroll positions are different)
```

---

## 📊 Summary

### What Changed

✅ Duplicate detection now checks **BOTH** scroll position AND image similarity  
✅ Prevents false positives for pages with fixed headers/sidebars  
✅ Backward compatible (old code still works)  
✅ Configurable scroll position tolerance (default: 10px)  
✅ Applied to both non-CDP and CDP capture modes  

### What Didn't Change

✅ Image similarity threshold (still 95%)  
✅ Perceptual hash algorithm (still `imagehash.average_hash`)  
✅ File deletion behavior (still deletes duplicates immediately)  
✅ Performance (minimal overhead from scroll position check)  

### Impact

**Before**: 61.5% of segments deleted as duplicates (16 out of 26)  
**After**: Expected ~0-10% deletion rate (only true duplicates)  

**Result**: More accurate duplicate detection, especially for pages with fixed layouts!

---

## 🚀 Status

✅ **IMPLEMENTED**  
✅ **BACKWARD COMPATIBLE**  
✅ **READY FOR TESTING**  

**Next Steps**:
1. Restart backend server
2. Run test capture with skip duplicates ON
3. Verify all segments are kept for pages with fixed headers/sidebars

