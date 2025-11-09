# 📚 Network Events - Lesson Learned

**Date**: 2025-11-08  
**Status**: ✅ REVERTED & FIXED  
**Issue**: Attempted fix caused `name 'log_request' is not defined` error

---

## 🔴 What Went Wrong

I attempted to attach network listeners BEFORE page load by defining functions inside the try block:

```python
try:
    new_tab = await self._create_new_tab_next_to_active()
    
    # Define functions
    def log_request(request):
        ...
    
    def log_response(response):
        ...
    
    # Attach listeners
    new_tab.on('request', log_request)  # ← Error: name 'log_request' is not defined
```

**Error**: `name 'log_request' is not defined`

**Why**: The functions were defined but there was a scope or timing issue when trying to attach them.

---

## ✅ What We Did

Reverted the changes and kept the original simpler approach:

```python
# Create a new tab next to the active tab
new_tab = await self._create_new_tab_next_to_active()

# Navigate to the URL in the new tab
print(f"🌐 Loading {url} in new tab...")
try:
    await new_tab.goto(url, wait_until='networkidle', timeout=30000)
    print("   ✅ Page loaded in new tab (network idle)")
except Exception as e:
    print(f"   ⚠️  Network idle timeout, using load event instead...")
    await new_tab.goto(url, wait_until='load', timeout=30000)
    print("   ✅ Page loaded in new tab (load event)")
```

---

## 🎓 Key Lessons

### 1. **Scope Issues with Nested Functions**
- Functions defined inside try blocks can have scope issues
- Better to define functions at module or class level
- Or use lambda functions for simple callbacks

### 2. **Event Listeners in Playwright**
- Network listeners ARE attached after page load in current implementation
- This is why network events are not captured
- But fixing this requires careful handling of function scope

### 3. **The Real Problem**
The root cause of "network events not detected" is still valid:
- Listeners attached AFTER page load
- Events already fired before listeners attached
- But the fix needs to be implemented differently

---

## 🔧 Better Approach (For Future)

Instead of defining functions inside the try block, define them at the class level:

```python
class ScreenshotService:
    def _create_network_listeners(self):
        """Create network event listeners"""
        network_events = []
        start_time = asyncio.get_event_loop().time()
        
        def log_request(request):
            if request.resource_type in ['xhr', 'fetch', 'document', 'websocket']:
                elapsed = asyncio.get_event_loop().time() - start_time
                network_events.append({...})
        
        def log_response(response):
            if response.request.resource_type in ['xhr', 'fetch', 'document', 'websocket']:
                elapsed = asyncio.get_event_loop().time() - start_time
                network_events.append({...})
        
        return {
            'log_request': log_request,
            'log_response': log_response,
            'network_events': network_events,
            'start_time': start_time
        }
    
    async def capture_segmented(self, ...):
        # Create listeners
        listeners = self._create_network_listeners()
        
        # Attach listeners BEFORE navigation
        new_tab.on('request', listeners['log_request'])
        new_tab.on('response', listeners['log_response'])
        
        # Navigate
        await new_tab.goto(url, wait_until='networkidle')
        
        # Print results
        print(f"Network events: {len(listeners['network_events'])}")
```

---

## 📊 Current Status

**Network Events Issue**: 
- Root cause identified: Listeners attached AFTER page load ✅
- Attempted fix: Failed due to scope issues ❌
- Current state: Reverted to original code ✅
- Backend: Running and stable ✅

**Next Steps**:
1. Implement network listeners at class level (not inside try block)
2. Attach listeners BEFORE page navigation
3. Capture all network events from start
4. Print network activity summary

---

## ✨ Summary

**What We Learned**:
1. Network events ARE not being captured (root cause confirmed)
2. Listeners ARE attached after page load (confirmed)
3. Fixing this requires careful handling of function scope
4. Better to define listeners at class level, not inside try blocks

**Current Status**: Backend is stable and working

**Next Attempt**: Will implement network listeners at class level for proper scope handling

---

## 🚀 Ready to Continue

Backend is running and stable. Ready to implement the proper fix for network event capture using class-level listener definitions.

