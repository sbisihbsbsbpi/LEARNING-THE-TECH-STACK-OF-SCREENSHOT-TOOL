# 🤖 Automated Error Detection & Prevention

## Pre-Commit Hooks

### Setup Git Hooks

```bash
# Create pre-commit hook
mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "🔍 Running pre-commit checks..."

# Check TypeScript
echo "📋 Checking TypeScript..."
cd screenshot-app/frontend
npx tsc --noEmit
if [ $? -ne 0 ]; then
  echo "❌ TypeScript errors found!"
  exit 1
fi

# Check for unused variables
echo "🧹 Checking for unused variables..."
npx tsc --noUnusedLocals --noUnusedParameters --noEmit
if [ $? -ne 0 ]; then
  echo "⚠️  Unused variables found (warnings only)"
fi

echo "✅ All checks passed!"
exit 0
EOF

chmod +x .git/hooks/pre-commit
```

### Setup Pre-Push Hook

```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

echo "🚀 Running pre-push checks..."

# Build frontend
echo "🔨 Building frontend..."
cd screenshot-app/frontend
npm run build
if [ $? -ne 0 ]; then
  echo "❌ Build failed!"
  exit 1
fi

# Build backend (if applicable)
echo "🔨 Checking backend..."
cd ../backend
python -m py_compile *.py
if [ $? -ne 0 ]; then
  echo "❌ Backend syntax errors!"
  exit 1
fi

echo "✅ Ready to push!"
exit 0
EOF

chmod +x .git/hooks/pre-push
```

---

## VSCode Settings

### .vscode/settings.json

```json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": true
    }
  },
  "typescript.preferences.quotePreference": "single",
  "typescript.preferences.importModuleSpecifierPreference": "relative",
  "editor.rulers": [80, 120],
  "editor.wordWrap": "on"
}
```

### .vscode/extensions.json

```json
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-typescript-next",
    "orta.vscode-twoslash-queries"
  ]
}
```

---

## ESLint Configuration

### .eslintrc.json

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "plugins": ["react", "@typescript-eslint"],
  "rules": {
    "no-unused-vars": "off",
    "@typescript-eslint/no-unused-vars": [
      "warn",
      {
        "argsIgnorePattern": "^_",
        "varsIgnorePattern": "^_"
      }
    ],
    "@typescript-eslint/no-explicit-any": "warn",
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off"
  }
}
```

---

## GitHub Actions CI/CD

### .github/workflows/typescript-check.yml

```yaml
name: TypeScript Check

on: [push, pull_request]

jobs:
  typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd screenshot-app/frontend
          npm install
      
      - name: Run TypeScript check
        run: |
          cd screenshot-app/frontend
          npx tsc --noEmit
      
      - name: Build
        run: |
          cd screenshot-app/frontend
          npm run build
```

---

## Manual Verification Commands

### Daily Development

```bash
# Check TypeScript (run before committing)
npm run type-check

# Check for errors
npm run lint

# Build and test
npm run build

# Full validation
npm run validate
```

### Add to package.json

```json
{
  "scripts": {
    "type-check": "tsc --noEmit",
    "type-check:strict": "tsc --noEmit --strict",
    "lint": "eslint src/",
    "lint:fix": "eslint src/ --fix",
    "validate": "npm run type-check && npm run lint && npm run build"
  }
}
```

---

## IDE Warnings to Watch For

### In VSCode

- Red squiggly lines = errors
- Yellow squiggly lines = warnings
- Orange squiggly lines = suggestions

**Don't ignore red lines!** They indicate real problems.

### Quick Actions

- `Cmd+.` (Mac) or `Ctrl+.` (Windows) = Show quick fixes
- `Cmd+Shift+P` = Command palette
- Type "TypeScript: Restart TS Server" if stuck

---

## Debugging Workflow

### When You See Blank Screen

```bash
# Step 1: Check TypeScript
npx tsc --noEmit

# Step 2: Check browser console
# Open DevTools (F12) and look for errors

# Step 3: Check Vite server
# Look at terminal running "npm run dev"

# Step 4: Check for runtime errors
# Add console.log statements to track execution

# Step 5: Rebuild
npm run build

# Step 6: Clear cache
rm -rf node_modules/.vite
npm run dev
```

---

## Common Issues & Fixes

| Issue | Command | Fix |
|-------|---------|-----|
| TypeScript errors | `npx tsc --noEmit` | Fix errors shown |
| Unused variables | `npx tsc --noUnusedLocals` | Remove or prefix with `_` |
| Build fails | `npm run build` | Check error messages |
| Vite not updating | `npm run dev` | Restart dev server |
| Blank screen | `F12` console | Check for JS errors |

---

## Best Practices

✅ **DO:**
- Run `npm run validate` before committing
- Check TypeScript errors daily
- Use pre-commit hooks
- Enable strict mode in tsconfig.json
- Review warnings, not just errors

❌ **DON'T:**
- Ignore TypeScript errors
- Use `any` type everywhere
- Skip type checking
- Commit with red squiggly lines
- Disable ESLint rules without reason

---

## Summary

**Automated checks catch errors BEFORE they reach production!**

Use:
1. Pre-commit hooks (local)
2. ESLint (real-time)
3. TypeScript (compile-time)
4. GitHub Actions (CI/CD)
5. Manual validation (before push)


