#!/usr/bin/env python3
"""
Inspect side menu structure to see if it uses .icon-caret-right
"""

import asyncio
from playwright.async_api import async_playwright

async def inspect():
    """Inspect side menu"""
    
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
        
        # Check what uses .icon-caret-right
        print(f"\n🔍 Checking all .icon-caret-right elements:")
        
        elements = await page.evaluate("""() => {
            const results = [];
            
            document.querySelectorAll('.icon-caret-right').forEach(el => {
                // Walk up the tree to find context
                let parent = el;
                let context = 'unknown';
                
                // Check if inside side menu
                for (let i = 0; i < 10; i++) {
                    if (!parent) break;
                    
                    if (parent.classList.contains('ant-menu')) {
                        context = 'SIDE MENU';
                        break;
                    }
                    if (parent.classList.contains('ant-collapse')) {
                        context = 'CONTENT PANEL';
                        break;
                    }
                    
                    parent = parent.parentElement;
                }
                
                // Get nearest text
                let textEl = el;
                for (let i = 0; i < 5; i++) {
                    if (!textEl) break;
                    if (textEl.textContent && textEl.textContent.length < 100) {
                        break;
                    }
                    textEl = textEl.parentElement;
                }
                
                results.push({
                    context: context,
                    text: textEl?.textContent?.trim().substring(0, 50) || 'NO TEXT',
                    parentClass: el.parentElement?.className || 'NO CLASS'
                });
            });
            
            return results;
        }""")
        
        print(f"\n   Found {len(elements)} .icon-caret-right elements:\n")
        
        side_menu_count = 0
        content_panel_count = 0
        
        for i, elem in enumerate(elements, 1):
            icon = "🔴" if elem['context'] == 'SIDE MENU' else "🟢"
            print(f"   {i}. {icon} [{elem['context']}] {elem['text']}")
            print(f"      Parent class: {elem['parentClass'][:80]}")
            
            if elem['context'] == 'SIDE MENU':
                side_menu_count += 1
            elif elem['context'] == 'CONTENT PANEL':
                content_panel_count += 1
        
        print(f"\n📊 Summary:")
        print(f"   🔴 Side menu items: {side_menu_count} (SHOULD NOT CLICK)")
        print(f"   🟢 Content panels: {content_panel_count} (SHOULD CLICK)")
        print(f"   ⚪ Unknown: {len(elements) - side_menu_count - content_panel_count}")
        
        await page.close()
        print(f"\n✅ Inspection complete!")

if __name__ == "__main__":
    asyncio.run(inspect())

