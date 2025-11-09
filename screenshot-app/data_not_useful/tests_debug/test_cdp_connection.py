#!/usr/bin/env python3
"""
Test CDP Connection to Chrome
This script tests if we can connect to Chrome via CDP and get the active tab
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from screenshot_service import ScreenshotService


async def test_cdp_connection():
    """Test connecting to Chrome via CDP"""
    service = ScreenshotService()
    
    try:
        print("=" * 60)
        print("🧪 Testing CDP Connection to Chrome")
        print("=" * 60)
        print()
        
        # Test 1: Connect to Chrome
        print("Test 1: Connecting to Chrome via CDP...")
        try:
            await service._connect_to_chrome_cdp()
            print("✅ Successfully connected to Chrome!")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            print()
            print("💡 Make sure Chrome is running with remote debugging:")
            print("   ./launch-chrome-debug.sh")
            return False
        
        print()
        
        # Test 2: Get active tab
        print("Test 2: Getting active tab...")
        try:
            page = await service._get_active_tab()
            print(f"✅ Found active tab: {page.url}")
        except Exception as e:
            print(f"❌ Failed to get active tab: {e}")
            return False
        
        print()
        
        # Test 3: Navigate to a test URL
        print("Test 3: Navigating to example.com...")
        try:
            await page.goto("https://example.com", wait_until='domcontentloaded', timeout=10000)
            print(f"✅ Successfully navigated to: {page.url}")
        except Exception as e:
            print(f"❌ Failed to navigate: {e}")
            return False
        
        print()
        
        # Test 4: Take a screenshot
        print("Test 4: Taking a screenshot...")
        try:
            test_screenshot = Path("screenshots/test_cdp.png")
            test_screenshot.parent.mkdir(exist_ok=True)
            await page.screenshot(path=str(test_screenshot))
            print(f"✅ Screenshot saved: {test_screenshot}")
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")
            return False
        
        print()
        print("=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
        print()
        print("Active Tab Mode is working correctly!")
        print()
        
        return True
        
    finally:
        # Clean up
        await service.close()


if __name__ == "__main__":
    print()
    print("This script tests the Active Tab Mode feature.")
    print()
    print("Prerequisites:")
    print("  1. Chrome must be running with remote debugging")
    print("  2. Run: ./launch-chrome-debug.sh")
    print("  3. Make sure Chrome has at least one tab open")
    print()
    input("Press Enter when ready...")
    print()
    
    success = asyncio.run(test_cdp_connection())
    
    if success:
        print("✅ CDP connection test completed successfully!")
        sys.exit(0)
    else:
        print("❌ CDP connection test failed!")
        sys.exit(1)

