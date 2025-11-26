#!/usr/bin/env python3
"""
Test both SERVICE and TEKION_PAY URLs to verify side menu is NOT expanded
"""

import asyncio
from playwright.async_api import async_playwright

async def test_url(page, url, module_name):
    """Test a single URL"""
    
    print(f"\n{'='*80}")
    print(f"Testing: {module_name}")
    print(f"URL: {url}")
    print(f"{'='*80}")
    
    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
    
    print(f"   ⏳ Waiting for SPA content to render...")
    await asyncio.sleep(10)
    
    # Get BEFORE state
    before = await page.evaluate("""() => {
        const sideMenu = [];
        const contentPanels = [];
        
        document.querySelectorAll('.ant-menu-submenu-title').forEach(el => {
            sideMenu.push({
                text: el.textContent?.trim(),
                expanded: el.getAttribute('aria-expanded') === 'true'
            });
        });
        
        document.querySelectorAll('.ant-collapse-item').forEach(el => {
            const header = el.querySelector('.ant-collapse-header');
            const isActive = el.classList.contains('ant-collapse-item-active');
            contentPanels.push({
                title: header?.textContent?.trim().substring(0, 30) || 'NO TITLE',
                isOpen: isActive
            });
        });
        
        return { sideMenu, contentPanels };
    }""")
    
    print(f"\n📊 BEFORE dropdown detection:")
    print(f"   Side Menu:")
    for item in before['sideMenu']:
        status = "✅ OPEN" if item['expanded'] else "❌ CLOSED"
        print(f"      {status}: {item['text']}")
    
    print(f"   Content Panels:")
    for item in before['contentPanels']:
        status = "✅ OPEN" if item['isOpen'] else "❌ CLOSED"
        print(f"      {status}: {item['title']}")
    
    # Run dropdown detection (ONLY Pattern 1: icon-caret-right)
    print(f"\n🔍 Running dropdown detection...")
    
    clicked = await page.evaluate("""() => {
        let count = 0;
        const clicked = [];
        
        // ONLY Pattern 1: Arrow Icons (icon-caret-right)
        const arrowSelectors = ['.icon-caret-right'];
        
        arrowSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            
            elements.forEach(el => {
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
                
                // Get nearest text
                let textEl = clickTarget;
                while (textEl && textEl.textContent.length > 100) {
                    textEl = textEl.querySelector('[class*="header"]') || textEl.parentElement;
                }
                
                clicked.push(textEl?.textContent?.trim().substring(0, 30) || 'NO TEXT');
                
                try {
                    clickTarget.click();
                    count++;
                } catch (e) {}
            });
        });
        
        return { count, clicked };
    }""")
    
    print(f"   ✅ Clicked {clicked['count']} elements:")
    for i, text in enumerate(clicked['clicked'], 1):
        print(f"      {i}. {text}")
    
    await asyncio.sleep(3)
    
    # Get AFTER state
    after = await page.evaluate("""() => {
        const sideMenu = [];
        const contentPanels = [];
        
        document.querySelectorAll('.ant-menu-submenu-title').forEach(el => {
            sideMenu.push({
                text: el.textContent?.trim(),
                expanded: el.getAttribute('aria-expanded') === 'true'
            });
        });
        
        document.querySelectorAll('.ant-collapse-item').forEach(el => {
            const header = el.querySelector('.ant-collapse-header');
            const isActive = el.classList.contains('ant-collapse-item-active');
            contentPanels.push({
                title: header?.textContent?.trim().substring(0, 30) || 'NO TITLE',
                isOpen: isActive
            });
        });
        
        return { sideMenu, contentPanels };
    }""")
    
    print(f"\n📊 AFTER dropdown detection:")
    print(f"   Side Menu:")
    for item in after['sideMenu']:
        status = "✅ OPEN" if item['expanded'] else "❌ CLOSED"
        print(f"      {status}: {item['text']}")
    
    print(f"   Content Panels:")
    for item in after['contentPanels']:
        status = "✅ OPEN" if item['isOpen'] else "❌ CLOSED"
        print(f"      {status}: {item['title']}")
    
    # Verify side menu didn't change
    print(f"\n🔍 Verification:")
    side_menu_changed = False
    for i, item in enumerate(before['sideMenu']):
        if item['expanded'] != after['sideMenu'][i]['expanded']:
            side_menu_changed = True
            print(f"   ⚠️  Side menu item changed: {item['text']}")
    
    if not side_menu_changed:
        print(f"   ✅ Side menu NOT touched - CORRECT!")
    else:
        print(f"   ❌ Side menu WAS changed - WRONG!")
    
    # Verify content panels were expanded
    content_expanded = False
    for i, item in enumerate(before['contentPanels']):
        if not item['isOpen'] and after['contentPanels'][i]['isOpen']:
            content_expanded = True
            print(f"   ✅ Content panel expanded: {item['title']}")
    
    if content_expanded:
        print(f"   ✅ Content panels expanded - CORRECT!")
    elif len(before['contentPanels']) == 0:
        print(f"   ℹ️  No content panels found")
    else:
        print(f"   ⚠️  No content panels were expanded")


async def main():
    """Main test function"""
    
    urls = [
        ("https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=SERVICE", "SERVICE"),
        ("https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=TEKION_PAY", "TEKION_PAY")
    ]
    
    async with async_playwright() as p:
        print("🔗 Connecting to Brave...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        
        for url, module_name in urls:
            await test_url(page, url, module_name)
        
        await page.close()
        
        print(f"\n{'='*80}")
        print(f"✅ All tests complete!")
        print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(main())

