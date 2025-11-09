# ⏱️ Per-Text-Box Batch Timeout Feature

## 🎯 What Changed

**BEFORE:** All text boxes shared the same batch timeout (90 seconds)

**AFTER:** Each text box has its own independent batch timeout!

---

## 🚀 How It Works Now

### **Each Text Box Has Its Own Timeout:**

```
Text Box 1: [Accounting] ⏱️ [90]  ← Fast pages
Text Box 2: [Parts]      ⏱️ [120] ← Slow pages  
Text Box 3: [Service]    ⏱️ [60]  ← Very fast pages
```

**Each timeout is:**
- ✅ Stored independently per text box
- ✅ Persisted to localStorage
- ✅ Used when capturing that specific text box
- ✅ Migrated automatically from old data

---

## 📊 Data Structure

### **TextBox Interface:**

```typescript
interface TextBox {
  id: string;
  sessionName: string;
  urls: string;
  batchTimeout?: number; // ✅ NEW: Optional for backward compatibility
}
```

### **Example Data:**

```typescript
textBoxes = [
  {
    id: "textbox-1",
    sessionName: "Accounting",
    urls: "https://...",
    batchTimeout: 90  // ← Text Box 1 timeout
  },
  {
    id: "textbox-2",
    sessionName: "Parts",
    urls: "https://...",
    batchTimeout: 120 // ← Text Box 2 timeout
  },
  {
    id: "textbox-3",
    sessionName: "Service",
    urls: "https://...",
    batchTimeout: 60  // ← Text Box 3 timeout
  }
]
```

---

## 🎮 How to Use

### **Step 1: Open Main Tab**

Enable "Open multiple text boxes" checkbox

### **Step 2: Set Different Timeouts**

```
Text Box 1: [Accounting] ⏱️ [90]  ← Type 90
Text Box 2: [Parts]      ⏱️ [120] ← Type 120
Text Box 3: [Service]    ⏱️ [60]  ← Type 60
```

### **Step 3: Capture Screenshots**

When you click "Capture Screenshots":
- Text Box 1 uses 90s timeout
- Text Box 2 uses 120s timeout
- Text Box 3 uses 60s timeout

**Each text box uses its own timeout!** 🎯

---

## 🔧 Implementation Details

### **1. State Management**

**Removed global timeout:**
```typescript
// ❌ OLD: Global timeout for all text boxes
const [batchTimeout, setBatchTimeout] = useState(90);

// ✅ NEW: Each text box has its own timeout
interface TextBox {
  batchTimeout?: number; // Stored per text box
}
```

### **2. Update Function**

**Changed signature:**
```typescript
// ❌ OLD: Updates global timeout
const updateBatchTimeout = async (newTimeout: number) => { ... }

// ✅ NEW: Updates specific text box's timeout
const updateBatchTimeout = async (textBoxId: string, newTimeout: number) => {
  // Find the text box
  const textBox = textBoxes.find(tb => tb.id === textBoxId);
  const oldTimeout = textBox.batchTimeout || 90;
  
  // Update only this text box
  const updatedTextBoxes = textBoxes.map(tb =>
    tb.id === textBoxId ? { ...tb, batchTimeout: newTimeout } : tb
  );
  setTextBoxes(updatedTextBoxes);
  
  // Trigger doc generation if changed
  if (newTimeout !== oldTimeout) {
    // ... API call
  }
}
```

### **3. UI Input**

**Uses text box's own value:**
```typescript
// ❌ OLD: All inputs showed same value
<input value={batchTimeout} ... />

// ✅ NEW: Each input shows its own text box's value
<input 
  value={textBox.batchTimeout || 90}
  onChange={(e) => {
    const newValue = parseInt(e.target.value);
    updateBatchTimeout(textBox.id, newValue); // ← Pass text box ID
  }}
/>
```

### **4. Backward Compatibility**

**Migration on mount:**
```typescript
// ✅ MIGRATION: Add batchTimeout to old text boxes
useEffect(() => {
  const needsMigration = textBoxes.some(tb => tb.batchTimeout === undefined);
  if (needsMigration) {
    const migratedTextBoxes = textBoxes.map(tb => ({
      ...tb,
      batchTimeout: tb.batchTimeout || 90 // Default to 90s if missing
    }));
    setTextBoxes(migratedTextBoxes);
  }
}, []); // Run once on mount
```

**Default for new text boxes:**
```typescript
const addTextBox = () => {
  const newTextBox: TextBox = {
    id: `textbox-${Date.now()}`,
    sessionName: "",
    urls: "",
    batchTimeout: 90, // ✅ Default timeout
  };
  setTextBoxes([...textBoxes, newTextBox]);
};
```

---

## 🛡️ Backward Compatibility

### **Old Data Migration:**

**If you have old text boxes without `batchTimeout`:**

```typescript
// OLD DATA (from localStorage):
[
  { id: "textbox-1", sessionName: "Accounting", urls: "..." }
  // ↑ No batchTimeout field
]

// AFTER MIGRATION (automatic on app load):
[
  { id: "textbox-1", sessionName: "Accounting", urls: "...", batchTimeout: 90 }
  // ↑ Added default 90s timeout
]
```

**Migration happens:**
- ✅ Automatically on app load
- ✅ Only if needed (checks for missing field)
- ✅ Preserves all existing data
- ✅ Adds default 90s timeout to old text boxes

---

## 💡 Use Cases

### **Use Case 1: Mixed Page Speeds**

**Problem:** Some pages load fast, others slow

**Solution:**
```
Text Box 1 (Fast pages):  ⏱️ [60]  ← Quick captures
Text Box 2 (Slow pages):  ⏱️ [120] ← Wait longer
Text Box 3 (Normal):      ⏱️ [90]  ← Default
```

### **Use Case 2: Different Domains**

**Problem:** Different websites have different load times

**Solution:**
```
Text Box 1 (arcdealer.com):     ⏱️ [90]  ← Normal
Text Box 2 (slow-site.com):     ⏱️ [150] ← Very slow
Text Box 3 (fast-cdn.com):      ⏱️ [45]  ← Very fast
```

### **Use Case 3: Testing Different Timeouts**

**Problem:** Want to test optimal timeout for each site

**Solution:**
```
Text Box 1: ⏱️ [60]  ← Test with 60s
Text Box 2: ⏱️ [90]  ← Test with 90s
Text Box 3: ⏱️ [120] ← Test with 120s

Compare results to find optimal timeout!
```

---

## 📂 Files Modified

### **Frontend:**

1. ✅ `frontend/src/App.tsx`
   - **Line 29-35:** Updated `TextBox` interface with `batchTimeout?: number`
   - **Line 55-77:** Added migration useEffect for old data
   - **Line 2594-2638:** Updated `updateBatchTimeout()` to accept `textBoxId`
   - **Line 3220-3230:** Updated `addTextBox()` to include default timeout
   - **Line 7078-7108:** Updated UI input to use text box's own value

### **No Backend Changes:**

Backend already supports per-request timeout via the API endpoint.

---

## 🎯 Benefits

| Feature | Before | After |
|---------|--------|-------|
| **Timeout per text box** | ❌ Shared | ✅ Independent |
| **Flexibility** | ❌ One size fits all | ✅ Customize per batch |
| **Backward compatibility** | N/A | ✅ Auto-migration |
| **Data persistence** | ✅ localStorage | ✅ localStorage |
| **UI control** | ❌ Global setting | ✅ Per text box |

---

## 🔍 Example Scenario

### **Scenario: 3 Different Websites**

**Setup:**
```
Text Box 1: arcdealer.com (18 URLs)     ⏱️ [90]
Text Box 2: slowsite.com (19 URLs)      ⏱️ [150]
Text Box 3: fastcdn.com (16 URLs)       ⏱️ [45]
```

**When you click "Capture Screenshots":**

```
Processing Text Box 1 (arcdealer.com):
  → Uses 90s timeout
  → Batch completes in ~90s
  
Processing Text Box 2 (slowsite.com):
  → Uses 150s timeout
  → Batch completes in ~150s (doesn't timeout!)
  
Processing Text Box 3 (fastcdn.com):
  → Uses 45s timeout
  → Batch completes in ~45s (faster!)
```

**Total time:** 90s + 150s + 45s = 285s (4.75 minutes)

**vs. Old way (all 90s):** 90s + 90s + 90s = 270s (but Text Box 2 would timeout!)

---

## 🎉 Summary

**Your request:** "make them handle different secs data also"

**Answer:** **DONE!** ✅

- ✅ Each text box has its own independent timeout
- ✅ Old data automatically migrated (no breaking changes)
- ✅ UI shows each text box's own timeout value
- ✅ Captures use the specific timeout for each text box
- ✅ All data persisted to localStorage
- ✅ New text boxes get default 90s timeout

**No more shared timeout - each text box is independent!** 🚀

