# Batch Timeout Unit Selector Enhancement

**Date:** November 12, 2025  
**Feature:** Enhanced Batch Timeout input with unit selector (seconds/minutes/hours)

---

## 🎯 **Overview**

Enhanced the **Batch Timeout** input field in the Main tab to allow users to enter timeout values in **seconds**, **minutes**, or **hours** instead of only seconds. The frontend automatically converts all values to seconds before storing, ensuring **no backend changes are needed**.

---

## ✨ **What Changed**

### **Before:**
```
⏱️ Batch Timeout (secs): [90]
```
- User had to manually calculate seconds (e.g., 4 minutes = 240 seconds)
- Only supported seconds
- Hardcoded range: 10-300 seconds

### **After:**
```
⏱️ Batch Timeout: [4] [minutes ▼]
```
- User can enter "4" and select "minutes" from dropdown
- Frontend automatically converts to 240 seconds
- Supports seconds, minutes, and hours
- Extended range: 10 seconds to 2 hours (7200 seconds)

---

## 🎨 **UI Components**

### **1. Label**
- **Before:** "⏱️ Batch Timeout (secs):"
- **After:** "⏱️ Batch Timeout:"

### **2. Number Input**
- **Type:** `number` with `step="any"` (allows decimals like 0.5)
- **Placeholder:** Empty (no default placeholder)
- **Value:** Shows the timeout in seconds (e.g., 240)
- **Width:** 80px

### **3. Unit Dropdown** (NEW)
- **Options:** 
  - "seconds" (default)
  - "minutes"
  - "hours"
- **Default:** "seconds"
- **Width:** 100px

---

## 🔧 **How It Works**

### **User Flow Example 1: Enter 4 minutes**

1. **User types:** `4` in the input field
2. **User selects:** `minutes` from dropdown
3. **Frontend calculates:** 4 × 60 = 240 seconds
4. **Frontend stores:** `batchTimeout: 240` (in TextBox object)
5. **Backend receives:** `batch_timeout: 240` (in API request)
6. **On page reload:** Input shows `240`, dropdown shows `seconds`

### **User Flow Example 2: Enter 0.5 hours**

1. **User types:** `0.5` in the input field
2. **User selects:** `hours` from dropdown
3. **Frontend calculates:** 0.5 × 3600 = 1800 seconds
4. **Frontend stores:** `batchTimeout: 1800`
5. **Backend receives:** `batch_timeout: 1800`
6. **On page reload:** Input shows `1800`, dropdown shows `seconds`

### **User Flow Example 3: Change unit from seconds to minutes**

1. **Current state:** Input shows `240`, dropdown shows `seconds`
2. **User changes dropdown to:** `minutes`
3. **Frontend recalculates:** 240 × 60 = 14400 seconds
4. **Frontend stores:** `batchTimeout: 14400`
5. **Input still shows:** `240` (the number doesn't change, only the unit)

---

## 💾 **Data Storage**

### **What's Stored**

**TextBox Interface (unchanged):**
```typescript
interface TextBox {
  id: string;
  sessionName: string;
  urls: string;
  batchTimeout?: number; // Stored in SECONDS only
}
```

**localStorage Example:**
```json
{
  "screenshot-textboxes": [
    {
      "id": "textbox-1",
      "sessionName": "Clark Chevrolet",
      "urls": "...",
      "batchTimeout": 240  // ← Always in seconds
    }
  ]
}
```

### **What's NOT Stored**

❌ **No `batchTimeoutUnit` field** - Dropdown selection is UI state only  
❌ **No `batchTimeoutValue` field** - Only seconds are stored  
❌ **No persistence of unit selection** - Always defaults to "seconds" on reload  

---

## 🔄 **Conversion Logic**

### **Input → Seconds Conversion**

```typescript
let timeoutInSeconds = numericValue;

if (unit === "minutes") {
  timeoutInSeconds = numericValue * 60;
} else if (unit === "hours") {
  timeoutInSeconds = numericValue * 3600;
}

// Round to nearest integer
const finalTimeout = Math.round(timeoutInSeconds);
```

### **Conversion Examples**

| User Input | Unit | Calculation | Stored Value |
|------------|------|-------------|--------------|
| 90 | seconds | 90 × 1 | 90 seconds |
| 4 | minutes | 4 × 60 | 240 seconds |
| 0.5 | hours | 0.5 × 3600 | 1800 seconds |
| 1.5 | minutes | 1.5 × 60 | 90 seconds |
| 2 | hours | 2 × 3600 | 7200 seconds |

---

## ✅ **Validation Rules**

### **Range Limits**

| Unit | Min | Max | Equivalent in Seconds |
|------|-----|-----|----------------------|
| **Seconds** | 10 | 7200 | 10s to 2 hours |
| **Minutes** | 0.17 | 120 | 10s to 2 hours |
| **Hours** | 0.003 | 2 | 10s to 2 hours |

**Note:** The validation is done in seconds, so any combination that results in 10-7200 seconds is valid.

### **Validation Logic**

```typescript
// Validate range (10 seconds to 2 hours = 7200 seconds)
if (timeoutInSeconds >= 10 && timeoutInSeconds <= 7200) {
  // Valid - update state
  setTextBoxes(updatedTextBoxes);
} else {
  // Invalid - ignore input
}
```

### **Empty Input Handling**

- **On change:** Allows empty input temporarily
- **On blur:** Resets to default (90 seconds) if empty or zero

---

## 🚀 **Auto-Save Behavior**

### **Debounced Auto-Save (500ms)**

The `textBoxes` state uses `useDebouncedLocalStorage` with 500ms delay:

```typescript
const [textBoxes, setTextBoxes] = useDebouncedLocalStorage<TextBox[]>(
  "screenshot-textboxes",
  [...],
  500  // ← 500ms auto-save delay
);
```

**How it works:**
1. User types "4" → State updates immediately
2. User selects "minutes" → State updates immediately (converts to 240 seconds)
3. **After 500ms of inactivity** → Saved to localStorage automatically
4. No manual save button needed ✅

---

## 🔌 **Backend Compatibility**

### **No Backend Changes Required**

The backend continues to receive `batch_timeout` in **seconds** only:

**Backend Model (main.py):**
```python
class URLRequest(BaseModel):
    batch_timeout: Optional[int] = Field(
        default=90, 
        ge=10,      # Min: 10 seconds
        le=7200,    # Max: 7200 seconds (2 hours) - UPDATED
        description="Batch timeout in seconds (10-7200, up to 2 hours)"
    )
```

**API Request Example:**
```json
{
  "urls": ["https://example.com"],
  "batch_timeout": 240,  // ← Always in seconds
  "max_parallel_urls": 5
}
```

---

## 📊 **Example Scenarios**

### **Scenario 1: Quick URLs (30 seconds)**

**User Input:**
```
Input: [30]
Dropdown: [seconds]
```

**Stored:** `batchTimeout: 30`  
**Backend receives:** `batch_timeout: 30`  
**Use case:** Fast-loading pages

---

### **Scenario 2: Complex Pages (4 minutes)**

**User Input:**
```
Input: [4]
Dropdown: [minutes]
```

**Stored:** `batchTimeout: 240`  
**Backend receives:** `batch_timeout: 240`  
**Use case:** Pages with heavy JavaScript, animations, or lazy loading

---

### **Scenario 3: Very Slow Pages (1 hour)**

**User Input:**
```
Input: [1]
Dropdown: [hours]
```

**Stored:** `batchTimeout: 3600`  
**Backend receives:** `batch_timeout: 3600`  
**Use case:** Extremely complex dashboards or pages with long-running scripts

---

### **Scenario 4: Fractional Values (1.5 minutes)**

**User Input:**
```
Input: [1.5]
Dropdown: [minutes]
```

**Stored:** `batchTimeout: 90` (1.5 × 60 = 90)  
**Backend receives:** `batch_timeout: 90`  
**Use case:** Fine-tuning timeout to exact needs

---

## 🎯 **Benefits**

### **1. User-Friendly**
✅ No mental math required (4 minutes vs. 240 seconds)  
✅ Intuitive unit selection  
✅ Supports decimals (0.5 hours, 1.5 minutes)  

### **2. Flexible**
✅ Wide range: 10 seconds to 2 hours  
✅ Three unit options (seconds, minutes, hours)  
✅ Auto-converts between units  

### **3. Backward Compatible**
✅ Existing text boxes continue to work  
✅ No data migration needed  
✅ No localStorage schema changes  

### **4. Consistent**
✅ Backend still receives seconds  
✅ No API changes required  
✅ Internal storage unchanged  

### **5. Auto-Save**
✅ 500ms debounced auto-save  
✅ No manual save button needed  
✅ Changes persist automatically  

---

## 🔍 **Technical Details**

### **Files Modified**

1. **`screenshot-app/frontend/src/App.tsx`** (Lines 8157-8322)
   - Replaced single input with input + dropdown combo
   - Added unit conversion logic
   - Updated validation ranges
   - Added auto-save with 500ms debounce

2. **`screenshot-app/frontend/src/App.tsx`** (Lines 2672-2680)
   - Updated `updateBatchTimeout` validation to support 10-7200 seconds

3. **`screenshot-app/backend/main.py`** (Line 115)
   - Updated `batch_timeout` field validation to `le=7200` (was `le=300`)

### **Key Functions**

**Conversion on Input Change:**
```typescript
onChange={(e) => {
  const numericValue = parseFloat(e.target.value);
  const unit = document.getElementById(`timeout-unit-${textBox.id}`).value;
  
  let timeoutInSeconds = numericValue;
  if (unit === "minutes") timeoutInSeconds = numericValue * 60;
  if (unit === "hours") timeoutInSeconds = numericValue * 3600;
  
  setTextBoxes(updatedTextBoxes); // Auto-saves after 500ms
}
```

**Conversion on Unit Change:**
```typescript
onChange={(e) => {
  const inputValue = inputField.value;
  const numericValue = parseFloat(inputValue);
  const unit = e.target.value;
  
  let timeoutInSeconds = numericValue;
  if (unit === "minutes") timeoutInSeconds = numericValue * 60;
  if (unit === "hours") timeoutInSeconds = numericValue * 3600;
  
  setTextBoxes(updatedTextBoxes); // Auto-saves after 500ms
}
```

---

## 🧪 **Testing Checklist**

- [ ] Enter "90" seconds → Stores 90 seconds
- [ ] Enter "4" minutes → Stores 240 seconds
- [ ] Enter "0.5" hours → Stores 1800 seconds
- [ ] Change unit from seconds to minutes → Recalculates correctly
- [ ] Empty input on blur → Resets to 90 seconds
- [ ] Invalid range (e.g., 5 seconds) → Ignored
- [ ] Page reload → Shows value in seconds, dropdown defaults to "seconds"
- [ ] Auto-save works after 500ms
- [ ] Backend receives correct timeout in seconds
- [ ] Multiple text boxes work independently

---

## 📝 **Notes**

1. **Unit selection is NOT persisted** - Always defaults to "seconds" on page reload
2. **Values are always stored in seconds** - No additional fields in TextBox interface
3. **Backend unchanged** - Still expects `batch_timeout` in seconds
4. **Extended range** - Now supports up to 2 hours (7200 seconds) instead of 5 minutes (300 seconds)
5. **Decimal support** - Allows fractional values like 0.5 hours or 1.5 minutes

---

**End of Documentation**

