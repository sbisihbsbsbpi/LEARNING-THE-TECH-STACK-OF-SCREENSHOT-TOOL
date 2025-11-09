#!/usr/bin/env python3
"""
Advanced Stealth Test for Zomato
Uses all available anti-detection techniques

⚠️  ETHICAL USE ONLY:
- For authorized testing purposes
- To understand bot detection mechanisms
- To improve your own detection systems
"""

import asyncio
import random

# Use rebrowser-playwright (has built-in stealth patches)
try:
    from rebrowser_playwright.async_api import async_playwright
    print("🚀 Using Rebrowser Playwright (with stealth patches)")
    USING_REBROWSER = True
except ImportError:
    from playwright.async_api import async_playwright
    print("⚠️  Using standard Playwright (less stealthy)")
    USING_REBROWSER = False

async def test_zomato_stealth():
    """
    Test Zomato with maximum stealth configuration
    """
    
    url = "https://www.zomato.com/restaurants-near-me"
    
    print(f"\n{'=' * 70}")
    print(f"🥷 Advanced Stealth Test: Zomato")
    print(f"{'=' * 70}\n")
    
    async with async_playwright() as p:
        print("🔧 Launching browser with stealth configuration...")
        
        # Launch with stealth args
        browser = await p.chromium.launch(
            headless=False,  # Headed mode is less detectable
            slow_mo=50,  # Human-like speed
            args=[
                # Disable automation flags
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                
                # Disable dev tools
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--no-sandbox',
                
                # Realistic window size
                '--window-size=1920,1080',
                
                # Disable automation extensions
                '--disable-extensions',
                '--disable-plugins-discovery',
                
                # GPU settings
                '--disable-gpu',
                '--disable-software-rasterizer',
                
                # Network settings
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
            ]
        )
        
        # Create context with realistic fingerprint
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            screen={'width': 1920, 'height': 1080},
            
            # Realistic user agent (latest Chrome on Mac)
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            
            # Locale and timezone
            locale='en-US',
            timezone_id='America/New_York',
            
            # Geolocation (optional - set to your location)
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            permissions=['geolocation'],
            
            # Realistic headers
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            },
            
            # Color scheme
            color_scheme='light',
            
            # Device scale factor
            device_scale_factor=2,
            
            # Has touch (for mobile-like behavior)
            has_touch=False,
            
            # Is mobile
            is_mobile=False,
        )
        
        # Override navigator properties to hide automation
        await context.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override chrome property
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Add realistic platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'MacIntel'
            });
            
            // Add realistic hardware concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            
            // Add realistic device memory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
        """)
        
        page = await context.new_page()
        
        print("✅ Browser launched with stealth configuration")
        print(f"   • Headless: False (visible browser)")
        print(f"   • User Agent: Chrome 131 on macOS")
        print(f"   • Viewport: 1920x1080")
        print(f"   • Automation flags: Disabled")
        print(f"   • Navigator.webdriver: Hidden")
        print()
        
        # Test 1: Direct navigation
        print("1️⃣  Test 1: Direct navigation to Zomato...")
        try:
            # Add random delay before navigation (human-like)
            await asyncio.sleep(random.uniform(1, 3))
            
            # Navigate with timeout
            response = await page.goto(
                url,
                wait_until='domcontentloaded',
                timeout=30000
            )
            
            print(f"   ✅ Navigation successful!")
            print(f"   📊 Status: {response.status}")
            print(f"   📄 Title: {await page.title()}")
            print(f"   🔗 URL: {page.url}")
            
            # Wait for content to load
            await page.wait_for_timeout(2000)
            
            # Take screenshot
            await page.screenshot(path='bot_test_artifacts/zomato_stealth_test1.png', full_page=True)
            print(f"   📸 Screenshot saved: bot_test_artifacts/zomato_stealth_test1.png")
            
            # Check for bot detection indicators
            content = await page.content()
            if any(indicator in content.lower() for indicator in ['captcha', 'blocked', 'access denied', 'forbidden']):
                print(f"   ⚠️  Bot detection indicators found in page content")
            else:
                print(f"   ✅ No obvious bot detection indicators")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            if 'ERR_HTTP2_PROTOCOL_ERROR' in str(e):
                print(f"   💡 HTTP2 protocol error - likely bot detection at network level")
            elif 'Timeout' in str(e):
                print(f"   💡 Timeout - page may be blocking or loading slowly")
            else:
                print(f"   💡 Unknown error - check error message above")
        
        # Test 2: Visit homepage first, then navigate
        print("\n2️⃣  Test 2: Visit homepage first, then navigate...")
        try:
            # Close previous page
            await page.close()
            page = await context.new_page()
            
            # Visit homepage first
            print("   📍 Loading homepage: https://www.zomato.com")
            await asyncio.sleep(random.uniform(1, 2))
            
            await page.goto('https://www.zomato.com', wait_until='domcontentloaded', timeout=30000)
            print(f"   ✅ Homepage loaded: {await page.title()}")
            
            # Simulate human behavior - scroll a bit
            await page.evaluate('window.scrollTo(0, 300)')
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Now navigate to target page
            print(f"   📍 Navigating to: {url}")
            await asyncio.sleep(random.uniform(1, 2))
            
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            print(f"   ✅ Target page loaded: {await page.title()}")
            
            # Wait and take screenshot
            await page.wait_for_timeout(2000)
            await page.screenshot(path='bot_test_artifacts/zomato_stealth_test2.png', full_page=True)
            print(f"   📸 Screenshot saved: bot_test_artifacts/zomato_stealth_test2.png")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        await browser.close()
    
    print(f"\n{'=' * 70}")
    print("🏁 Stealth testing complete!")
    print(f"{'=' * 70}\n")
    
    print("📊 Results:")
    print("   • Check screenshots in bot_test_artifacts/")
    print("   • If Test 1 failed: Network-level bot detection")
    print("   • If Test 2 worked: Homepage visit helps establish session")
    print()
    print("💡 Next steps:")
    print("   • If both failed: Zomato has strong bot detection")
    print("   • If one worked: Use that approach in your scenarios")
    print("   • Consider: Getting authorization from Zomato for testing")

if __name__ == '__main__':
    asyncio.run(test_zomato_stealth())

