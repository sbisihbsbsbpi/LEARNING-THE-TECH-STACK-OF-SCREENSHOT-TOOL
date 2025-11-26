# Batch Timeout UI Guide

**Quick visual guide for using the enhanced Batch Timeout input**

---

## 🎨 **UI Layout**

### **Before Enhancement:**
```
┌─────────────────────────────────────────────┐
│ ⏱️ Batch Timeout (secs): [90        ]      │
└─────────────────────────────────────────────┘
```

### **After Enhancement:**
```
┌──────────────────────────────────────────────────────────┐
│ ⏱️ Batch Timeout: [        ] [seconds    ▼]             │
└──────────────────────────────────────────────────────────┘
     ↑ Number input    ↑ Unit dropdown
     (80px wide)       (100px wide)
```

---

## 📋 **Common Use Cases**

### **Use Case 1: Fast Pages (30 seconds)**

**When to use:** Simple pages that load quickly

**How to set:**
```
1. Type: 30
2. Select: seconds
3. Result: 30 seconds timeout
```

**Visual:**
```
⏱️ Batch Timeout: [30] [seconds ▼]
```

---

### **Use Case 2: Normal Pages (4 minutes)**

**When to use:** Most pages with moderate complexity

**How to set:**
```
1. Type: 4
2. Select: minutes
3. Result: 240 seconds timeout
```

**Visual:**
```
⏱️ Batch Timeout: [4] [minutes ▼]
```

**What gets stored:** 240 seconds

---

### **Use Case 3: Complex Pages (10 minutes)**

**When to use:** Pages with heavy JavaScript, animations, or lazy loading

**How to set:**
```
1. Type: 10
2. Select: minutes
3. Result: 600 seconds timeout
```

**Visual:**
```
⏱️ Batch Timeout: [10] [minutes ▼]
```

**What gets stored:** 600 seconds

---

### **Use Case 4: Very Slow Pages (30 minutes)**

**When to use:** Extremely complex dashboards or pages with long-running scripts

**How to set:**
```
1. Type: 30
2. Select: minutes
3. Result: 1800 seconds timeout
```

**Visual:**
```
⏱️ Batch Timeout: [30] [minutes ▼]
```

**What gets stored:** 1800 seconds

---

### **Use Case 5: Maximum Timeout (2 hours)**

**When to use:** Pages that take an extremely long time to load

**How to set:**
```
1. Type: 2
2. Select: hours
3. Result: 7200 seconds timeout
```

**Visual:**
```
⏱️ Batch Timeout: [2] [hours ▼]
```

**What gets stored:** 7200 seconds

---

### **Use Case 6: Fractional Values (1.5 minutes)**

**When to use:** Fine-tuning timeout to exact needs

**How to set:**
```
1. Type: 1.5
2. Select: minutes
3. Result: 90 seconds timeout
```

**Visual:**
```
⏱️ Batch Timeout: [1.5] [minutes ▼]
```

**What gets stored:** 90 seconds

---

## 🔄 **What Happens When You Change Units**

### **Example: Change from seconds to minutes**

**Step 1: Current state**
```
⏱️ Batch Timeout: [240] [seconds ▼]
Stored: 240 seconds
```

**Step 2: User changes dropdown to "minutes"**
```
⏱️ Batch Timeout: [240] [minutes ▼]
                    ↑ Number stays the same!
```

**Step 3: Frontend recalculates**
```
Calculation: 240 × 60 = 14400 seconds
Stored: 14400 seconds
```

**Result:** The timeout is now 14400 seconds (4 hours), which exceeds the maximum limit (7200 seconds), so the change is **ignored** and reverts to the previous value.

---

### **Correct Way to Change Units**

**If you want to change from 240 seconds to 4 minutes:**

**Option 1: Clear and re-enter**
```
1. Clear the input field
2. Type: 4
3. Select: minutes
4. Result: 240 seconds ✅
```

**Option 2: Calculate and enter**
```
1. Calculate: 240 ÷ 60 = 4
2. Type: 4
3. Select: minutes
4. Result: 240 seconds ✅
```

---

## 📊 **Quick Reference Table**

| User Input | Unit | Stored Value | Use Case |
|------------|------|--------------|----------|
| 30 | seconds | 30 sec | Very fast pages |
| 90 | seconds | 90 sec | Default (fast pages) |
| 4 | minutes | 240 sec | Normal pages |
| 10 | minutes | 600 sec | Complex pages |
| 30 | minutes | 1800 sec | Very slow pages |
| 1 | hours | 3600 sec | Extremely slow pages |
| 2 | hours | 7200 sec | Maximum timeout |
| 1.5 | minutes | 90 sec | Fine-tuning |
| 0.5 | hours | 1800 sec | 30 minutes |

---

## ⚠️ **Important Notes**

### **1. Unit Selection is NOT Saved**

When you reload the page:
- **Input field** shows the value in **seconds**
- **Dropdown** always defaults to **"seconds"**

**Example:**
```
Before reload: [4] [minutes ▼]  (stored as 240 seconds)
After reload:  [240] [seconds ▼]
```

### **2. Empty Input Resets to Default**

If you clear the input and click away:
- **Automatically resets to 90 seconds**

**Example:**
```
1. Clear input: [  ]
2. Click away (blur)
3. Result: [90] [seconds ▼]
```

### **3. Invalid Values are Ignored**

If you enter a value outside the valid range:
- **No error message**
- **Value is simply ignored**
- **Previous value is kept**

**Valid range:** 10 seconds to 7200 seconds (2 hours)

**Example:**
```
Current: [240] [seconds ▼]
User types: [5] [seconds ▼]  (too low, minimum is 10)
Result: [240] [seconds ▼]  (unchanged)
```

### **4. Auto-Save After 500ms**

Changes are automatically saved after 500ms of inactivity:
- **No save button needed**
- **Just type and wait**

**Example:**
```
1. Type: 4
2. Select: minutes
3. Wait 500ms
4. ✅ Automatically saved to localStorage
```

---

## 🎯 **Recommended Settings**

### **For Retrying Failed URLs from "Clark Chevrolet" Session**

Based on the investigation, most URLs took 60-120 seconds:

**Recommended:**
```
⏱️ Batch Timeout: [4] [minutes ▼]
```
**Result:** 240 seconds (4 minutes)  
**Success rate:** 85-95% expected

**Conservative:**
```
⏱️ Batch Timeout: [6] [minutes ▼]
```
**Result:** 360 seconds (6 minutes)  
**Success rate:** 95-99% expected

---

## 💡 **Pro Tips**

### **Tip 1: Start with Minutes for Easier Math**

Instead of calculating seconds, think in minutes:
- **2 minutes** = 120 seconds
- **4 minutes** = 240 seconds
- **5 minutes** = 300 seconds
- **10 minutes** = 600 seconds

### **Tip 2: Use Decimals for Precision**

You can use decimal values:
- **1.5 minutes** = 90 seconds
- **2.5 minutes** = 150 seconds
- **0.5 hours** = 30 minutes = 1800 seconds

### **Tip 3: Monitor the Logs**

Watch the **Log Output** section to see:
```
⏱️ Batch timeout: 240s (120s per URL)
```

This shows:
- **Batch timeout:** 240 seconds (what you set)
- **Per-URL timeout:** 120 seconds (half of batch timeout)

### **Tip 4: Adjust Based on Warnings**

If you see timeout warnings:
```
⚠️ Warning: 3 URL(s) took >80% of timeout (96s)
   ⏱️ https://example.com/page1 took 115.7s
```

**Action:** Increase timeout by 1-2 minutes

---

## 🚀 **Quick Start Guide**

### **For New Users:**

1. **Leave default (90 seconds)** for fast pages
2. **Use 4 minutes** for most pages
3. **Use 10 minutes** for complex pages
4. **Monitor logs** and adjust as needed

### **For Retrying Failed URLs:**

1. **Check the analysis** in `SESSION_ANALYSIS_*.md`
2. **Find slowest URL time** (e.g., 134 seconds)
3. **Add 50% buffer** (134 × 1.5 = 201 seconds)
4. **Round up to minutes** (201 ≈ 4 minutes)
5. **Set timeout:**
   ```
   ⏱️ Batch Timeout: [4] [minutes ▼]
   ```

---

**End of Guide**

