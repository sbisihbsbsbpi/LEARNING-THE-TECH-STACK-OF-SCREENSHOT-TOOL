#!/usr/bin/env python3
"""
Inspect ALL elements on the Tekion page to find the dropdowns
"""

import asyncio
from playwright.async_api import async_playwright

async def inspect_page():
    """Inspect page elements"""
    
    url = "https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=SERVICE"
    
    async with async_playwright() as p:
        print("🔗 Connecting to Brave...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        
        print(f"🌐 Loading: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)

        print(f"   ⏳ Waiting 10 seconds for content to load...")
        await asyncio.sleep(10)

        # Check what's actually on the page
        page_info = await page.evaluate("""() => {
            return {
                title: document.title,
                bodyText: document.body?.innerText?.substring(0, 500) || 'NO BODY',
                elementCount: document.querySelectorAll('*').length,
                hasLogin: document.body?.innerText?.toLowerCase().includes('login') || false,
                hasError: document.body?.innerText?.toLowerCase().includes('error') || false
            };
        }""")

        print(f"\n📄 Page Info:")
        print(f"   Title: {page_info['title']}")
        print(f"   Elements: {page_info['elementCount']}")
        print(f"   Has 'login': {page_info['hasLogin']}")
        print(f"   Has 'error': {page_info['hasError']}")
        print(f"\n   Body text (first 500 chars):")
        print(f"   {page_info['bodyText']}")

        print(f"\n🔍 Searching for elements containing key text...")
        
        # Search for ANY element containing our target text
        results = await page.evaluate("""() => {
            const searchTexts = [
                'Variable',
                'Fixed',
                'Services',
                'Part',
                'Purchase',
                'Warranty',
                'Others',
                'Payment'
            ];
            
            const found = [];
            document.querySelectorAll('*').forEach(el => {
                const text = el.textContent?.trim() || '';
                
                // Check if text contains any of our search terms
                if (searchTexts.some(term => text.includes(term)) && text.length < 100) {
                    const style = window.getComputedStyle(el);
                    found.push({
                        text: text,
                        tag: el.tagName,
                        classes: el.className,
                        id: el.id,
                        childCount: el.children.length,
                        cursor: style.cursor,
                        display: style.display,
                        visible: el.offsetHeight > 0,
                        ariaExpanded: el.getAttribute('aria-expanded'),
                        role: el.getAttribute('role')
                    });
                }
            });
            
            return found;
        }""")
        
        print(f"\n✅ Found {len(results)} elements:")
        print(f"{'='*100}")
        
        for i, item in enumerate(results[:30], 1):  # Show first 30
            print(f"\n{i}. TEXT: {item['text'][:60]}")
            print(f"   Tag: {item['tag']}, Children: {item['childCount']}, Visible: {item['visible']}")
            print(f"   Classes: {item['classes'][:60]}")
            print(f"   Cursor: {item['cursor']}, Display: {item['display']}")
            print(f"   ARIA: {item['ariaExpanded']}, Role: {item['role']}")
        
        await page.close()
        print(f"\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(inspect_page())

