#!/usr/bin/env python3
"""
Test if saved auth state works in a visible Playwright browser.

This script:
1. Loads the saved auth_state.json
2. Opens a VISIBLE Chrome browser with the auth state
3. Navigates to Tekion
4. Waits for you to inspect the page
5. Checks if you got redirected to Okta (auth failed) or stayed on Tekion (auth worked)

If you get redirected to Okta → auth state is being rejected server-side
If you stay on Tekion → auth state works!
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

AUTH_STATE_FILE = Path(__file__).parent.parent / "backend" / "auth_state.json"
TEST_URL = "https://preprodapp.tekioncloud.com/home"

async def test_auth_state():
    print("=" * 60)
    print("🧪 TESTING SAVED AUTH STATE IN VISIBLE BROWSER")
    print("=" * 60)
    print()
    
    # Check if auth state exists
    if not AUTH_STATE_FILE.exists():
        print("❌ ERROR: No saved auth state found!")
        print(f"   Expected file: {AUTH_STATE_FILE}")
        print()
        print("💡 Run this first:")
        print("   1. Go to Auth Data tab in the tool")
        print("   2. Click 'Login & Save Auth State'")
        print("   3. Complete login + select dealer")
        print("   4. Then run this script again")
        return
    
    # Load and analyze auth state
    print(f"📂 Loading auth state from: {AUTH_STATE_FILE}")
    with open(AUTH_STATE_FILE, 'r') as f:
        state = json.load(f)
    
    cookies = state.get('cookies', [])
    origins = state.get('origins', [])
    
    print(f"   ✅ Found {len(cookies)} cookies")
    
    # Count localStorage items
    ls_count = 0
    for origin in origins:
        ls_count += len(origin.get('localStorage', []))
    print(f"   ✅ Found {ls_count} localStorage items")
    print()
    
    # Check for Tekion-specific tokens
    print("🔍 Checking for Tekion-specific tokens...")
    tekion_tokens = []
    for origin in origins:
        for item in origin.get('localStorage', []):
            name = item.get('name', '')
            if name in ['t_token', 'dse_t_user', 't_user', 'expiryTime']:
                tekion_tokens.append(name)
                value = item.get('value', '')
                truncated = value[:50] + '...' if len(value) > 50 else value
                print(f"   ✅ {name}: {truncated}")
    
    if not tekion_tokens:
        print("   ⚠️  WARNING: No Tekion tokens found!")
        print("   💡 This might mean auth state was saved too early")
    print()
    
    # Start Playwright
    print("🚀 Starting Playwright...")
    playwright = await async_playwright().start()
    
    # Launch VISIBLE browser with saved auth state
    print("🌐 Opening Chrome browser with saved auth state...")
    browser = await playwright.chromium.launch(
        headless=False,
        channel="chrome",
        args=[
            '--disable-blink-features=AutomationControlled',
        ]
    )
    
    # Create context with saved auth state
    context = await browser.new_context(
        storage_state=str(AUTH_STATE_FILE),
        viewport={'width': 1600, 'height': 900},
        locale='en-US',
        timezone_id='America/New_York',
    )
    
    page = await context.new_page()
    
    print(f"📍 Navigating to: {TEST_URL}")
    print()
    await page.goto(TEST_URL, wait_until='domcontentloaded', timeout=60000)
    
    # Wait a bit for page to load
    print("⏳ Waiting 5 seconds for page to load...")
    await asyncio.sleep(5)
    
    # Check current URL
    current_url = page.url
    print()
    print("=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    print(f"Current URL: {current_url}")
    print()
    
    # Check if redirected to Okta
    if 'okta' in current_url.lower() or 'login' in current_url.lower():
        print("❌ FAILED: Redirected to Okta/Login page!")
        print()
        print("🔍 This means:")
        print("   • Your saved auth state is being REJECTED by the server")
        print("   • Possible reasons:")
        print("     1. Session expired")
        print("     2. Dealer selection was not completed")
        print("     3. Device binding (Okta requires same device)")
        print("     4. IP address changed")
        print("     5. Session was invalidated server-side")
        print()
        print("💡 Solutions:")
        print("   1. Re-save auth state (make sure to select dealer!)")
        print("   2. Wait 2-3 minutes after dealer selection before closing")
        print("   3. Run this test immediately after saving auth state")
        print("   4. Check if IT requires non-MFA automation account")
    else:
        print("✅ SUCCESS: Stayed on Tekion page!")
        print()
        
        # Check for errors on the page
        try:
            error_check = await page.evaluate("""
                () => {
                    const bodyText = document.body.innerText;
                    return {
                        hasRoleChangeError: bodyText.includes('Your role has been changed'),
                        hasUnableToFetchError: bodyText.includes('Unable to fetch'),
                        hasJSONError: bodyText.includes('Unexpected token') || bodyText.includes('valid JSON'),
                        title: document.title
                    };
                }
            """)
            
            print(f"📄 Page title: {error_check['title']}")
            print()
            
            if error_check['hasRoleChangeError']:
                print("⚠️  WARNING: 'Your role has been changed' error detected!")
                print("   💡 Auth state was likely saved before dealer selection")
            elif error_check['hasUnableToFetchError']:
                print("⚠️  WARNING: 'Unable to fetch' error detected!")
                print("   💡 Dealer context might be incomplete")
            elif error_check['hasJSONError']:
                print("⚠️  WARNING: JSON parsing error detected!")
            else:
                print("✅ No errors detected on the page!")
                print()
                print("🎉 Auth state is working correctly!")
                print("   Your screenshots should work now!")
        except Exception as e:
            print(f"⚠️  Could not check for errors: {e}")
    
    print()
    print("=" * 60)
    print("👀 INSPECT THE BROWSER WINDOW")
    print("=" * 60)
    print("The browser will stay open for 60 seconds.")
    print("Check if:")
    print("  • You see the Tekion dashboard (good!)")
    print("  • You see the Okta login page (bad!)")
    print("  • You see any error messages")
    print("  • You see dealer information")
    print()
    print("Press Ctrl+C to close early, or wait 60 seconds...")
    
    try:
        await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    
    print()
    print("🔒 Closing browser...")
    await browser.close()
    await playwright.stop()
    
    print("✅ Test complete!")
    print()

if __name__ == "__main__":
    asyncio.run(test_auth_state())

