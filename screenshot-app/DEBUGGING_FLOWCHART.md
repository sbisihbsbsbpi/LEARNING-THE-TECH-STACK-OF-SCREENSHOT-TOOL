# 🔍 Debugging Flowchart - Blank Screen Issue

## Decision Tree

```
START: App shows blank screen
│
├─ Step 1: Check TypeScript
│  │
│  ├─ Run: npx tsc --noEmit
│  │
│  ├─ Errors found?
│  │  │
│  │  ├─ YES → Go to Step 2
│  │  │
│  │  └─ NO → Go to Step 3
│  │
│  └─ (Continue below)
│
├─ Step 2: Analyze TypeScript Errors
│  │
│  ├─ Error contains "used before"?
│  │  │
│  │  ├─ YES → Function Definition Order Issue
│  │  │  │
│  │  │  ├─ Note the function name (e.g., "addLog")
│  │  │  ├─ Note the line number where it's called
│  │  │  ├─ Find where it's defined
│  │  │  ├─ Move definition EARLIER in component
│  │  │  ├─ Restart dev server
│  │  │  └─ ✅ FIXED
│  │  │
│  │  └─ NO → Go to Step 3
│  │
│  └─ (Continue below)
│
├─ Step 3: Check Browser Console
│  │
│  ├─ Open DevTools: F12 or Cmd+Option+I
│  │
│  ├─ Red errors visible?
│  │  │
│  │  ├─ YES → Read error message
│  │  │  │
│  │  │  ├─ "is not defined" → Missing function/variable
│  │  │  ├─ "Cannot read property" → Object is undefined
│  │  │  ├─ "Unexpected token" → Syntax error
│  │  │  │
│  │  │  └─ Fix based on error type
│  │  │
│  │  └─ NO → Go to Step 4
│  │
│  └─ (Continue below)
│
├─ Step 4: Check Vite Dev Server
│  │
│  ├─ Look at terminal running "npm run dev"
│  │
│  ├─ Shows "✓ compiled successfully"?
│  │  │
│  │  ├─ YES → Go to Step 5
│  │  │
│  │  └─ NO → Compilation error
│  │     │
│  │     ├─ Read error message
│  │     ├─ Fix the error
│  │     ├─ Vite will auto-recompile
│  │     └─ Refresh browser
│  │
│  └─ (Continue below)
│
├─ Step 5: Check React Component
│  │
│  ├─ Is App component rendering?
│  │  │
│  │  ├─ Check: Does App() have a return statement?
│  │  ├─ Check: Is return statement inside try-catch?
│  │  ├─ Check: Are there any errors in render logic?
│  │  │
│  │  └─ If errors found → Fix them
│  │
│  └─ (Continue below)
│
├─ Step 6: Clear Cache & Restart
│  │
│  ├─ Run: rm -rf node_modules/.vite
│  ├─ Run: npm run dev
│  ├─ Refresh browser: Cmd+Shift+R (hard refresh)
│  │
│  └─ Does it work now?
│     │
│     ├─ YES → ✅ FIXED
│     │
│     └─ NO → Go to Step 7
│
├─ Step 7: Nuclear Option
│  │
│  ├─ Run: npm install
│  ├─ Run: npm run build
│  ├─ Run: npm run dev
│  ├─ Refresh browser
│  │
│  └─ Does it work now?
│     │
│     ├─ YES → ✅ FIXED
│     │
│     └─ NO → Escalate (unknown issue)
│
└─ END
```

---

## Quick Reference Table

| Symptom | Check | Fix |
|---------|-------|-----|
| Blank screen | `npx tsc --noEmit` | Fix TypeScript errors |
| Red console error | Browser F12 | Read error, fix code |
| Vite compilation failed | Terminal output | Fix error, restart |
| Function not defined | Search code | Move definition earlier |
| Object is undefined | Check initialization | Initialize before use |
| Syntax error | Check brackets/quotes | Fix syntax |

---

## Error Message → Solution Map

### Error: "Variable 'X' is used before being assigned"
```
Location: Line number shown
Solution: Move function definition earlier
Time: 2 minutes
```

### Error: "Block-scoped variable 'X' used before its declaration"
```
Location: Line number shown
Solution: Move function definition earlier
Time: 2 minutes
```

### Error: "Cannot read property 'X' of undefined"
```
Location: Line number shown
Solution: Check if object is initialized before use
Time: 3 minutes
```

### Error: "ReferenceError: X is not defined"
```
Location: Browser console
Solution: Define the variable/function or import it
Time: 2 minutes
```

### Error: "Unexpected token"
```
Location: Line number shown
Solution: Check for missing brackets, quotes, semicolons
Time: 1 minute
```

---

## Debugging Checklist

### Before Investigating

- [ ] Saved all files?
- [ ] Dev server running?
- [ ] Browser refreshed?
- [ ] No unsaved changes?

### Investigation Steps

- [ ] Run `npx tsc --noEmit`
- [ ] Check browser console (F12)
- [ ] Check Vite terminal
- [ ] Look for error messages
- [ ] Read error carefully
- [ ] Find the line number
- [ ] Go to that line in code
- [ ] Understand what's wrong
- [ ] Apply fix
- [ ] Restart dev server
- [ ] Refresh browser
- [ ] Verify fix works

### After Fix

- [ ] No TypeScript errors?
- [ ] No console errors?
- [ ] UI renders correctly?
- [ ] All features work?
- [ ] Ready to commit?

---

## Common Fixes

### Fix 1: Move Function Definition
```typescript
// Move from line 2500 to line 100
const addLog = () => { ... };
```

### Fix 2: Add Missing Import
```typescript
import { addLog } from "./utils";
```

### Fix 3: Initialize Variable
```typescript
const [logs, setLogs] = useState([]); // Initialize
```

### Fix 4: Add Dependency
```typescript
useCallback(() => { ... }, [addLog]); // Add dependency
```

### Fix 5: Fix Syntax
```typescript
// Add missing bracket, quote, semicolon
const func = () => { ... }; // ✅ Correct
```

---

## Time Estimates

| Issue | Detection | Fix | Total |
|-------|-----------|-----|-------|
| Function order | 30 sec | 2 min | 2.5 min |
| Missing import | 1 min | 1 min | 2 min |
| Syntax error | 30 sec | 1 min | 1.5 min |
| Undefined object | 1 min | 2 min | 3 min |
| Type mismatch | 1 min | 3 min | 4 min |

**Average: 2-3 minutes to fix**

---

## Prevention

### Daily Routine

```bash
# Before committing
npx tsc --noEmit
npm run lint
npm run build

# Before pushing
npm run validate
```

### Weekly Routine

```bash
# Full validation
npm install
npm run build
npm run test
```

---

## When to Ask for Help

🆘 **Ask for help if:**
- Error message is unclear
- Multiple errors at once
- Error persists after fixes
- Don't understand the error
- Tried all steps, still broken

📝 **Provide when asking:**
- Full error message
- Line number
- Code snippet
- Steps to reproduce
- What you've tried

---

## Summary

**Most blank screen issues are function definition order problems!**

**Quick fix:**
1. Run `npx tsc --noEmit`
2. Look for "used before" errors
3. Move function definition earlier
4. Restart dev server
5. Done! ✅


