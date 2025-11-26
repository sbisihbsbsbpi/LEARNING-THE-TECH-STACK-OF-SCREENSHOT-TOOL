#!/usr/bin/env python3
"""
Test final dropdown detection - should only expand content panels, not side menu
"""

import asyncio
from playwright.async_api import async_playwright

async def test_final():
    """Test final dropdown detection"""
    
    url = "https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=SERVICE"
    
    async with async_playwright() as p:
        print("🔗 Connecting to Brave...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        
        print(f"🌐 Loading: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        print(f"   ⏳ Waiting for SPA content to render...")
        await asyncio.sleep(10)
        
        print(f"\n📊 BEFORE dropdown detection:")
        before = await page.evaluate("""() => {
            const sideMenu = [];
            const contentPanels = [];
            
            // Check side menu items
            document.querySelectorAll('.ant-menu-submenu-title').forEach(el => {
                sideMenu.push({
                    text: el.textContent?.trim().substring(0, 30),
                    ariaExpanded: el.getAttribute('aria-expanded')
                });
            });
            
            // Check content collapse panels
            document.querySelectorAll('.ant-collapse-item').forEach(el => {
                const header = el.querySelector('.ant-collapse-header');
                const isActive = el.classList.contains('ant-collapse-item-active');
                contentPanels.push({
                    text: header?.textContent?.trim().substring(0, 30) || 'NO TEXT',
                    isActive: isActive,
                    ariaExpanded: header?.getAttribute('aria-expanded')
                });
            });
            
            return { sideMenu, contentPanels };
        }""")
        
        print(f"\n   Side Menu Items:")
        for item in before['sideMenu']:
            status = "✅ OPEN" if item['ariaExpanded'] == 'true' else "❌ CLOSED"
            print(f"      {status}: {item['text']}")
        
        print(f"\n   Content Panels:")
        for item in before['contentPanels']:
            status = "✅ OPEN" if item['isActive'] else "❌ CLOSED"
            print(f"      {status}: {item['text']}")
        
        # Now run dropdown detection (Pattern 1 only - icon-caret-right)
        print(f"\n🔍 Running dropdown detection (Pattern 1: .icon-caret-right)...")
        
        result = await page.evaluate("""() => {
            let count = 0;
            const clicked = [];
            
            // Pattern 1: Arrow Icons (Caret/Chevron)
            const arrowSelectors = ['.icon-caret-right'];
            
            arrowSelectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                
                elements.forEach(el => {
                    // Find the clickable parent
                    let clickTarget = el;
                    for (let i = 0; i < 3; i++) {
                        if (clickTarget.parentElement) {
                            clickTarget = clickTarget.parentElement;
                            const style = window.getComputedStyle(clickTarget);
                            
                            if (style.cursor === 'pointer' ||
                                clickTarget.onclick ||
                                clickTarget.getAttribute('role') === 'button' ||
                                clickTarget.classList.contains('collapse') ||
                                clickTarget.classList.contains('accordion')) {
                                break;
                            }
                        }
                    }
                    
                    // Get the nearest text content
                    let textElement = clickTarget;
                    while (textElement && (!textElement.textContent || textElement.textContent.length > 100)) {
                        textElement = textElement.parentElement;
                    }
                    
                    const text = textElement?.textContent?.trim().substring(0, 50) || 'NO TEXT';
                    
                    clicked.push({
                        text: text,
                        tag: clickTarget.tagName,
                        classes: clickTarget.className.substring(0, 50)
                    });
                    
                    try {
                        clickTarget.click();
                        count++;
                    } catch (e) {
                        // Ignore
                    }
                });
            });
            
            return { count, clicked };
        }""")
        
        print(f"\n✅ Clicked {result['count']} elements:")
        for i, item in enumerate(result['clicked'], 1):
            print(f"   {i}. {item['text']}")
            print(f"      Tag: {item['tag']}, Classes: {item['classes']}")
        
        # Wait and check final state
        await asyncio.sleep(3)
        
        print(f"\n📊 AFTER dropdown detection:")
        after = await page.evaluate("""() => {
            const sideMenu = [];
            const contentPanels = [];
            
            // Check side menu items
            document.querySelectorAll('.ant-menu-submenu-title').forEach(el => {
                sideMenu.push({
                    text: el.textContent?.trim().substring(0, 30),
                    ariaExpanded: el.getAttribute('aria-expanded')
                });
            });
            
            // Check content collapse panels
            document.querySelectorAll('.ant-collapse-item').forEach(el => {
                const header = el.querySelector('.ant-collapse-header');
                const isActive = el.classList.contains('ant-collapse-item-active');
                contentPanels.push({
                    text: header?.textContent?.trim().substring(0, 30) || 'NO TEXT',
                    isActive: isActive,
                    ariaExpanded: header?.getAttribute('aria-expanded')
                });
            });
            
            return { sideMenu, contentPanels };
        }""")
        
        print(f"\n   Side Menu Items:")
        for item in after['sideMenu']:
            status = "✅ OPEN" if item['ariaExpanded'] == 'true' else "❌ CLOSED"
            print(f"      {status}: {item['text']}")
        
        print(f"\n   Content Panels:")
        for item in after['contentPanels']:
            status = "✅ OPEN" if item['isActive'] else "❌ CLOSED"
            print(f"      {status}: {item['text']}")
        
        await page.close()
        print(f"\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_final())

