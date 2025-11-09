#!/usr/bin/env python3
"""
Test if Playwright and Chromium are properly installed
"""

import sys

print("=" * 70)
print("🧪 Testing Playwright Installation")
print("=" * 70)

# Test 1: Import Playwright (try rebrowser first)
print("\n1️⃣  Testing Playwright import...")
try:
    from rebrowser_playwright.async_api import async_playwright
    print("   ✅ Rebrowser Playwright library installed")
    using_rebrowser = True
except ImportError:
    try:
        from playwright.async_api import async_playwright
        print("   ✅ Standard Playwright library installed")
        using_rebrowser = False
    except ImportError as e:
        print(f"   ❌ Playwright not installed: {e}")
        sys.exit(1)

# Test 2: Check if Chromium is available
print("\n2️⃣  Testing Chromium browser availability...")
import asyncio

async def test_chromium():
    try:
        async with async_playwright() as p:
            # Try to launch Chromium
            browser = await p.chromium.launch(headless=True)
            print("   ✅ Chromium browser installed and working")
            
            # Get version
            version = browser.version
            print(f"   📦 Chromium version: {version}")
            
            await browser.close()
            return True
    except Exception as e:
        print(f"   ❌ Chromium not available: {e}")
        print("\n   💡 To install Chromium, run:")
        print("      python3 -m playwright install chromium")
        return False

# Run test
result = asyncio.run(test_chromium())

print("\n" + "=" * 70)
if result:
    print("✅ All tests passed! Bot Detection Testing Framework is ready!")
    print("\n🚀 Next steps:")
    print("   python3 brain_bottest.py init    # Create example scenarios")
    print("   python3 brain_bottest.py run     # Run tests")
else:
    print("⚠️  Chromium browser needs to be installed")
    print("\n🔧 Run this command:")
    if using_rebrowser:
        print("   python3 -m rebrowser_playwright install chromium")
    else:
        print("   python3 -m playwright install chromium")
print("=" * 70)

