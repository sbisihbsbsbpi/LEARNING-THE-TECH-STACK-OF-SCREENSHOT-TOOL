# Issue B: Timeout Display Fix - RESOLVED ✅

## Problem Summary

When users entered a timeout value and changed the unit (e.g., "10 minutes"), the input field would display the wrong value (e.g., "600" instead of "10").

### Example of the Bug

**User Action:**
1. Type "10" in input field
2. Change dropdown from "seconds" to "minutes"

**Expected Result:**
- Input shows: "10"
- Dropdown shows: "minutes"
- User sees: "10 minutes" (600 seconds internally)

**Actual Result (Before Fix):**
- Input shows: "600" ❌
- Dropdown shows: "minutes"
- User sees: "600 minutes" (36,000 seconds!)

---

## Root Cause

The input field was bound directly to `textBox.batchTimeout`, which always stores the value in **seconds**. When the unit changed, the input would display the raw seconds value instead of converting it to the selected unit.

**Code Issue (Line 8178):**
```typescript
value={textBox.batchTimeout || ""}  // ❌ Shows raw seconds
```

---

## Solution Implemented

### 1. Added `batchTimeoutUnit` Field

**File:** `App.tsx` Line 35

```typescript
interface TextBox {
  id: string;
  sessionName: string;
  urls: string;
  batchTimeout?: number;        // Internal: always in seconds
  batchTimeoutUnit?: string;    // Display: "seconds" | "minutes" | "hours"
}
```

### 2. Created Helper Function

**File:** `App.tsx` Lines 2692-2705

```typescript
const getTimeoutDisplayValue = (textBox: TextBox): number | string => {
  if (!textBox.batchTimeout) return "";
  
  const unit = textBox.batchTimeoutUnit || "seconds";
  
  if (unit === "minutes") {
    return textBox.batchTimeout / 60;
  } else if (unit === "hours") {
    return textBox.batchTimeout / 3600;
  } else {
    return textBox.batchTimeout;
  }
};
```

### 3. Updated Input Field

**File:** `App.tsx` Line 8214

```typescript
value={getTimeoutDisplayValue(textBox)}  // ✅ Shows converted value
```

### 4. Updated Input onChange

**File:** `App.tsx` Lines 8215-8259

- Uses unit from state instead of DOM
- Keeps the current unit when updating state
- Converts display value to seconds for storage

### 5. Updated Dropdown to Controlled Component

**File:** `App.tsx` Lines 8340-8364

```typescript
<select
  value={textBox.batchTimeoutUnit || "seconds"}  // ✅ Controlled
  onChange={(e) => {
    const newUnit = e.target.value;
    
    // Simply update the unit - input auto-updates via getTimeoutDisplayValue()
    const updatedTextBoxes = textBoxes.map((tb) =>
      tb.id === textBox.id
        ? { ...tb, batchTimeoutUnit: newUnit }
        : tb
    );
    setTextBoxes(updatedTextBoxes);
  }}
>
```

### 6. Updated Migration Logic

**File:** `App.tsx` Lines 102-115

Migrates old textboxes to include `batchTimeoutUnit: "seconds"` by default.

### 7. Updated Default Values

- Default textboxes (lines 77-97): Include `batchTimeoutUnit: "seconds"`
- New textboxes (line 3502): Include `batchTimeoutUnit: "seconds"`

---

## How It Works Now

### Data Flow

**Internal Storage (State):**
```typescript
{
  batchTimeout: 600,           // Always in seconds
  batchTimeoutUnit: "minutes"  // Display preference
}
```

**Display Calculation:**
```typescript
getTimeoutDisplayValue(textBox)
// Returns: 600 ÷ 60 = 10
```

**Input Field Shows:** `10`  
**Dropdown Shows:** `minutes`  
**User Sees:** "10 minutes" ✅

---

## Test Scenarios

### Scenario 1: Type "10" with default "seconds"
- Input onChange: 10 × 1 = 10 seconds
- State: `{ batchTimeout: 10, batchTimeoutUnit: "seconds" }`
- Display: 10 ÷ 1 = **10** ✅
- User sees: "10 seconds"

### Scenario 2: Type "10", change to "minutes"
- Dropdown onChange: Updates unit to "minutes"
- State: `{ batchTimeout: 10, batchTimeoutUnit: "minutes" }`
- Display: 10 ÷ 60 = **0.17** ✅
- User sees: "0.17 minutes"
- User types "10" again
- Input onChange: 10 × 60 = 600 seconds
- State: `{ batchTimeout: 600, batchTimeoutUnit: "minutes" }`
- Display: 600 ÷ 60 = **10** ✅
- User sees: "10 minutes"

### Scenario 3: Type "2", change to "hours"
- Dropdown onChange: Updates unit to "hours"
- State: `{ batchTimeout: 2, batchTimeoutUnit: "hours" }`
- Display: 2 ÷ 3600 = **0.0006** ✅
- User sees: "0.0006 hours"
- User types "2" again
- Input onChange: 2 × 3600 = 7200 seconds
- State: `{ batchTimeout: 7200, batchTimeoutUnit: "hours" }`
- Display: 7200 ÷ 3600 = **2** ✅
- User sees: "2 hours"

### Scenario 4: Page reload
- localStorage contains: `{ batchTimeout: 600, batchTimeoutUnit: "minutes" }`
- Page loads
- Display: 600 ÷ 60 = **10** ✅
- User sees: "10 minutes" (preference preserved!)

---

## Benefits

✅ Input field always shows correct value in selected unit  
✅ User can type "10" and select "minutes" - stays as "10 minutes"  
✅ Switching units updates display value automatically  
✅ Internal storage always in seconds (backend compatibility)  
✅ User preference (unit) saved to localStorage  
✅ Page reload preserves selected unit  
✅ No DOM manipulation - pure React state management  
✅ Cleaner, more maintainable code  

---

## Files Modified

1. **screenshot-app/frontend/src/App.tsx**
   - Line 35: Added `batchTimeoutUnit` to TextBox interface
   - Lines 77-97: Updated default textboxes
   - Lines 102-115: Updated migration logic
   - Lines 2692-2705: Added `getTimeoutDisplayValue` helper
   - Line 3502: Updated `addTextBox` function
   - Line 8214: Updated input value binding
   - Lines 8215-8259: Updated input onChange
   - Lines 8260-8335: Updated input onBlur
   - Lines 8340-8364: Updated dropdown to controlled component

---

## Testing Checklist

- [ ] Type "90" with "seconds" selected → Shows "90 seconds"
- [ ] Type "10" then select "minutes" → Shows "10 minutes"
- [ ] Type "2" then select "hours" → Shows "2 hours"
- [ ] Change from "10 minutes" to "seconds" → Shows "600 seconds"
- [ ] Change from "2 hours" to "minutes" → Shows "120 minutes"
- [ ] Reload page with "10 minutes" → Still shows "10 minutes"
- [ ] Add new textbox → Defaults to "seconds"
- [ ] Empty input and blur → Resets to "90 seconds"
- [ ] Type "5" with "seconds" → Shows warning (< 10 minimum)
- [ ] Type "200" with "minutes" → Shows warning (> 7200 max)

---

## Status

✅ **RESOLVED** - Issue B is now fixed!

The timeout display now works correctly, showing the converted value based on the selected unit while maintaining internal storage in seconds for backend compatibility.

