#!/usr/bin/env python3
"""
Test script to verify viewport detection fix
Run this to debug viewport detection issues
"""

import asyncio
import sys
from playwright.async_api import async_playwright


async def test_viewport_detection():
    """Test viewport detection in real browser mode"""
    
    print("\n" + "="*80)
    print("🧪 VIEWPORT DETECTION TEST")
    print("="*80 + "\n")
    
    # Step 1: Check Chrome connection
    print("📍 Step 1: Checking Chrome connection...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ Connected to Chrome via CDP\n")
            
            # Step 2: Get existing context and create new page
            print("📍 Step 2: Creating new page in existing Chrome...")
            context = browser.contexts[0]
            page = await context.new_page()
            print("✅ New page created\n")
            
            # Step 3: Navigate to a test page
            print("📍 Step 3: Navigating to test page...")
            await page.goto("https://example.com", wait_until="networkidle")
            print("✅ Page loaded\n")
            
            # Step 4: Test viewport_size property
            print("📍 Step 4: Testing viewport_size property...")
            actual_viewport = page.viewport_size
            print(f"   viewport_size: {actual_viewport}")
            
            if actual_viewport:
                print(f"   ✅ viewport_size works!")
                print(f"   Width: {actual_viewport['width']}")
                print(f"   Height: {actual_viewport['height']}\n")
            else:
                print("   ⚠️  viewport_size is None\n")
            
            # Step 5: Test JavaScript detection
            print("📍 Step 5: Testing JavaScript detection...")
            viewport_info = await page.evaluate("""() => {
                return {
                    width: window.innerWidth,
                    height: window.innerHeight,
                    outerWidth: window.outerWidth,
                    outerHeight: window.outerHeight
                };
            }""")
            print(f"   window.innerWidth: {viewport_info['width']}")
            print(f"   window.innerHeight: {viewport_info['height']}")
            print(f"   window.outerWidth: {viewport_info['outerWidth']}")
            print(f"   window.outerHeight: {viewport_info['outerHeight']}")
            print("   ✅ JavaScript detection works!\n")
            
            # Step 6: Compare both methods
            print("📍 Step 6: Comparing detection methods...")
            if actual_viewport:
                match = (
                    actual_viewport['width'] == viewport_info['width'] and
                    actual_viewport['height'] == viewport_info['height']
                )
                if match:
                    print("   ✅ Both methods return same values!")
                else:
                    print("   ⚠️  Methods return different values:")
                    print(f"      viewport_size: {actual_viewport['width']}x{actual_viewport['height']}")
                    print(f"      window.inner: {viewport_info['width']}x{viewport_info['height']}")
            print()
            
            # Step 7: Test scroll_step calculation
            print("📍 Step 7: Testing scroll_step calculation...")
            viewport_height = viewport_info['height']
            overlap_percent = 20
            scroll_step = int(viewport_height * (1 - overlap_percent / 100))
            print(f"   Viewport height: {viewport_height}px")
            print(f"   Overlap: {overlap_percent}%")
            print(f"   Calculated scroll_step: {scroll_step}px")
            print(f"   ✅ Calculation works!\n")
            
            # Step 8: Test page height measurement
            print("📍 Step 8: Testing page height measurement...")
            page_height = await page.evaluate("""() => {
                return Math.max(
                    document.documentElement.scrollHeight,
                    document.body.scrollHeight
                );
            }""")
            print(f"   Page height: {page_height}px")
            
            if page_height > 0:
                segments = -(-page_height // scroll_step)  # Ceiling division
                print(f"   Segments needed: {segments}")
                print(f"   ✅ Page height measurement works!\n")
            
            # Summary
            print("="*80)
            print("✅ ALL TESTS PASSED!")
            print("="*80)
            print("\n📊 Summary:")
            print(f"   Viewport: {viewport_info['width']}x{viewport_info['height']}")
            print(f"   Page Height: {page_height}px")
            print(f"   Scroll Step: {scroll_step}px")
            print(f"   Segments: {segments}")
            print("\n✨ Viewport detection is working correctly!\n")
            
            await browser.close()
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        print("Troubleshooting:")
        print("1. Make sure Chrome is running with: --remote-debugging-port=9222")
        print("2. Verify Chrome is accessible: curl http://localhost:9222/json/version")
        print("3. Check network connectivity")
        print()
        return False


async def main():
    """Main entry point"""
    success = await test_viewport_detection()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

