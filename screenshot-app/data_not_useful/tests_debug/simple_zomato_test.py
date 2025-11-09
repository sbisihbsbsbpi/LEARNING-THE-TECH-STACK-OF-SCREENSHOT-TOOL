"""
Simple Zomato Blocking Test
Tests what error we get when trying to access Zomato
"""

import asyncio

try:
    from rebrowser_playwright.async_api import async_playwright
    print("✅ Using Rebrowser Playwright")
except ImportError:
    from playwright.async_api import async_playwright
    print("⚠️  Using Standard Playwright")


async def test_zomato():
    """Test Zomato access and capture the exact error"""
    
    url = "https://www.zomato.com/restaurants-near-me"
    
    print(f"\n{'='*80}")
    print(f"🧪 Testing Zomato Bot Detection")
    print(f"{'='*80}\n")
    print(f"URL: {url}\n")
    
    async with async_playwright() as p:
        # Test 1: Headless without stealth
        print("Test 1: Headless (no stealth)")
        print("-" * 40)
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            response = await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            print(f"✅ SUCCESS - Status: {response.status if response else 'N/A'}")
            await page.screenshot(path="bot_test_artifacts/zomato_test1_headless.png")
            
        except Exception as e:
            error_str = str(e)
            print(f"❌ BLOCKED - Error: {error_str[:200]}")
            
            if 'ERR_HTTP2_PROTOCOL_ERROR' in error_str:
                print(f"   🔍 Detection: HTTP/2 Protocol Fingerprinting")
            elif 'ERR_CONNECTION_REFUSED' in error_str:
                print(f"   🔍 Detection: Connection Refused (Network Block)")
            elif 'timeout' in error_str.lower():
                print(f"   🔍 Detection: Timeout (Rate Limiting)")
                
        finally:
            await browser.close()
        
        print()
        
        # Test 2: Headless with stealth
        print("Test 2: Headless + Stealth")
        print("-" * 40)
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Hide webdriver
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = await context.new_page()
            
            response = await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            print(f"✅ SUCCESS - Status: {response.status if response else 'N/A'}")
            await page.screenshot(path="bot_test_artifacts/zomato_test2_stealth.png")
            
        except Exception as e:
            error_str = str(e)
            print(f"❌ BLOCKED - Error: {error_str[:200]}")
            
            if 'ERR_HTTP2_PROTOCOL_ERROR' in error_str:
                print(f"   🔍 Detection: HTTP/2 Protocol Fingerprinting")
            elif 'ERR_CONNECTION_REFUSED' in error_str:
                print(f"   🔍 Detection: Connection Refused (Network Block)")
            elif 'timeout' in error_str.lower():
                print(f"   🔍 Detection: Timeout (Rate Limiting)")
                
        finally:
            await browser.close()
        
        print()
        
        # Test 3: Real browser (headed) with stealth
        print("Test 3: Real Browser (Headed) + Stealth")
        print("-" * 40)
        try:
            browser = await p.chromium.launch(
                headless=False,
                channel="chrome",
                args=['--disable-blink-features=AutomationControlled']
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Hide webdriver
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = await context.new_page()
            
            response = await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            print(f"✅ SUCCESS - Status: {response.status if response else 'N/A'}")
            await page.screenshot(path="bot_test_artifacts/zomato_test3_real_browser.png")
            
            # Wait a bit so you can see the browser
            await asyncio.sleep(3)
            
        except Exception as e:
            error_str = str(e)
            print(f"❌ BLOCKED - Error: {error_str[:200]}")
            
            if 'ERR_HTTP2_PROTOCOL_ERROR' in error_str:
                print(f"   🔍 Detection: HTTP/2 Protocol Fingerprinting")
            elif 'ERR_CONNECTION_REFUSED' in error_str:
                print(f"   🔍 Detection: Connection Refused (Network Block)")
            elif 'timeout' in error_str.lower():
                print(f"   🔍 Detection: Timeout (Rate Limiting)")
                
        finally:
            await browser.close()
        
        print()
        
    print("="*80)
    print("📊 SUMMARY")
    print("="*80)
    print("\nZomato is using one or more of these detection methods:")
    print("1. HTTP/2 Protocol Fingerprinting - Detects headless browsers at network level")
    print("2. TLS Fingerprinting - Analyzes SSL/TLS handshake patterns")
    print("3. Browser Fingerprinting - Checks WebGL, Canvas, Fonts, etc.")
    print("4. Behavioral Analysis - Monitors mouse movements, timing, etc.")
    print("5. IP/Network Blocking - Blocks known datacenter IPs")
    print("\nIf all tests failed with HTTP2 error, Zomato is using network-level detection")
    print("which is very difficult to bypass without residential proxies.")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_zomato())

