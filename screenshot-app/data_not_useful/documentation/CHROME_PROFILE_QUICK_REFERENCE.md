# 🖥️ Chrome Profile - Quick Reference

---

## 📍 Two Chrome Profiles

### Original Profile (Your Real Chrome)
```
Location: ~/Library/Application Support/Google/Chrome
Contains: All your logins, cookies, extensions
Used for: Your daily browsing
Status: NEVER modified by tool
```

### Duplicate Profile (For Screenshot Tool)
```
Location: ~/Library/Application Support/Google/Chrome-Debug
Contains: Copy of all your logins, cookies, extensions
Used for: Screenshot tool's "Real Browser" mode
Status: Updated manually by you
```

---

## 🔄 How It Works

```
Your Chrome (Original)
    ↓
    ├─→ You use it normally (daily browsing)
    │
    └─→ Run: ./setup-chrome-profile.sh
        ↓
        Creates copy
        ↓
        Chrome-Debug Profile (Duplicate)
        ↓
        Run: ./launch-chrome-debug.sh
        ↓
        Chrome launches with debug profile
        ↓
        Screenshot tool connects via CDP
        ↓
        Takes screenshots with your logins
```

---

## ⚡ Quick Commands

### First Time Setup
```bash
# 1. Close Chrome
Cmd+Q

# 2. Create debug profile (one-time)
./setup-chrome-profile.sh

# 3. Launch Chrome with debug profile
./launch-chrome-debug.sh
```

### Regular Use
```bash
# 1. Log into websites in your Chrome
# 2. Update debug profile with new logins
./setup-chrome-profile.sh

# 3. Launch Chrome
./launch-chrome-debug.sh

# 4. Use screenshot tool with "Real Browser" mode
```

---

## 📊 Profile Comparison

| Feature | Original | Duplicate |
|---------|----------|-----------|
| **Location** | `Chrome/` | `Chrome-Debug/` |
| **Logins** | ✅ All yours | ✅ Copy of yours |
| **Cookies** | ✅ All yours | ✅ Copy of yours |
| **Extensions** | ✅ All yours | ✅ Copy of yours |
| **Modified by tool** | ❌ NO | ✅ YES (by setup script) |
| **Used for** | Daily browsing | Screenshot tool |
| **Auto-updated** | ✅ YES | ❌ NO (manual) |

---

## 🎯 Why Two Profiles?

1. **Safety** - Original profile is protected
2. **Isolation** - Separate environments
3. **Consistency** - All logins available
4. **Flexibility** - Easy to update

---

## 🔐 Important

### Original Profile
- ✅ NEVER modified by tool
- ✅ Your daily browsing is safe
- ✅ Can use Chrome normally

### Duplicate Profile
- ✅ Copy of original
- ✅ Used only by screenshot tool
- ✅ Updated manually by you

---

## 📁 File Locations

```
Original:  ~/Library/Application Support/Google/Chrome
Duplicate: ~/Library/Application Support/Google/Chrome-Debug
```

---

## 🔄 Update Process

**When to update**:
- New logins
- New extensions
- Password changes
- New cookies

**How to update**:
```bash
./setup-chrome-profile.sh
```

---

## ✅ Checklist

- [ ] Original Chrome profile exists
- [ ] Run `./setup-chrome-profile.sh` (creates duplicate)
- [ ] Run `./launch-chrome-debug.sh` (launches Chrome)
- [ ] Use screenshot tool with "Real Browser" mode
- [ ] Screenshots work with your logins

---

## 🚀 Status

**Original Profile**: ✅ Safe and untouched  
**Duplicate Profile**: ✅ Ready to use  
**Screenshot Tool**: ✅ Ready to capture

---


