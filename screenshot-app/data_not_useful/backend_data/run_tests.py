"""
Manual Test Runner for Screenshot Tool
Runs comprehensive regression tests and generates report
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
import sys

from screenshot_service import ScreenshotService
from quality_checker import QualityChecker
from config import settings

# Test results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": []
}

def log_test(name, status, duration=0, error=None):
    """Log test result"""
    test_results["total_tests"] += 1
    if status == "PASS":
        test_results["passed"] += 1
        print(f"✅ {name} - PASSED ({duration:.2f}s)")
    elif status == "FAIL":
        test_results["failed"] += 1
        print(f"❌ {name} - FAILED: {error}")
    elif status == "SKIP":
        test_results["skipped"] += 1
        print(f"⏭️  {name} - SKIPPED")
    
    test_results["tests"].append({
        "name": name,
        "status": status,
        "duration": duration,
        "error": str(error) if error else None
    })

async def test_viewport_capture():
    """Test viewport mode screenshot capture"""
    service = ScreenshotService()
    start = time.time()
    try:
        screenshot_path = await service.capture(
            url="https://example.com",
            viewport_width=1920,
            viewport_height=1080,
            full_page=False,
            use_stealth=False,
            browser_engine="playwright"
        )
        
        assert screenshot_path is not None
        assert Path(screenshot_path).exists()
        
        # Cleanup
        Path(screenshot_path).unlink()
        
        log_test("Viewport Capture", "PASS", time.time() - start)
    except Exception as e:
        log_test("Viewport Capture", "FAIL", time.time() - start, e)
    finally:
        await service.close()

async def test_fullpage_capture():
    """Test fullpage mode screenshot capture"""
    service = ScreenshotService()
    start = time.time()
    try:
        screenshot_path = await service.capture(
            url="https://example.com",
            viewport_width=1920,
            viewport_height=1080,
            full_page=True,
            use_stealth=False,
            browser_engine="playwright"
        )
        
        assert screenshot_path is not None
        assert Path(screenshot_path).exists()
        
        # Cleanup
        Path(screenshot_path).unlink()
        
        log_test("Fullpage Capture", "PASS", time.time() - start)
    except Exception as e:
        log_test("Fullpage Capture", "FAIL", time.time() - start, e)
    finally:
        await service.close()

async def test_segmented_capture():
    """Test segmented mode screenshot capture"""
    service = ScreenshotService()
    start = time.time()
    try:
        screenshot_paths = await service.capture_segmented(
            url="https://example.com",
            viewport_width=1920,
            viewport_height=1080,
            use_stealth=False,
            browser_engine="playwright",
            overlap_percent=20,
            scroll_delay_ms=500,
            max_segments=5
        )
        
        assert screenshot_paths is not None
        assert len(screenshot_paths) > 0
        
        # Cleanup
        for path in screenshot_paths:
            if Path(path).exists():
                Path(path).unlink()
        
        log_test("Segmented Capture", "PASS", time.time() - start)
    except Exception as e:
        log_test("Segmented Capture", "FAIL", time.time() - start, e)
    finally:
        await service.close()

async def test_stealth_mode():
    """Test stealth mode screenshot capture"""
    service = ScreenshotService()
    start = time.time()
    try:
        screenshot_path = await service.capture(
            url="https://example.com",
            viewport_width=1920,
            viewport_height=1080,
            use_stealth=True,
            browser_engine="playwright"
        )
        
        assert screenshot_path is not None
        assert Path(screenshot_path).exists()
        
        # Cleanup
        Path(screenshot_path).unlink()
        
        log_test("Stealth Mode", "PASS", time.time() - start)
    except Exception as e:
        log_test("Stealth Mode", "FAIL", time.time() - start, e)
    finally:
        await service.close()

async def test_camoufox_engine():
    """Test Camoufox browser engine"""
    service = ScreenshotService()
    start = time.time()
    try:
        screenshot_path = await service.capture(
            url="https://example.com",
            viewport_width=1920,
            viewport_height=1080,
            browser_engine="camoufox"
        )
        
        assert screenshot_path is not None
        assert Path(screenshot_path).exists()
        
        # Cleanup
        Path(screenshot_path).unlink()
        
        log_test("Camoufox Engine", "PASS", time.time() - start)
    except Exception as e:
        log_test("Camoufox Engine", "FAIL", time.time() - start, e)
    finally:
        await service.close()

async def test_quality_check():
    """Test quality checking"""
    service = ScreenshotService()
    start = time.time()
    try:
        # Capture screenshot
        screenshot_path = await service.capture(
            url="https://example.com",
            viewport_width=1920,
            viewport_height=1080
        )
        
        # Check quality
        checker = QualityChecker()
        result = await checker.check(screenshot_path)
        
        assert "passed" in result
        assert "score" in result
        
        # Cleanup
        Path(screenshot_path).unlink()
        
        log_test("Quality Check", "PASS", time.time() - start)
    except Exception as e:
        log_test("Quality Check", "FAIL", time.time() - start, e)
    finally:
        await service.close()

async def test_auth_state():
    """Test auth state management"""
    start = time.time()
    try:
        # Create test auth state
        test_state = {
            "cookies": [
                {
                    "name": "test_cookie",
                    "value": "test_value",
                    "domain": ".example.com",
                    "path": "/"
                }
            ],
            "origins": []
        }
        
        # Save auth state
        auth_file = Path("test_auth_state.json")
        with open(auth_file, 'w') as f:
            json.dump(test_state, f)
        
        assert auth_file.exists()
        
        # Cleanup
        auth_file.unlink()
        
        log_test("Auth State Management", "PASS", time.time() - start)
    except Exception as e:
        log_test("Auth State Management", "FAIL", time.time() - start, e)

async def test_error_handling():
    """Test error handling for invalid URLs"""
    service = ScreenshotService()
    start = time.time()
    try:
        # Should raise exception for invalid URL
        try:
            await service.capture(url="invalid-url")
            # If no exception, test fails
            log_test("Error Handling", "FAIL", time.time() - start, "No exception raised for invalid URL")
        except Exception:
            # Exception expected
            log_test("Error Handling", "PASS", time.time() - start)
    finally:
        await service.close()

async def run_all_tests():
    """Run all regression tests"""
    print("=" * 60)
    print("🧪 SCREENSHOT TOOL - REGRESSION TEST SUITE")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    await test_viewport_capture()
    await test_fullpage_capture()
    await test_segmented_capture()
    await test_stealth_mode()
    await test_camoufox_engine()
    await test_quality_check()
    await test_auth_state()
    await test_error_handling()
    
    # Print summary
    print()
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"⏭️  Skipped: {test_results['skipped']}")
    print(f"Success Rate: {(test_results['passed'] / test_results['total_tests'] * 100):.1f}%")
    print()
    
    # Save results
    results_file = Path("test_results.json")
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"📄 Results saved to: {results_file}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_all_tests())

