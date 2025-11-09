#!/usr/bin/env python3
"""
Test Zomato website to diagnose HTTP2 protocol error
"""

import asyncio

# Try rebrowser-playwright first
try:
    from rebrowser_playwright.async_api import async_playwright
    print("🚀 Using Rebrowser Playwright")
except ImportError:
    from playwright.async_api import async_playwright
    print("⚠️  Using standard Playwright")

async def test_zomato():
    """Test Zomato with different configurations"""
    
    url = "https://www.zomato.com/restaurants-near-me"
    
    print(f"\n{'=' * 70}")
    print(f"🧪 Testing Zomato URL: {url}")
    print(f"{'=' * 70}\n")
    
    async with async_playwright() as p:
        # Test 1: Standard configuration
        print("1️⃣  Test 1: Standard configuration (headed mode)")
        try:
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=100
            )
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                locale='en-US',
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Try with domcontentloaded
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Take screenshot
            await page.screenshot(path="bot_test_artifacts/zomato_test1.png")
            
            print(f"   ✅ Success! Page loaded")
            print(f"   📸 Screenshot saved: bot_test_artifacts/zomato_test1.png")
            print(f"   📄 Title: {await page.title()}")
            
            await browser.close()
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            print(f"   💡 This might be bot detection at network level")
        
        # Test 2: With additional headers
        print("\n2️⃣  Test 2: With additional HTTP headers")
        try:
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=100,
                args=[
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                locale='en-US',
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                }
            )
            
            page = await context.new_page()
            
            # Try with load event
            await page.goto(url, wait_until="load", timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Take screenshot
            await page.screenshot(path="bot_test_artifacts/zomato_test2.png")
            
            print(f"   ✅ Success! Page loaded")
            print(f"   📸 Screenshot saved: bot_test_artifacts/zomato_test2.png")
            print(f"   📄 Title: {await page.title()}")
            
            await browser.close()
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            print(f"   💡 This might be bot detection at network level")
        
        # Test 3: Try homepage first
        print("\n3️⃣  Test 3: Try Zomato homepage first")
        try:
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=100
            )
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                locale='en-US',
            )
            
            page = await context.new_page()
            
            # Try homepage first
            print("   📍 Loading homepage: https://www.zomato.com")
            await page.goto("https://www.zomato.com", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)
            
            print(f"   ✅ Homepage loaded: {await page.title()}")
            
            # Now try the restaurants page
            print(f"   📍 Navigating to: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Take screenshot
            await page.screenshot(path="bot_test_artifacts/zomato_test3.png")
            
            print(f"   ✅ Success! Page loaded")
            print(f"   📸 Screenshot saved: bot_test_artifacts/zomato_test3.png")
            print(f"   📄 Title: {await page.title()}")
            
            await browser.close()
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            print(f"   💡 This might be bot detection at network level")
    
    print(f"\n{'=' * 70}")
    print("🏁 Testing complete!")
    print(f"{'=' * 70}\n")
    
    print("📊 Analysis:")
    print("   • If all tests failed with HTTP2_PROTOCOL_ERROR:")
    print("     → Zomato is blocking automated browsers at network level")
    print("     → This is a TRUE POSITIVE for bot detection")
    print("     → Your bot detection system is working!")
    print()
    print("   • If some tests passed:")
    print("     → Try the successful configuration in your scenarios")
    print()
    print("   • Recommendation:")
    print("     → Use a different test site (example.com, httpbin.org)")
    print("     → Or test Zomato with authorization from their team")

if __name__ == '__main__':
    asyncio.run(test_zomato())

