"""
Zomato Bot Detection Diagnostic Tool

This script analyzes HOW Zomato is blocking automated browsers.
It tests multiple detection vectors and reports which ones are triggering.
"""

import asyncio
import json
from datetime import datetime

try:
    from rebrowser_playwright.async_api import async_playwright
    USING_REBROWSER = True
    print("🚀 Using Rebrowser Playwright")
except ImportError:
    from playwright.async_api import async_playwright
    USING_REBROWSER = False
    print("⚠️  Using Standard Playwright")


async def test_detection_vector(name: str, test_func, page):
    """Test a specific detection vector"""
    try:
        result = await test_func(page)
        return {
            "name": name,
            "detected": result["detected"],
            "details": result.get("details", ""),
            "value": result.get("value", None)
        }
    except Exception as e:
        return {
            "name": name,
            "detected": None,
            "details": f"Error: {str(e)}",
            "value": None
        }


async def check_navigator_webdriver(page):
    """Check if navigator.webdriver is exposed"""
    result = await page.evaluate("""
        () => {
            return {
                value: navigator.webdriver,
                detected: navigator.webdriver === true
            };
        }
    """)
    return {
        "detected": result["detected"],
        "value": result["value"],
        "details": f"navigator.webdriver = {result['value']}"
    }


async def check_chrome_property(page):
    """Check if window.chrome is missing"""
    result = await page.evaluate("""
        () => {
            const hasChrome = !!window.chrome;
            const hasRuntime = !!(window.chrome && window.chrome.runtime);
            return {
                hasChrome: hasChrome,
                hasRuntime: hasRuntime,
                detected: !hasChrome
            };
        }
    """)
    return {
        "detected": result["detected"],
        "value": result,
        "details": f"window.chrome exists: {result['hasChrome']}, has runtime: {result['hasRuntime']}"
    }


async def check_permissions_api(page):
    """Check permissions API behavior"""
    result = await page.evaluate("""
        async () => {
            try {
                const permissionStatus = await navigator.permissions.query({ name: 'notifications' });
                return {
                    detected: false,
                    state: permissionStatus.state
                };
            } catch (e) {
                return {
                    detected: true,
                    error: e.message
                };
            }
        }
    """)
    return {
        "detected": result.get("detected", False),
        "value": result,
        "details": f"Permissions API: {result}"
    }


async def check_plugins_length(page):
    """Check if plugins array is empty (headless indicator)"""
    result = await page.evaluate("""
        () => {
            return {
                length: navigator.plugins.length,
                detected: navigator.plugins.length === 0
            };
        }
    """)
    return {
        "detected": result["detected"],
        "value": result["length"],
        "details": f"navigator.plugins.length = {result['length']}"
    }


async def check_languages(page):
    """Check language configuration"""
    result = await page.evaluate("""
        () => {
            return {
                language: navigator.language,
                languages: navigator.languages,
                detected: !navigator.languages || navigator.languages.length === 0
            };
        }
    """)
    return {
        "detected": result["detected"],
        "value": result,
        "details": f"Languages: {result['languages']}"
    }


async def check_user_agent(page):
    """Check user agent for headless indicators"""
    result = await page.evaluate("""
        () => {
            const ua = navigator.userAgent;
            const hasHeadless = ua.includes('Headless') || ua.includes('headless');
            return {
                userAgent: ua,
                detected: hasHeadless
            };
        }
    """)
    return {
        "detected": result["detected"],
        "value": result["userAgent"],
        "details": f"Headless in UA: {result['detected']}"
    }


async def check_webgl_vendor(page):
    """Check WebGL vendor/renderer (fingerprinting)"""
    result = await page.evaluate("""
        () => {
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (!gl) return { detected: true, details: 'No WebGL support' };
                
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                if (!debugInfo) return { detected: false, details: 'No debug info' };
                
                const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                
                const suspicious = vendor.includes('Google') && renderer.includes('SwiftShader');
                
                return {
                    vendor: vendor,
                    renderer: renderer,
                    detected: suspicious
                };
            } catch (e) {
                return { detected: true, error: e.message };
            }
        }
    """)
    return {
        "detected": result.get("detected", False),
        "value": result,
        "details": f"Vendor: {result.get('vendor', 'N/A')}, Renderer: {result.get('renderer', 'N/A')}"
    }


async def check_automation_flags(page):
    """Check for automation-specific flags"""
    result = await page.evaluate("""
        () => {
            const flags = {
                webdriver: navigator.webdriver,
                automation: window.navigator.automation,
                callPhantom: !!window.callPhantom,
                _phantom: !!window._phantom,
                phantom: !!window.phantom,
                __nightmare: !!window.__nightmare,
                _selenium: !!window._selenium,
                __webdriver_script_fn: !!document.__webdriver_script_fn,
                __driver_evaluate: !!document.__driver_evaluate,
                __webdriver_evaluate: !!document.__webdriver_evaluate,
                __selenium_evaluate: !!document.__selenium_evaluate,
                __fxdriver_evaluate: !!document.__fxdriver_evaluate,
                __driver_unwrapped: !!document.__driver_unwrapped,
                __webdriver_unwrapped: !!document.__webdriver_unwrapped,
                __selenium_unwrapped: !!document.__selenium_unwrapped,
                __fxdriver_unwrapped: !!document.__fxdriver_unwrapped,
            };
            
            const detected = Object.values(flags).some(v => v === true);
            
            return {
                flags: flags,
                detected: detected
            };
        }
    """)
    return {
        "detected": result["detected"],
        "value": result["flags"],
        "details": f"Automation flags found: {[k for k, v in result['flags'].items() if v]}"
    }


async def check_cdp_detection(page):
    """Check for Chrome DevTools Protocol detection"""
    result = await page.evaluate("""
        () => {
            // Check if CDP is detectable
            const hasCDP = !!(window.chrome && window.chrome.runtime && window.chrome.runtime.connect);
            
            return {
                detected: !hasCDP,
                details: hasCDP ? 'CDP available' : 'CDP not available'
            };
        }
    """)
    return {
        "detected": result["detected"],
        "value": result,
        "details": result["details"]
    }


async def test_network_request(url: str, mode: str, use_stealth: bool):
    """Test if we can make a successful request to Zomato"""
    print(f"\n{'='*80}")
    print(f"🧪 Testing: {mode}")
    print(f"   URL: {url}")
    print(f"   Stealth: {use_stealth}")
    print(f"{'='*80}\n")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=(mode == "headless"),
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ] if use_stealth else [],
            channel="chrome" if mode == "real_browser" else None
        )
        
        # Create context
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        # Add stealth scripts if enabled
        if use_stealth:
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
            """)
        
        page = await context.new_page()
        
        # Run detection tests BEFORE navigation
        print("📊 Running detection tests...\n")
        
        tests = [
            ("navigator.webdriver", check_navigator_webdriver),
            ("window.chrome", check_chrome_property),
            ("Permissions API", check_permissions_api),
            ("Plugins Length", check_plugins_length),
            ("Languages", check_languages),
            ("User Agent", check_user_agent),
            ("WebGL Vendor", check_webgl_vendor),
            ("Automation Flags", check_automation_flags),
            ("CDP Detection", check_cdp_detection),
        ]
        
        results = []
        for name, test_func in tests:
            result = await test_detection_vector(name, test_func, page)
            results.append(result)
            
            # Print result
            status = "🔴 DETECTED" if result["detected"] else "🟢 HIDDEN"
            print(f"{status} | {name}")
            print(f"         {result['details']}\n")
        
        # Try to navigate to Zomato
        print(f"\n🌐 Attempting to navigate to {url}...\n")
        
        navigation_result = {
            "success": False,
            "error": None,
            "status_code": None,
            "final_url": None
        }
        
        try:
            response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            navigation_result["success"] = True
            navigation_result["status_code"] = response.status if response else None
            navigation_result["final_url"] = page.url
            
            print(f"✅ Navigation successful!")
            print(f"   Status: {response.status if response else 'N/A'}")
            print(f"   Final URL: {page.url}")
            
            # Take screenshot
            screenshot_path = f"bot_test_artifacts/zomato_diagnostic_{mode}_{'stealth' if use_stealth else 'normal'}.png"
            await page.screenshot(path=screenshot_path)
            print(f"   Screenshot: {screenshot_path}")
            
        except Exception as e:
            navigation_result["success"] = False
            navigation_result["error"] = str(e)
            
            print(f"❌ Navigation failed!")
            print(f"   Error: {str(e)}")
            
            # Check error type
            error_str = str(e)
            if 'ERR_HTTP2_PROTOCOL_ERROR' in error_str:
                print(f"   🔍 Detection Method: HTTP/2 Protocol Fingerprinting")
            elif 'ERR_CONNECTION_REFUSED' in error_str:
                print(f"   🔍 Detection Method: Connection Refused (IP/Network Block)")
            elif 'ERR_SSL_PROTOCOL_ERROR' in error_str:
                print(f"   🔍 Detection Method: SSL/TLS Fingerprinting")
            elif 'timeout' in error_str.lower():
                print(f"   🔍 Detection Method: Timeout (Possible Rate Limiting)")
            else:
                print(f"   🔍 Detection Method: Unknown")
        
        await browser.close()
        
        return {
            "mode": mode,
            "use_stealth": use_stealth,
            "detection_tests": results,
            "navigation": navigation_result,
            "detected_count": sum(1 for r in results if r["detected"]),
            "total_tests": len(results)
        }


async def main():
    """Run comprehensive Zomato blocking analysis"""
    
    print("\n" + "="*80)
    print("🔍 ZOMATO BOT DETECTION DIAGNOSTIC TOOL")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Using: {'Rebrowser Playwright' if USING_REBROWSER else 'Standard Playwright'}")
    print("="*80 + "\n")
    
    url = "https://www.zomato.com/restaurants-near-me"
    
    # Test different configurations
    configurations = [
        ("headless", False),
        ("headless", True),
        ("real_browser", False),
        ("real_browser", True),
    ]
    
    all_results = []
    
    for mode, use_stealth in configurations:
        result = await test_network_request(url, mode, use_stealth)
        all_results.append(result)
        
        # Wait between tests
        await asyncio.sleep(2)
    
    # Generate summary report
    print("\n" + "="*80)
    print("📊 SUMMARY REPORT")
    print("="*80 + "\n")
    
    for result in all_results:
        mode_name = f"{result['mode']} + {'stealth' if result['use_stealth'] else 'normal'}"
        success = "✅ SUCCESS" if result['navigation']['success'] else "❌ BLOCKED"
        detected = f"{result['detected_count']}/{result['total_tests']} detection vectors triggered"
        
        print(f"{success} | {mode_name:30} | {detected}")
    
    # Save detailed report
    report_path = "bot_test_artifacts/zomato_diagnostic_report.json"
    with open(report_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    # Recommendations
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80 + "\n")
    
    best_config = min(all_results, key=lambda x: x['detected_count'])
    
    if best_config['navigation']['success']:
        print(f"✅ Best configuration: {best_config['mode']} + {'stealth' if best_config['use_stealth'] else 'normal'}")
        print(f"   Detection vectors triggered: {best_config['detected_count']}/{best_config['total_tests']}")
    else:
        print("❌ All configurations were blocked!")
        print("\nPossible reasons:")
        print("1. IP address is flagged/blocked")
        print("2. Network-level fingerprinting (HTTP/2, TLS)")
        print("3. Behavioral analysis (too fast, no mouse movement)")
        print("4. Residential proxy required")
        print("\nNext steps:")
        print("- Try from different network/IP")
        print("- Use residential proxy service")
        print("- Add human-like delays and interactions")
        print("- Use Zomato's official API instead")


if __name__ == "__main__":
    asyncio.run(main())

