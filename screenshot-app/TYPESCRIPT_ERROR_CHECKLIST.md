# 🔍 TypeScript Error Identification Checklist

## Quick Diagnosis Guide

### Symptom: Blank Screen / No UI Rendering

**Step 1: Check TypeScript Errors**
```bash
cd screenshot-app/frontend
npx tsc --noEmit
```

**Expected Output (if error exists):**
```
src/App.tsx(1895,35): error TS2454: Variable 'addLog' is used before being assigned.
src/App.tsx(1895,35): error TS2448: Block-scoped variable 'addLog' used before its declaration.
```

**Step 2: Check Browser Console**
- Open DevTools: `F12` or `Cmd+Option+I`
- Look for red errors
- Common errors:
  - `ReferenceError: [function] is not defined`
  - `TypeError: Cannot read property of undefined`

**Step 3: Check Vite Dev Server**
- Look at terminal running `npm run dev`
- Should see: `✓ compiled successfully`
- If errors: `✗ compilation failed`

---

## Common Error Patterns

### Pattern 1: Function Used Before Definition
```typescript
// ❌ WRONG
function App() {
  const handleClick = () => {
    addLog("Clicked"); // addLog not defined yet
  };
  
  const addLog = (msg) => { ... }; // Defined too late
}

// ✅ CORRECT
function App() {
  const addLog = (msg) => { ... }; // Define first
  
  const handleClick = () => {
    addLog("Clicked"); // Now safe
  };
}
```

### Pattern 2: useCallback with Missing Dependencies
```typescript
// ❌ WRONG
const deleteItems = useCallback(() => {
  addLog("Deleting..."); // addLog not in dependency array
}, []); // Missing addLog!

// ✅ CORRECT
const deleteItems = useCallback(() => {
  addLog("Deleting...");
}, [addLog]); // Include in dependencies
```

### Pattern 3: Circular Dependencies
```typescript
// ❌ WRONG
const funcA = () => funcB(); // funcB not defined yet
const funcB = () => funcA(); // funcA defined but circular

// ✅ CORRECT
const funcA = () => {
  if (condition) funcB();
};
const funcB = () => {
  if (condition) funcA();
};
```

---

## Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Variable 'X' is used before being assigned` | Function called before defined | Move definition earlier |
| `Block-scoped variable 'X' used before its declaration` | Same as above | Move definition earlier |
| `Cannot read property 'X' of undefined` | Object/function is undefined | Check if defined before use |
| `'X' is not defined` | Variable/function doesn't exist | Define it or import it |
| `Type 'unknown' is not assignable to type 'X'` | Type mismatch | Add proper type annotation |

---

## Prevention Checklist

Before committing code:

- [ ] Run `npx tsc --noEmit` - no errors?
- [ ] Check browser console (F12) - no red errors?
- [ ] App renders UI - not blank screen?
- [ ] All functions defined before use?
- [ ] All dependencies in useCallback/useEffect?
- [ ] No circular dependencies?
- [ ] All imports present?
- [ ] No unused variables (warnings OK)?

---

## Quick Fixes

### Fix 1: Move Definition Earlier
```typescript
// Move the function definition to the top of the component
// Right after state declarations
```

### Fix 2: Add to Dependency Array
```typescript
useCallback(() => {
  addLog("..."); // If addLog is used
}, [addLog]); // Add it here
```

### Fix 3: Check Imports
```typescript
// Make sure all functions are imported
import { addLog } from "./utils"; // If from external file
```

### Fix 4: Use Optional Chaining
```typescript
// If object might be undefined
const value = obj?.property; // Safe access
```

---

## Testing Commands

```bash
# Check TypeScript
npx tsc --noEmit

# Check for unused variables
npx tsc --noUnusedLocals --noUnusedParameters

# Build for production (catches more errors)
npm run build

# Run linter
npx eslint src/

# Format code
npx prettier --write src/
```

---

## When to Investigate

🚨 **Investigate immediately if:**
- Blank screen appears
- TypeScript errors in console
- `npm run dev` shows compilation failed
- Browser console shows red errors
- App worked before, now doesn't

---

## File Organization Best Practice

```typescript
function App() {
  // 1. State declarations
  const [state, setState] = useState();
  
  // 2. Utility functions (define early!)
  const addLog = (msg) => { ... };
  const clearLogs = () => { ... };
  
  // 3. useEffect hooks
  useEffect(() => { ... }, []);
  
  // 4. Event handlers (can use utilities)
  const handleClick = () => {
    addLog("Clicked");
  };
  
  // 5. Complex functions (useCallback)
  const deleteItems = useCallback(() => {
    addLog("Deleting");
  }, [addLog]);
  
  // 6. Return JSX
  return (
    <div>...</div>
  );
}
```

---

## Summary

**Key Takeaway**: Define functions BEFORE you use them.

**Order matters in React components!**

1. State first
2. Utilities second
3. Effects third
4. Handlers fourth
5. JSX last


