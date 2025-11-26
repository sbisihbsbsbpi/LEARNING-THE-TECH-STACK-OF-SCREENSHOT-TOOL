#!/usr/bin/env python3
"""
Inspect TEKION_PAY page to see all content
"""

import asyncio
from playwright.async_api import async_playwright

async def inspect():
    """Inspect page"""
    
    url = "https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=TEKION_PAY"
    
    async with async_playwright() as p:
        print("🔗 Connecting to Brave...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        
        print(f"🌐 Loading: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        print(f"   ⏳ Waiting for SPA content to render...")
        await asyncio.sleep(10)
        
        # Expand all dropdowns
        print(f"\n🔍 Expanding dropdowns...")
        await page.evaluate("""() => {
            // Click all .icon-caret-right
            document.querySelectorAll('.icon-caret-right').forEach(el => {
                let clickTarget = el;
                for (let i = 0; i < 3; i++) {
                    if (clickTarget.parentElement) {
                        clickTarget = clickTarget.parentElement;
                        const style = window.getComputedStyle(clickTarget);
                        if (style.cursor === 'pointer') break;
                    }
                }
                try { clickTarget.click(); } catch(e) {}
            });
        }""")
        
        await asyncio.sleep(3)
        
        # Check all content
        print(f"\n📊 Page Content Structure:")
        
        structure = await page.evaluate("""() => {
            const result = {
                sideMenu: [],
                contentPanels: []
            };
            
            // Side menu
            document.querySelectorAll('.ant-menu-submenu-title').forEach(el => {
                result.sideMenu.push({
                    text: el.textContent?.trim(),
                    expanded: el.getAttribute('aria-expanded') === 'true'
                });
            });
            
            // Content panels
            document.querySelectorAll('.ant-collapse-item').forEach(el => {
                const header = el.querySelector('.ant-collapse-header');
                const isActive = el.classList.contains('ant-collapse-item-active');
                
                // Count rows in table if exists
                const table = el.querySelector('[role="table"]');
                const rows = table ? table.querySelectorAll('[role="row"]').length - 1 : 0; // -1 for header
                
                result.contentPanels.push({
                    title: header?.textContent?.trim().substring(0, 50) || 'NO TITLE',
                    isOpen: isActive,
                    hasTable: !!table,
                    rowCount: rows
                });
            });
            
            return result;
        }""")
        
        print(f"\n📁 Side Menu:")
        for item in structure['sideMenu']:
            status = "✅" if item['expanded'] else "❌"
            print(f"   {status} {item['text']}")
        
        print(f"\n📦 Content Panels:")
        for item in structure['contentPanels']:
            status = "✅ OPEN" if item['isOpen'] else "❌ CLOSED"
            table_info = f"({item['rowCount']} rows)" if item['hasTable'] else "(no table)"
            print(f"   {status}: {item['title']} {table_info}")
        
        # Check for any collapsed elements
        print(f"\n🔍 Checking for remaining collapsed elements...")
        
        collapsed = await page.evaluate("""() => {
            const collapsed = [];
            
            // Check for right arrows (collapsed state)
            document.querySelectorAll('.icon-caret-right').forEach(el => {
                let parent = el.parentElement;
                while (parent && parent.textContent.length > 100) {
                    parent = parent.parentElement;
                }
                collapsed.push({
                    type: 'caret-right',
                    text: parent?.textContent?.trim().substring(0, 50) || 'NO TEXT'
                });
            });
            
            // Check for collapsed panels
            document.querySelectorAll('.ant-collapse-item:not(.ant-collapse-item-active)').forEach(el => {
                const header = el.querySelector('.ant-collapse-header');
                collapsed.push({
                    type: 'collapsed-panel',
                    text: header?.textContent?.trim().substring(0, 50) || 'NO TEXT'
                });
            });
            
            return collapsed;
        }""")
        
        if len(collapsed) > 0:
            print(f"   ⚠️  Found {len(collapsed)} collapsed elements:")
            for item in collapsed:
                print(f"      - [{item['type']}] {item['text']}")
        else:
            print(f"   ✅ No collapsed elements found - all content is expanded!")
        
        await page.close()
        print(f"\n✅ Inspection complete!")

if __name__ == "__main__":
    asyncio.run(inspect())

