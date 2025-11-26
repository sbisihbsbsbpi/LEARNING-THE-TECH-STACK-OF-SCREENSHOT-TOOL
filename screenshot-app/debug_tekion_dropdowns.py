#!/usr/bin/env python3
"""
Debug script to inspect Tekion dropdown structure
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

async def inspect_dropdowns():
    """Inspect the dropdown structure on Tekion pages"""
    
    # Load cookies
    storage_file = Path("browser_sessions/playwright_storage_state.json")
    if not storage_file.exists():
        print("❌ No cookies found. Please extract cookies first.")
        return

    # Load and fix storage state
    with open(storage_file, 'r') as f:
        storage_state = json.load(f)

    # Fix cookie expires format (convert to float if needed)
    if 'cookies' in storage_state:
        for cookie in storage_state['cookies']:
            if 'expires' in cookie and not isinstance(cookie['expires'], (int, float)):
                cookie['expires'] = -1  # Session cookie

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        # Load storage state (cookies)
        context = await browser.new_context(
            storage_state=storage_state,
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        # Navigate to the page
        url = "https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=SERVICE"
        print(f"🌐 Navigating to: {url}")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        
        # Wait for page to load
        await asyncio.sleep(3)
        
        print("\n🔍 Inspecting dropdown elements...")
        
        # Inspect the structure
        dropdown_info = await page.evaluate("""() => {
            const results = [];
            
            // Find all elements
            const allElements = document.querySelectorAll('*');
            
            allElements.forEach(el => {
                const text = el.textContent?.trim() || '';
                
                // Look for specific patterns
                const isVariableOps = text === 'Variable Operations';
                const isFixedOps = text === 'Fixed Operations';
                const isPaymentReceipts = text === 'Payment Receipts';
                const hasCount = /^[^(]+\\(\\d+\\)$/.test(text) && text.length < 50;
                
                if ((isVariableOps || isFixedOps || isPaymentReceipts || hasCount) && 
                    el.children.length <= 3) {
                    
                    // Get all attributes
                    const attrs = {};
                    for (let attr of el.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    
                    // Get computed style
                    const style = window.getComputedStyle(el);
                    
                    // Check for arrow icons
                    const hasArrowIcon = el.querySelector('[class*="arrow"], [class*="caret"], [class*="chevron"]');
                    const arrowIconClass = hasArrowIcon ? hasArrowIcon.className : null;
                    
                    // Check for info icon
                    const hasInfoIcon = el.querySelector('[class*="info"]');
                    
                    results.push({
                        text: text,
                        tag: el.tagName,
                        classes: el.className,
                        id: el.id,
                        attributes: attrs,
                        cursor: style.cursor,
                        display: style.display,
                        hasOnClick: !!el.onclick,
                        hasArrowIcon: !!hasArrowIcon,
                        arrowIconClass: arrowIconClass,
                        hasInfoIcon: !!hasInfoIcon,
                        childCount: el.children.length,
                        innerHTML: el.innerHTML.substring(0, 300)
                    });
                }
            });
            
            return results;
        }""")
        
        print(f"\n✅ Found {len(dropdown_info)} potential dropdown elements:\n")
        
        for i, info in enumerate(dropdown_info, 1):
            print(f"{'='*80}")
            print(f"Element {i}: {info['text'][:60]}")
            print(f"{'='*80}")
            print(f"Tag:           {info['tag']}")
            print(f"Classes:       {info['classes']}")
            print(f"ID:            {info['id']}")
            print(f"Cursor:        {info['cursor']}")
            print(f"Has onClick:   {info['hasOnClick']}")
            print(f"Has Arrow:     {info['hasArrowIcon']}")
            if info['arrowIconClass']:
                print(f"Arrow Class:   {info['arrowIconClass']}")
            print(f"Has Info Icon: {info['hasInfoIcon']}")
            print(f"Attributes:    {json.dumps(info['attributes'], indent=2)}")
            print(f"HTML Preview:  {info['innerHTML'][:200]}...")
            print()
        
        # Now try clicking on one to see what happens
        print("\n🖱️  Testing click on 'Variable Operations'...")
        
        click_result = await page.evaluate("""() => {
            const allElements = document.querySelectorAll('*');
            let found = null;
            
            for (let el of allElements) {
                if (el.textContent?.trim() === 'Variable Operations' && el.children.length <= 3) {
                    found = el;
                    break;
                }
            }
            
            if (found) {
                const beforeHTML = found.parentElement?.innerHTML.substring(0, 500);
                found.click();
                
                // Wait a bit for animation
                return new Promise(resolve => {
                    setTimeout(() => {
                        const afterHTML = found.parentElement?.innerHTML.substring(0, 500);
                        resolve({
                            clicked: true,
                            changed: beforeHTML !== afterHTML,
                            beforeHTML: beforeHTML,
                            afterHTML: afterHTML
                        });
                    }, 500);
                });
            }
            
            return { clicked: false };
        }""")
        
        print(f"Click result: {json.dumps(click_result, indent=2)}")
        
        # Keep browser open for manual inspection
        print("\n✅ Browser will stay open for 30 seconds for manual inspection...")
        await asyncio.sleep(30)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_dropdowns())

