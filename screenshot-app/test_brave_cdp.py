#!/usr/bin/env python3
"""
Test script to capture Tekion pages using Brave CDP
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def test_brave_cdp():
    """Test capturing with Brave CDP"""
    
    print("🦁 Testing Brave CDP Mode")
    print("="*80)
    
    # Test URLs
    test_urls = [
        "https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=SERVICE",
        "https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=NEW_VEHICLE",
    ]
    
    async with async_playwright() as p:
        print("🔗 Connecting to Brave on port 9222...")
        
        try:
            # Connect to existing Brave instance
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ Connected to Brave!")
            
            # Get default context (your actual Brave session)
            contexts = browser.contexts
            if not contexts:
                print("❌ No browser contexts found")
                return
            
            context = contexts[0]
            print(f"✅ Using browser context (already logged in)")
            
            for url in test_urls:
                print(f"\n{'='*80}")
                print(f"Testing: {url}")
                print(f"{'='*80}")
                
                # Create new page (tab)
                page = await context.new_page()
                
                # Navigate
                print(f"🌐 Navigating to URL...")
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    print(f"   ✅ Page loaded (domcontentloaded)")
                except Exception as e:
                    print(f"   ⚠️  Navigation timeout, but continuing: {e}")

                # Wait for page to settle and content to load
                print(f"   ⏳ Waiting for content to load...")
                await asyncio.sleep(5)

                # Check final URL
                final_url = page.url
                print(f"📍 Requested URL: {url}")
                print(f"📍 Final URL:     {final_url}")

                if '/login' in final_url.lower():
                    print(f"❌ Redirected to login - you need to log in to Brave first!")
                elif url != final_url:
                    print(f"⚠️  URL changed (might be redirect)")
                else:
                    print(f"✅ URL stayed the same")

                # Get page title
                title = await page.title()
                print(f"📄 Page title: {title}")
                
                # Check for collapsed sections
                print(f"\n🔍 Checking for collapsed sections...")
                collapsed_info = await page.evaluate("""() => {
                    const results = [];
                    const texts = [
                        'Variable Operations',
                        'Fixed Operations',
                        'Payment Receipts'
                    ];

                    // Check ALL elements
                    const allElements = Array.from(document.querySelectorAll('*'));
                    console.log(`Total elements on page: ${allElements.length}`);

                    allElements.forEach(el => {
                        const text = el.textContent?.trim() || '';

                        // Check for specific texts or count patterns
                        const matchesText = texts.some(t => text === t);
                        const hasCount = /^[^(]+\\(\\d+\\)$/.test(text) && text.length < 50;

                        if ((matchesText || hasCount) && el.children.length <= 5) {
                            const style = window.getComputedStyle(el);
                            results.push({
                                text: text,
                                tag: el.tagName,
                                classes: el.className,
                                clickable: style.cursor === 'pointer' || !!el.onclick,
                                ariaExpanded: el.getAttribute('aria-expanded'),
                                visible: el.offsetHeight > 0
                            });
                        }
                    });

                    return results;
                }""")

                print(f"   Found {len(collapsed_info)} potential collapsible elements:")
                for item in collapsed_info[:15]:  # Show first 15
                    clickable = "✅" if item['clickable'] else "❌"
                    visible = "👁️" if item['visible'] else "🚫"
                    aria = item.get('ariaExpanded', 'null')
                    print(f"      {clickable} {visible} {item['text'][:40]} (aria: {aria}, class: {item['classes'][:30]})")
                
                # Take screenshot
                print(f"\n📸 Taking screenshot...")
                screenshot_path = f"screenshots/test_brave_{url.split('module=')[1]}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"   ✅ Saved: {screenshot_path}")
                
                # Close the tab
                await page.close()
                print(f"   ✅ Tab closed")
            
            print(f"\n{'='*80}")
            print(f"✅ Test complete!")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"\n💡 Make sure:")
            print(f"   1. Brave is running")
            print(f"   2. Brave was launched with --remote-debugging-port=9222")
            print(f"   3. You're logged into Tekion in Brave")

if __name__ == "__main__":
    asyncio.run(test_brave_cdp())

