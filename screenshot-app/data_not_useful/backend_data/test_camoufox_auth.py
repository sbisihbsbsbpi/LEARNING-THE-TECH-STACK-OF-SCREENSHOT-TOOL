"""
🦊 Test authentication injection with Camoufox (headless mode)

This script tests if the enhanced localStorage injection works with Camoufox.
"""

import asyncio
import json
from pathlib import Path
from camoufox.async_api import AsyncCamoufox


async def test_camoufox_auth():
    """Test if auth state works with Camoufox headless mode"""
    
    print("=" * 80)
    print("🦊 CAMOUFOX AUTHENTICATION TEST (Headless Mode)")
    print("=" * 80)
    
    # Load auth state
    auth_state_path = Path("auth_state.json")
    if not auth_state_path.exists():
        print("❌ auth_state.json not found!")
        return
    
    with open(auth_state_path, 'r') as f:
        auth_state = json.load(f)
    
    print(f"\n✅ Loaded auth_state.json")
    print(f"   📊 Cookies: {len(auth_state.get('cookies', []))} found")
    print(f"   📊 Origins: {len(auth_state.get('origins', []))} found")
    
    # Extract localStorage for Tekion
    ls_data = {}
    for origin in auth_state.get('origins', []):
        if 'preprodapp.tekioncloud.com' in origin['origin']:
            for item in origin.get('localStorage', []):
                ls_data[item['name']] = item['value']
    
    print(f"   💾 LocalStorage items: {len(ls_data)}")
    
    # Test URL
    test_url = "https://preprodapp.tekioncloud.com/home"
    
    print(f"\n" + "=" * 80)
    print(f"🚀 LAUNCHING CAMOUFOX (HEADLESS MODE)")
    print(f"=" * 80)
    print(f"📍 Test URL: {test_url}")
    
    # Launch Camoufox
    async with AsyncCamoufox(
        headless=True,
        humanize=True,
    ) as browser:
        print(f"\n✅ Camoufox browser launched (headless)")
        
        # Create context with storage_state
        context = await browser.new_context(
            storage_state=str(auth_state_path),
            viewport={'width': 1920, 'height': 1080}
        )
        
        print(f"✅ Browser context created with storage_state")
        
        # ✅ ENHANCED: Inject localStorage using official Playwright pattern
        print(f"\n💾 Injecting localStorage using enhanced method...")
        await context.add_init_script("""
            (storage) => {
                if (window.location.hostname === 'preprodapp.tekioncloud.com' ||
                    window.location.hostname.includes('tekion')) {
                    console.log('[AUTH TEST] Injecting localStorage...');
                    for (const [key, value] of Object.entries(storage)) {
                        window.localStorage.setItem(key, value);
                        console.log('[AUTH TEST] Set:', key);
                    }
                    console.log('[AUTH TEST] localStorage injection complete!');
                }
            }
        """, ls_data)
        print(f"   ✅ Enhanced localStorage injection configured")
        
        page = await context.new_page()
        
        # Check cookies BEFORE navigation
        print(f"\n📋 Cookies BEFORE navigation:")
        cookies_before = await context.cookies()
        tekion_cookies_before = [c for c in cookies_before if 'tekion' in c['domain']]
        print(f"   Total cookies: {len(cookies_before)}")
        print(f"   Tekion cookies: {len(tekion_cookies_before)}")
        
        # Navigate to page
        print(f"\n🌐 Navigating to {test_url}...")
        try:
            response = await page.goto(test_url, wait_until='networkidle', timeout=30000)
            print(f"   ✅ Page loaded: {response.status} {response.status_text}")
            print(f"   📍 Final URL: {page.url}")
        except Exception as e:
            print(f"   ❌ Navigation failed: {e}")
        
        # Check localStorage AFTER navigation
        print(f"\n💾 LocalStorage AFTER navigation:")
        try:
            local_storage = await page.evaluate("""
                () => {
                    const data = {};
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        data[key] = localStorage.getItem(key);
                    }
                    return data;
                }
            """)
            print(f"   Total items: {len(local_storage)}")
            
            # Check critical auth tokens
            auth_tokens = ['t_token', 't_user', 'dse_t_user', 'currentActiveDealerId']
            found_tokens = 0
            for key in auth_tokens:
                if key in local_storage:
                    value_preview = local_storage[key][:80] + "..." if len(local_storage[key]) > 80 else local_storage[key]
                    print(f"      ✅ {key}: {value_preview}")
                    found_tokens += 1
                else:
                    print(f"      ❌ {key}: NOT FOUND")
            
            print(f"\n   📊 Auth tokens found: {found_tokens}/{len(auth_tokens)}")
            
        except Exception as e:
            print(f"   ❌ Failed to read localStorage: {e}")
        
        # Check if we're authenticated
        print(f"\n🔍 Authentication Check:")
        try:
            current_url = page.url
            if 'login' in current_url.lower():
                print(f"   ❌ REDIRECTED TO LOGIN PAGE")
                print(f"   📍 Current URL: {current_url}")
                print(f"   ⚠️  Authentication FAILED")
            elif 'home' in current_url.lower():
                print(f"   ✅ AUTHENTICATED SUCCESSFULLY!")
                print(f"   📍 Current URL: {current_url}")
                
                # Check page content
                page_text = await page.evaluate("() => document.body.innerText")
                if 'Your role has been changed' in page_text:
                    print(f"   ⚠️  WARNING: 'Your role has been changed' message detected")
                    print(f"   💡 This might be a role/session mismatch issue")
                elif 'Username' in page_text or 'Password' in page_text:
                    print(f"   ❌ Login form detected - auth failed")
                else:
                    print(f"   ✅ Dashboard content loaded!")
                    print(f"   📝 Page preview: {page_text[:200]}...")
            else:
                print(f"   ⚠️  UNKNOWN STATE")
                print(f"   📍 Current URL: {current_url}")
            
            # Take screenshot
            screenshot_path = Path("screenshots/camoufox_auth_test.png")
            screenshot_path.parent.mkdir(exist_ok=True)
            await page.screenshot(path=str(screenshot_path), full_page=False)
            print(f"\n📸 Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            print(f"   ❌ Auth check failed: {e}")
    
    print(f"\n" + "=" * 80)
    print(f"✅ TEST COMPLETE")
    print(f"=" * 80)
    print(f"\n📊 Summary:")
    print(f"   - Enhanced localStorage injection implemented")
    print(f"   - Check screenshot: screenshots/camoufox_auth_test.png")
    print(f"   - If auth tokens are found: ✅ Fix is working!")
    print(f"   - If still redirected to login: Need persistent context")


if __name__ == "__main__":
    asyncio.run(test_camoufox_auth())

