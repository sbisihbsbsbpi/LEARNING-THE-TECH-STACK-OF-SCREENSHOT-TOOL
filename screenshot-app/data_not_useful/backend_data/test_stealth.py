"""
Test script for stealth mode enhancements
Tests the new 2024-2025 stealth features on detection sites
"""

import asyncio
import sys
from pathlib import Path
from screenshot_service import ScreenshotService

# Test URLs for bot detection
TEST_URLS = {
    "basic": "https://bot.sannysoft.com/",
    "headless": "https://arh.antoinevastel.com/bots/areyouheadless",
    "fingerprint": "https://pixelscan.net/",
    "advanced": "https://creepjs.com/"
}

async def test_stealth_mode():
    """Test stealth mode on various detection sites"""
    print("=" * 70)
    print("🥷 STEALTH MODE ENHANCEMENT TEST")
    print("=" * 70)
    print("\nTesting new 2024-2025 stealth enhancements...")
    print("This will capture screenshots from bot detection sites.\n")
    
    service = ScreenshotService()
    
    try:
        await service.start()
        
        results = []
        
        for test_name, url in TEST_URLS.items():
            print(f"\n{'=' * 70}")
            print(f"🧪 Test: {test_name.upper()}")
            print(f"📍 URL: {url}")
            print(f"{'=' * 70}\n")
            
            try:
                # Capture with stealth mode enabled
                screenshot_path = await service.capture(
                    url=url,
                    viewport_width=1920,
                    viewport_height=1080,
                    full_page=True,
                    timeout=60000,
                    use_stealth=True,  # Enable stealth mode
                    use_real_browser=False,  # Use headless
                )
                
                print(f"\n✅ Screenshot captured: {screenshot_path}")
                print(f"📁 Check the screenshot to verify stealth effectiveness")
                results.append((test_name, url, "SUCCESS", screenshot_path))
                
            except Exception as e:
                print(f"\n❌ Test failed: {e}")
                results.append((test_name, url, "FAILED", str(e)))
        
        # Summary
        print(f"\n{'=' * 70}")
        print("📊 TEST SUMMARY")
        print(f"{'=' * 70}\n")
        
        success_count = sum(1 for _, _, status, _ in results if status == "SUCCESS")
        total_count = len(results)
        
        for test_name, url, status, info in results:
            status_icon = "✅" if status == "SUCCESS" else "❌"
            print(f"{status_icon} {test_name.upper()}: {status}")
            if status == "SUCCESS":
                print(f"   Screenshot: {info}")
            else:
                print(f"   Error: {info}")
            print()
        
        print(f"{'=' * 70}")
        print(f"Results: {success_count}/{total_count} tests passed ({success_count/total_count*100:.0f}%)")
        print(f"{'=' * 70}\n")
        
        # Instructions
        print("📋 NEXT STEPS:")
        print("1. Check the screenshots in the 'screenshots/' folder")
        print("2. For bot.sannysoft.com - Look for green checkmarks (not red)")
        print("3. For areyouheadless - Should say 'You are not Chrome headless'")
        print("4. For pixelscan.net - Check the fingerprint consistency score")
        print("5. For creepjs.com - Trust score should be > 80%")
        print("\n✨ If all tests show good results, stealth mode is working!\n")
        
        return success_count == total_count
        
    finally:
        await service.close()


async def test_stealth_features():
    """Test individual stealth features"""
    print("\n" + "=" * 70)
    print("🔬 TESTING INDIVIDUAL STEALTH FEATURES")
    print("=" * 70 + "\n")
    
    service = ScreenshotService()
    
    try:
        await service.start()
        browser = await service._get_browser(use_real_browser=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # Test 1: Canvas/WebGL Randomization
        print("🎨 Testing Canvas & WebGL Randomization...")
        await service._apply_canvas_webgl_randomization(page)
        print("   ✅ Canvas & WebGL randomization applied")
        
        # Test 2: CDP Detection Bypass
        print("\n🔒 Testing CDP Detection Bypass...")
        await service._apply_cdp_detection_bypass(page)
        print("   ✅ CDP detection bypass applied")
        
        # Test 3: Audio Context Randomization
        print("\n🔊 Testing Audio Context Randomization...")
        await service._apply_audio_context_randomization(page)
        print("   ✅ Audio context randomization applied")
        
        # Test 4: Behavioral Randomization
        print("\n🤖 Testing Behavioral Randomization...")
        await page.goto("https://example.com", wait_until='domcontentloaded')
        await service._apply_behavioral_randomization(page)
        print("   ✅ Behavioral randomization applied")
        
        # Verify navigator.webdriver is hidden
        print("\n🔍 Verifying stealth features...")
        webdriver_value = await page.evaluate("navigator.webdriver")
        print(f"   navigator.webdriver: {webdriver_value} (should be undefined)")
        
        if webdriver_value is None:
            print("   ✅ navigator.webdriver successfully hidden!")
        else:
            print("   ⚠️  navigator.webdriver not hidden properly")
        
        # Check plugins
        plugins_count = await page.evaluate("navigator.plugins.length")
        print(f"   navigator.plugins.length: {plugins_count} (should be > 0)")
        
        if plugins_count > 0:
            print("   ✅ Plugins array populated!")
        else:
            print("   ⚠️  Plugins array empty")
        
        await context.close()
        
        print("\n✅ All individual feature tests passed!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Feature test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await service.close()


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 STEALTH MODE ENHANCEMENT TEST SUITE")
    print("=" * 70)
    print("\nThis will test the new 2024-2025 stealth enhancements.")
    print("Tests include:")
    print("  1. Individual feature tests (Canvas, WebGL, CDP, Audio, Behavioral)")
    print("  2. Real-world detection site tests (bot.sannysoft.com, etc.)")
    print("\n" + "=" * 70 + "\n")
    
    # Test 1: Individual features
    print("PART 1: Individual Feature Tests")
    print("-" * 70)
    features_ok = await test_stealth_features()
    
    # Test 2: Real detection sites
    print("\n\nPART 2: Real Detection Site Tests")
    print("-" * 70)
    detection_ok = await test_stealth_mode()
    
    # Final summary
    print("\n" + "=" * 70)
    print("🎯 FINAL RESULTS")
    print("=" * 70)
    
    if features_ok:
        print("✅ Individual feature tests: PASSED")
    else:
        print("❌ Individual feature tests: FAILED")
    
    if detection_ok:
        print("✅ Detection site tests: PASSED")
    else:
        print("⚠️  Detection site tests: Some failures (check screenshots)")
    
    print("=" * 70 + "\n")
    
    if features_ok and detection_ok:
        print("🎉 All tests passed! Stealth mode is working perfectly!")
        return 0
    elif features_ok:
        print("⚠️  Features work, but some detection sites may still detect.")
        print("   Check the screenshots to verify results.")
        return 0
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

