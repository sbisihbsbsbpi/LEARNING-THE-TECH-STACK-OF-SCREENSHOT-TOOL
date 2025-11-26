# 📖 How to Use Text Box Checkbox Selection

**Quick Guide:** Selectively choose which text boxes to capture without deleting them

---

## 🎯 What This Feature Does

**Problem:**
- You have 5 text boxes set up
- You only want to capture 2 of them right now
- You don't want to delete the other 3 because you'll need them later

**Solution:**
- Simply **uncheck** the text boxes you don't want to capture
- They'll stay in your UI but won't be processed
- Later, you can **check** them again when you need them

---

## 🚀 Step-by-Step Guide

### **Step 1: Open the Main Tab**

Make sure you're in the **Main** tab and **"Open multiple text boxes"** is enabled.

---

### **Step 2: Look for the Selection Controls**

Above your text boxes, you'll see a blue bar:

```
┌─────────────────────────────────────────────────────────────┐
│ [☑️ Deselect All]  3 of 3 text boxes selected • 15 URL(s)  │
└─────────────────────────────────────────────────────────────┘
```

This shows:
- **Button:** "Deselect All" (or "Select All" if some are unchecked)
- **Stats:** How many text boxes are selected
- **URL Count:** Total URLs from selected text boxes

---

### **Step 3: Select/Deselect Individual Text Boxes**

Each text box has a **checkbox** next to its label:

**Checked (Selected):**
```
┌─────────────────────────────────────────────────────────────┐
│ [✓] Text Box 1 📝 Session Name: [Accounting___________]     │
│     Normal appearance - will be captured                    │
└─────────────────────────────────────────────────────────────┘
```

**Unchecked (Skipped):**
```
┌─────────────────────────────────────────────────────────────┐
│ [ ] Text Box 2 📝 Session Name: [Parts_____________]        │
│     Dimmed/grayed out - will be skipped                     │
└─────────────────────────────────────────────────────────────┘
```

**To uncheck a text box:**
- Click the checkbox next to the text box label
- The text box will become dimmed/grayed out
- The selection stats will update

**To check it again:**
- Click the checkbox again
- The text box will return to normal appearance

---

### **Step 4: Use "Select All" / "Deselect All"**

**To quickly select all text boxes:**
- Click the **"☐ Select All"** button
- All text boxes will be checked

**To quickly deselect all text boxes:**
- Click the **"☑️ Deselect All"** button
- All text boxes will be unchecked

The button automatically toggles based on the current state.

---

### **Step 5: Verify Your Selection**

Before capturing, check the **selection stats**:

```
3 of 5 text boxes selected • 25 URL(s) to capture
```

This tells you:
- **3 of 5:** You've selected 3 out of 5 text boxes
- **25 URLs:** Total URLs from those 3 text boxes

---

### **Step 6: Capture Screenshots**

Click **"Capture Screenshots"** as usual.

**What happens:**
- ✅ **Selected text boxes** (checked) are processed
- ❌ **Unselected text boxes** (unchecked) are skipped entirely
- 📄 Word documents are generated only for selected text boxes

**If you try to capture with no text boxes selected:**
```
⚠️ Alert: "Please select at least one text box to capture!"
```

---

## 📊 Real-World Example

### **Scenario: Selective Capture**

You have 5 text boxes set up:

1. **Text Box 1:** Accounting (10 URLs) ✅ **Selected**
2. **Text Box 2:** Parts (15 URLs) ❌ **Unselected**
3. **Text Box 3:** Service (20 URLs) ✅ **Selected**
4. **Text Box 4:** Sales (12 URLs) ❌ **Unselected**
5. **Text Box 5:** Reports (8 URLs) ❌ **Unselected**

**Selection stats show:**
```
2 of 5 text boxes selected • 30 URL(s) to capture
```

**When you click "Capture Screenshots":**
- ✅ Text Box 1 (Accounting) → 10 screenshots → Word doc generated
- ⏭️ Text Box 2 (Parts) → **Skipped**
- ✅ Text Box 3 (Service) → 20 screenshots → Word doc generated
- ⏭️ Text Box 4 (Sales) → **Skipped**
- ⏭️ Text Box 5 (Reports) → **Skipped**

**Result:**
- 2 Word documents created (Accounting, Service)
- 30 total screenshots captured
- Text Boxes 2, 4, 5 remain in UI for future use

---

## 💡 Tips & Tricks

### **Tip 1: Keep Text Boxes for Later**
Don't delete text boxes you might need later. Just uncheck them!

### **Tip 2: Quick Toggle**
Use "Select All" / "Deselect All" to quickly change all checkboxes at once.

### **Tip 3: Visual Feedback**
Unchecked text boxes are dimmed (50% opacity) so you can easily see what will be skipped.

### **Tip 4: Check URL Count**
The selection stats show total URLs from selected text boxes, so you know exactly how many screenshots will be captured.

### **Tip 5: Organize by Priority**
- Keep high-priority text boxes at the top
- Uncheck low-priority ones
- Capture high-priority first, then check the others later

---

## ❓ FAQ

### **Q: What happens to unchecked text boxes?**
**A:** They stay in your UI but are completely skipped during capture. No screenshots, no Word docs.

### **Q: Are unchecked text boxes deleted?**
**A:** No! They remain in your UI. You can check them again anytime.

### **Q: Can I capture with no text boxes selected?**
**A:** No. You'll get an error: "Please select at least one text box to capture!"

### **Q: Does the selection state persist?**
**A:** Yes! Your checkbox selections are saved to localStorage and will be remembered when you reload the app.

### **Q: What if I accidentally uncheck all text boxes?**
**A:** Click the "☐ Select All" button to quickly check all text boxes again.

### **Q: Can I see which text boxes are selected?**
**A:** Yes! The selection stats show "X of Y text boxes selected" and unchecked text boxes are dimmed.

### **Q: Does this work in single text box mode?**
**A:** No. This feature only works when "Open multiple text boxes" is enabled.

---

## 🎨 Visual Guide

### **Before (All Selected):**
```
┌─────────────────────────────────────────────────────────────┐
│ [☑️ Deselect All]  3 of 3 text boxes selected • 45 URL(s)  │
└─────────────────────────────────────────────────────────────┘

[✓] Text Box 1 - Accounting (15 URLs)
[✓] Text Box 2 - Parts (20 URLs)
[✓] Text Box 3 - Service (10 URLs)
```

### **After (Selective):**
```
┌─────────────────────────────────────────────────────────────┐
│ [☐ Select All]  1 of 3 text boxes selected • 15 URL(s)     │
└─────────────────────────────────────────────────────────────┘

[✓] Text Box 1 - Accounting (15 URLs)  ← Normal appearance
[ ] Text Box 2 - Parts (20 URLs)       ← Dimmed/grayed out
[ ] Text Box 3 - Service (10 URLs)     ← Dimmed/grayed out
```

**Capture Result:**
- ✅ Only Text Box 1 (Accounting) is captured
- ❌ Text Boxes 2 and 3 are skipped

---

## ✅ Summary

**Checkbox selection gives you:**
- ✅ **Flexibility:** Skip text boxes without deleting them
- ✅ **Control:** Choose exactly what to capture
- ✅ **Efficiency:** Process only what you need
- ✅ **Clarity:** Visual feedback shows what will be captured
- ✅ **Persistence:** Selections are saved automatically

**Happy screenshotting! 📸**

