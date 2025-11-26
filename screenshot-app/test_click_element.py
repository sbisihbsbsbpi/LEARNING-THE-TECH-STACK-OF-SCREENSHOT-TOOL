#!/usr/bin/env python3
"""
Test clicking on "Customer Return w/ Restocking" element
"""

import asyncio
from playwright.async_api import async_playwright

async def test_click():
    """Test clicking on element by text"""
    
    url = "https://preprodapp.tekioncloud.com/parts/return-reasons"
    
    async with async_playwright() as p:
        print("🔗 Connecting to Brave...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        
        print(f"🌐 Loading: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        print(f"   ⏳ Waiting for content to render...")
        await asyncio.sleep(5)
        
        # Click on "Customer Return w/ Restocking"
        print(f"\n🖱️  Clicking on 'Customer Return w/ Restocking'...")
        
        clicked = await page.evaluate("""(searchText) => {
            // Search for elements containing the text
            const allElements = document.querySelectorAll('*');
            let found = false;
            
            for (const el of allElements) {
                // Check if element's text content matches
                const textContent = el.textContent?.trim() || '';
                
                if (textContent === searchText || textContent.includes(searchText)) {
                    // Make sure it's a visible element
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        // Try to find the clickable parent (row, cell, button, etc.)
                        let clickTarget = el;
                        
                        // Walk up the tree to find a clickable element
                        for (let i = 0; i < 5; i++) {
                            if (!clickTarget) break;
                            
                            const style = window.getComputedStyle(clickTarget);
                            const tagName = clickTarget.tagName.toLowerCase();
                            
                            // Check if this element is clickable
                            if (style.cursor === 'pointer' ||
                                clickTarget.onclick ||
                                clickTarget.getAttribute('role') === 'button' ||
                                clickTarget.getAttribute('role') === 'gridcell' ||
                                clickTarget.getAttribute('role') === 'row' ||
                                tagName === 'button' ||
                                tagName === 'a' ||
                                clickTarget.classList.contains('rt-tr') ||
                                clickTarget.classList.contains('rt-td')) {
                                
                                try {
                                    clickTarget.click();
                                    found = true;
                                    return {
                                        success: true,
                                        element: tagName,
                                        text: textContent.substring(0, 50),
                                        classes: clickTarget.className
                                    };
                                } catch (e) {
                                    // Continue searching
                                }
                            }
                            
                            clickTarget = clickTarget.parentElement;
                        }
                    }
                }
            }
            
            return { success: false };
        }""", "Customer Return w/ Restocking")
        
        if clicked.get('success'):
            print(f"   ✅ Clicked: {clicked.get('element')}")
            print(f"      Text: {clicked.get('text')}")
            print(f"      Classes: {clicked.get('classes')}")
            
            # Wait for modal to appear
            print(f"\n   ⏳ Waiting for modal to appear...")
            await asyncio.sleep(2)
            
            # Check if modal appeared
            modal = await page.evaluate("""() => {
                const modal = document.querySelector('.ant-modal, [role="dialog"]');
                if (modal) {
                    const title = modal.querySelector('.ant-modal-title, h1, h2, h3');
                    return {
                        found: true,
                        title: title?.textContent || 'NO TITLE',
                        visible: window.getComputedStyle(modal).display !== 'none'
                    };
                }
                return { found: false };
            }""")
            
            if modal.get('found'):
                print(f"   ✅ Modal appeared!")
                print(f"      Title: {modal.get('title')}")
                print(f"      Visible: {modal.get('visible')}")
            else:
                print(f"   ⚠️  Modal not found")
        else:
            print(f"   ❌ Element not found: 'Customer Return w/ Restocking'")
        
        print(f"\n✅ Test complete!")
        await page.close()

if __name__ == "__main__":
    asyncio.run(test_click())

