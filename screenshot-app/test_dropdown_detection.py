#!/usr/bin/env python3
"""
Test dropdown detection on Tekion page
"""

import asyncio
from playwright.async_api import async_playwright

async def test_dropdown_detection():
    """Test dropdown detection"""
    
    url = "https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=SERVICE"
    
    async with async_playwright() as p:
        print("🔗 Connecting to Brave...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        
        print(f"🌐 Loading: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)

        print(f"   ⏳ Waiting for React/Angular to render content...")
        await asyncio.sleep(10)  # Wait longer for SPA to render
        
        print(f"\n🔍 First, let's check if .icon-caret-right exists...")

        # Check if elements exist
        check_result = await page.evaluate("""() => {
            const caretRight = document.querySelectorAll('.icon-caret-right');
            const antSubmenu = document.querySelectorAll('.ant-menu-submenu-title[aria-expanded="false"]');

            return {
                caretRightCount: caretRight.length,
                antSubmenuCount: antSubmenu.length,
                caretRightSample: caretRight.length > 0 ? {
                    tag: caretRight[0].tagName,
                    classes: caretRight[0].className,
                    parent: caretRight[0].parentElement?.className || 'NO PARENT'
                } : null
            };
        }""")

        print(f"   .icon-caret-right elements: {check_result['caretRightCount']}")
        print(f"   .ant-menu-submenu-title[aria-expanded=false]: {check_result['antSubmenuCount']}")
        if check_result['caretRightSample']:
            print(f"   Sample caret-right: {check_result['caretRightSample']}")

        print(f"\n🔍 Now testing dropdown detection patterns...")

        # Run the EXACT same detection code from screenshot_service.py
        result = await page.evaluate("""() => {
            let count = 0;
            const clicked = [];
            
            // Pattern 1: Arrow Icons (Caret/Chevron)
            const arrowSelectors = [
                '.icon-caret-right',
                '.caret-right',
                '.fa-caret-right',
                '.icon-chevron-right',
                '.chevron-right',
                '.fa-chevron-right'
            ];
            
            arrowSelectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                console.log(`Found ${elements.length} elements for selector: ${selector}`);
                
                elements.forEach(el => {
                    // Find the clickable parent (usually 1-3 levels up)
                    let clickTarget = el;
                    for (let i = 0; i < 3; i++) {
                        if (clickTarget.parentElement) {
                            clickTarget = clickTarget.parentElement;
                            const style = window.getComputedStyle(clickTarget);
                            
                            console.log(`  Level ${i}: ${clickTarget.tagName}.${clickTarget.className.substring(0,30)} cursor=${style.cursor}`);
                            
                            if (style.cursor === 'pointer' ||
                                clickTarget.onclick ||
                                clickTarget.getAttribute('role') === 'button' ||
                                clickTarget.classList.contains('collapse') ||
                                clickTarget.classList.contains('accordion')) {
                                break;
                            }
                        }
                    }
                    
                    // Get info about what we're clicking
                    const text = clickTarget.textContent?.trim().substring(0, 50) || '';
                    clicked.push({
                        selector: selector,
                        tag: clickTarget.tagName,
                        classes: clickTarget.className.substring(0, 50),
                        text: text,
                        cursor: window.getComputedStyle(clickTarget).cursor
                    });
                    
                    // Click to expand
                    try {
                        clickTarget.click();
                        count++;
                    } catch (e) {
                        console.error('Click failed:', e);
                    }
                });
            });
            
            // Pattern 4.5: Ant Design Menu Submenu
            const antMenuSubmenus = document.querySelectorAll('.ant-menu-submenu-title[aria-expanded="false"]');
            console.log(`Found ${antMenuSubmenus.length} Ant menu submenus with aria-expanded=false`);
            
            antMenuSubmenus.forEach(el => {
                const text = el.textContent?.trim().substring(0, 50) || '';
                clicked.push({
                    selector: '.ant-menu-submenu-title[aria-expanded="false"]',
                    tag: el.tagName,
                    classes: el.className.substring(0, 50),
                    text: text,
                    cursor: window.getComputedStyle(el).cursor
                });
                
                try {
                    el.click();
                    count++;
                } catch (e) {
                    console.error('Click failed:', e);
                }
            });
            
            return { count, clicked };
        }""")
        
        print(f"\n✅ Clicked {result['count']} elements:")
        print(f"{'='*100}")
        
        for i, item in enumerate(result['clicked'], 1):
            print(f"\n{i}. Pattern: {item['selector']}")
            print(f"   Element: {item['tag']}.{item['classes']}")
            print(f"   Text: {item['text']}")
            print(f"   Cursor: {item['cursor']}")
        
        # Wait to see the result
        print(f"\n⏸️  Waiting 5 seconds to see expanded sections...")
        await asyncio.sleep(5)
        
        # Check what's expanded now
        expanded = await page.evaluate("""() => {
            const expanded = [];
            document.querySelectorAll('.ant-menu-submenu-title').forEach(el => {
                expanded.push({
                    text: el.textContent?.trim().substring(0, 50),
                    ariaExpanded: el.getAttribute('aria-expanded')
                });
            });
            return expanded;
        }""")
        
        print(f"\n📊 Final state of menu items:")
        for item in expanded:
            status = "✅ EXPANDED" if item['ariaExpanded'] == 'true' else "❌ COLLAPSED"
            print(f"   {status}: {item['text']}")
        
        await page.close()
        print(f"\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_dropdown_detection())

