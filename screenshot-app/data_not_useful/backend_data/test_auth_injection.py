"""
🔍 Authentication Injection Test Script

This script tests whether cookies and localStorage are being properly injected
into headless browser sessions.

Usage:
    python3 test_auth_injection.py
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def test_auth_injection():
    """Test if auth state is properly injected in headless mode"""
    
    print("=" * 80)
    print("🔍 AUTHENTICATION INJECTION TEST")
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
    
    # Show critical cookies
    critical_cookies = ['t_token', 'JSESSIONID', 'idx', 'DT', 'tcookie']
    print(f"\n🔑 Critical Cookies:")
    for cookie in auth_state.get('cookies', []):
        if cookie['name'] in critical_cookies:
            value_preview = cookie['value'][:50] + "..." if len(cookie['value']) > 50 else cookie['value']
            print(f"   ✅ {cookie['name']}: {value_preview}")
            print(f"      Domain: {cookie['domain']}, Expires: {cookie.get('expires', 'session')}")
    
    # Show localStorage
    print(f"\n💾 LocalStorage:")
    for origin in auth_state.get('origins', []):
        print(f"   Origin: {origin['origin']}")
        for item in origin.get('localStorage', []):
            if item['name'] in ['t_token', 't_user', 'dse_t_user']:
                value_preview = item['value'][:80] + "..." if len(item['value']) > 80 else item['value']
                print(f"      ✅ {item['name']}: {value_preview}")
    
    # Test URL
    test_url = "https://preprodapp.tekioncloud.com/home"
    
    print(f"\n" + "=" * 80)
    print(f"🚀 LAUNCHING HEADLESS BROWSER TEST")
    print(f"=" * 80)
    print(f"📍 Test URL: {test_url}")
    
    # Launch Playwright
    playwright = await async_playwright().start()
    
    # Test 1: With storage_state parameter
    print(f"\n" + "-" * 80)
    print(f"TEST 1: Using storage_state parameter (Playwright's built-in method)")
    print(f"-" * 80)
    
    browser = await playwright.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    
    context = await browser.new_context(
        storage_state=str(auth_state_path),
        viewport={'width': 1920, 'height': 1080}
    )
    
    page = await context.new_page()
    
    # Check cookies BEFORE navigation
    print(f"\n📋 Cookies BEFORE navigation:")
    cookies_before = await context.cookies()
    tekion_cookies_before = [c for c in cookies_before if 'tekion' in c['domain']]
    print(f"   Total cookies: {len(cookies_before)}")
    print(f"   Tekion cookies: {len(tekion_cookies_before)}")
    for cookie in tekion_cookies_before:
        print(f"      ✅ {cookie['name']} ({cookie['domain']})")
    
    # Navigate to page
    print(f"\n🌐 Navigating to {test_url}...")
    try:
        response = await page.goto(test_url, wait_until='networkidle', timeout=30000)
        print(f"   ✅ Page loaded: {response.status} {response.status_text}")
        print(f"   📍 Final URL: {page.url}")
    except Exception as e:
        print(f"   ❌ Navigation failed: {e}")
    
    # Check cookies AFTER navigation
    print(f"\n📋 Cookies AFTER navigation:")
    cookies_after = await context.cookies()
    tekion_cookies_after = [c for c in cookies_after if 'tekion' in c['domain']]
    print(f"   Total cookies: {len(cookies_after)}")
    print(f"   Tekion cookies: {len(tekion_cookies_after)}")
    
    # Check localStorage
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
        for key in ['t_token', 't_user', 'dse_t_user', 'currentActiveDealerId']:
            if key in local_storage:
                value_preview = local_storage[key][:80] + "..." if len(local_storage[key]) > 80 else local_storage[key]
                print(f"      ✅ {key}: {value_preview}")
            else:
                print(f"      ❌ {key}: NOT FOUND")
    except Exception as e:
        print(f"   ❌ Failed to read localStorage: {e}")
    
    # Check sessionStorage
    print(f"\n🔐 SessionStorage AFTER navigation:")
    try:
        session_storage = await page.evaluate("""
            () => {
                const data = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    data[key] = sessionStorage.getItem(key);
                }
                return data;
            }
        """)
        print(f"   Total items: {len(session_storage)}")
        if len(session_storage) > 0:
            for key, value in list(session_storage.items())[:5]:  # Show first 5
                value_preview = value[:80] + "..." if len(value) > 80 else value
                print(f"      ✅ {key}: {value_preview}")
        else:
            print(f"      ⚠️  SessionStorage is EMPTY (this is expected - Playwright doesn't persist sessionStorage)")
    except Exception as e:
        print(f"   ❌ Failed to read sessionStorage: {e}")
    
    # Check if we're authenticated
    print(f"\n🔍 Authentication Check:")
    try:
        # Check if we're on login page or authenticated page
        current_url = page.url
        if 'login' in current_url.lower() or 'auth' in current_url.lower():
            print(f"   ❌ REDIRECTED TO LOGIN PAGE")
            print(f"   📍 Current URL: {current_url}")
            print(f"   ⚠️  Authentication FAILED - cookies/tokens not working")
        elif 'home' in current_url.lower() or 'dashboard' in current_url.lower():
            print(f"   ✅ AUTHENTICATED SUCCESSFULLY")
            print(f"   📍 Current URL: {current_url}")
            print(f"   ✅ Cookies and tokens are working!")
        else:
            print(f"   ⚠️  UNKNOWN STATE")
            print(f"   📍 Current URL: {current_url}")
            
        # Take screenshot for visual verification
        screenshot_path = Path("screenshots/auth_test_headless.png")
        screenshot_path.parent.mkdir(exist_ok=True)
        await page.screenshot(path=str(screenshot_path), full_page=False)
        print(f"\n📸 Screenshot saved: {screenshot_path}")
        
    except Exception as e:
        print(f"   ❌ Auth check failed: {e}")
    
    await browser.close()
    
    # Test 2: Manual cookie injection
    print(f"\n" + "-" * 80)
    print(f"TEST 2: Manual cookie injection (alternative method)")
    print(f"-" * 80)
    
    browser2 = await playwright.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    
    context2 = await browser2.new_context(
        viewport={'width': 1920, 'height': 1080}
    )
    
    # Manually add cookies
    print(f"\n🍪 Manually adding cookies...")
    await context2.add_cookies(auth_state['cookies'])
    print(f"   ✅ Added {len(auth_state['cookies'])} cookies")
    
    page2 = await context2.new_page()
    
    # Navigate to page first
    print(f"\n🌐 Navigating to {test_url}...")
    try:
        await page2.goto(test_url, wait_until='domcontentloaded', timeout=10000)
        print(f"   ✅ Page loaded")
    except Exception as e:
        print(f"   ⚠️  Initial navigation: {e}")
    
    # Inject localStorage
    print(f"\n💾 Injecting localStorage...")
    for origin in auth_state.get('origins', []):
        if origin['origin'] in test_url:
            for item in origin.get('localStorage', []):
                try:
                    await page2.evaluate(f"""
                        () => {{
                            localStorage.setItem({json.dumps(item['name'])}, {json.dumps(item['value'])});
                        }}
                    """)
                except Exception as e:
                    print(f"   ❌ Failed to set {item['name']}: {e}")
            print(f"   ✅ Injected {len(origin.get('localStorage', []))} localStorage items")
    
    # Reload page to apply localStorage
    print(f"\n🔄 Reloading page to apply localStorage...")
    try:
        await page2.reload(wait_until='networkidle', timeout=30000)
        print(f"   ✅ Page reloaded")
        print(f"   📍 Final URL: {page2.url}")
    except Exception as e:
        print(f"   ❌ Reload failed: {e}")
    
    # Check authentication
    current_url2 = page2.url
    if 'login' in current_url2.lower() or 'auth' in current_url2.lower():
        print(f"\n   ❌ MANUAL INJECTION FAILED - still on login page")
    elif 'home' in current_url2.lower() or 'dashboard' in current_url2.lower():
        print(f"\n   ✅ MANUAL INJECTION SUCCESSFUL - authenticated!")
    else:
        print(f"\n   ⚠️  UNKNOWN STATE: {current_url2}")
    
    # Take screenshot
    screenshot_path2 = Path("screenshots/auth_test_manual.png")
    await page2.screenshot(path=str(screenshot_path2), full_page=False)
    print(f"   📸 Screenshot saved: {screenshot_path2}")
    
    await browser2.close()
    await playwright.stop()
    
    print(f"\n" + "=" * 80)
    print(f"✅ TEST COMPLETE")
    print(f"=" * 80)
    print(f"\n📊 Summary:")
    print(f"   - Check screenshots in screenshots/ directory")
    print(f"   - If redirected to login: cookies/tokens are NOT working")
    print(f"   - If showing home/dashboard: cookies/tokens ARE working")
    print(f"\n💡 Next Steps:")
    print(f"   1. Review the screenshots to see what page loaded")
    print(f"   2. Check if sessionStorage is needed (it's not persisted by Playwright)")
    print(f"   3. Consider using persistent browser context for better auth persistence")


if __name__ == "__main__":
    asyncio.run(test_auth_injection())

