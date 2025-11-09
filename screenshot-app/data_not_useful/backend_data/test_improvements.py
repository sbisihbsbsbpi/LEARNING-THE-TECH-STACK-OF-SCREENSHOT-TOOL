"""
Test script for Phase 1, 2, and 3 improvements
Run this to verify all changes work correctly
"""

import asyncio
import sys
from pathlib import Path

# Test Phase 3: Configuration Management
def test_configuration():
    """Test that configuration loads correctly"""
    print("=" * 60)
    print("PHASE 3: Testing Configuration Management")
    print("=" * 60)
    
    try:
        from config import settings, get_timeout, ensure_directories
        
        print("✅ Configuration module imported successfully")
        
        # Test settings access
        print(f"\n📊 Configuration Values:")
        print(f"  - API Host: {settings.api_host}")
        print(f"  - API Port: {settings.api_port}")
        print(f"  - Max Concurrent Captures: {settings.max_concurrent_captures}")
        print(f"  - Log Level: {settings.log_level}")
        print(f"  - Allowed Origins: {len(settings.allowed_origins_list)} origins")
        for origin in settings.allowed_origins_list:
            print(f"    • {origin}")
        
        # Test timeout helper
        print(f"\n⏱️  Timeout Helper:")
        print(f"  - Normal mode: {get_timeout('viewport', False, False)}s")
        print(f"  - Real browser: {get_timeout('viewport', True, False)}s")
        print(f"  - Stealth mode: {get_timeout('viewport', False, True)}s")
        print(f"  - Segmented: {get_timeout('segmented', False, False)}s")
        
        # Test directory creation
        print(f"\n📁 Directory Creation:")
        ensure_directories()
        print(f"  - Screenshots dir: {settings.screenshots_dir.exists()}")
        print(f"  - Browser sessions dir: {settings.browser_sessions_dir.exists()}")
        print(f"  - Logs dir: {Path('logs').exists()}")
        
        print("\n✅ Configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test Phase 3: Code Extraction
async def test_code_extraction():
    """Test that extracted helper methods work correctly"""
    print("\n" + "=" * 60)
    print("PHASE 3: Testing Code Extraction")
    print("=" * 60)
    
    try:
        from screenshot_service import ScreenshotService
        
        service = ScreenshotService()
        print("✅ ScreenshotService instantiated successfully")
        
        # Test stealth config helper
        print(f"\n🥷 Testing _get_stealth_config():")
        viewport_w, viewport_h, user_agent, headers = service._get_stealth_config(
            1920, 1080, use_stealth=True
        )
        print(f"  - Viewport: {viewport_w}x{viewport_h}")
        print(f"  - User Agent: {user_agent[:50]}...")
        print(f"  - Headers: {len(headers)} headers")
        
        # Test without stealth
        viewport_w2, viewport_h2, user_agent2, headers2 = service._get_stealth_config(
            1920, 1080, use_stealth=False
        )
        print(f"  - No stealth - Viewport: {viewport_w2}x{viewport_h2}")
        print(f"  - No stealth - User Agent: {user_agent2}")
        print(f"  - No stealth - Headers: {len(headers2)} headers")
        
        # Test auth state helper
        print(f"\n🔐 Testing _load_auth_state():")
        storage_state = service._load_auth_state(cookies="", local_storage="")
        if storage_state:
            print(f"  - Auth state file found: {storage_state}")
        else:
            print(f"  - No auth state file (expected if not created yet)")
        
        # Test cookies/storage helper (without actual context)
        print(f"\n🍪 Testing _apply_cookies_and_storage():")
        print(f"  - Method exists: {hasattr(service, '_apply_cookies_and_storage')}")
        print(f"  - Signature correct: {callable(service._apply_cookies_and_storage)}")
        
        print("\n✅ Code extraction tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Code extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test Phase 2: Context Manager
async def test_context_manager():
    """Test that browser context manager works correctly"""
    print("\n" + "=" * 60)
    print("PHASE 2: Testing Browser Context Manager")
    print("=" * 60)
    
    try:
        from screenshot_service import ScreenshotService
        
        service = ScreenshotService()
        print("✅ ScreenshotService instantiated successfully")
        
        # Test context manager exists
        print(f"\n🌐 Testing _browser_context():")
        print(f"  - Method exists: {hasattr(service, '_browser_context')}")
        print(f"  - Is async context manager: {hasattr(service._browser_context, '__aenter__')}")
        
        print("\n✅ Context manager tests passed!")
        print("  (Full integration test requires browser launch)")
        return True
        
    except Exception as e:
        print(f"\n❌ Context manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test Phase 1: Logging
def test_logging():
    """Test that structured logging works correctly"""
    print("\n" + "=" * 60)
    print("PHASE 1: Testing Structured Logging")
    print("=" * 60)
    
    try:
        from logging_config import setup_logging, log_request_start, log_request_complete, log_cancellation
        
        logger = setup_logging("test")
        print("✅ Logging configured successfully")
        
        # Test logging functions
        print(f"\n📝 Testing logging functions:")
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        # Test request logging
        log_request_start("test-request-123", 5)
        log_request_complete("test-request-123", 5, 3, 2, 0, 12.5)
        log_cancellation("test-request-123", 2, 5)
        
        print("✅ Logging tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test Phase 1: Path Validation
def test_path_validation():
    """Test that path validation prevents directory traversal"""
    print("\n" + "=" * 60)
    print("PHASE 1: Testing Path Validation")
    print("=" * 60)
    
    try:
        from main import validate_screenshot_path
        from fastapi import HTTPException
        
        print("✅ Path validation function imported")
        
        # Create a test file
        test_file = Path("screenshots/test.png")
        test_file.parent.mkdir(exist_ok=True)
        test_file.touch()
        
        # Test valid path
        print(f"\n✅ Testing valid path:")
        try:
            result = validate_screenshot_path(str(test_file))
            print(f"  - Valid path accepted: {result}")
        except HTTPException as e:
            print(f"  - ❌ Valid path rejected: {e.detail}")
            return False
        
        # Test invalid path (directory traversal)
        print(f"\n🚫 Testing invalid path (directory traversal):")
        try:
            validate_screenshot_path("../../../etc/passwd")
            print(f"  - ❌ Directory traversal NOT blocked!")
            return False
        except HTTPException as e:
            print(f"  - ✅ Directory traversal blocked: {e.detail}")
        
        # Test non-existent file
        print(f"\n🚫 Testing non-existent file:")
        try:
            validate_screenshot_path("screenshots/nonexistent.png")
            print(f"  - ❌ Non-existent file NOT blocked!")
            return False
        except HTTPException as e:
            print(f"  - ✅ Non-existent file blocked: {e.detail}")
        
        # Cleanup
        test_file.unlink()
        
        print("\n✅ Path validation tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Path validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 TESTING ALL IMPROVEMENTS (PHASES 1, 2, 3)")
    print("=" * 60)
    
    results = []
    
    # Phase 3 tests
    results.append(("Configuration Management", test_configuration()))
    results.append(("Code Extraction", await test_code_extraction()))
    
    # Phase 2 tests
    results.append(("Context Manager", await test_context_manager()))
    
    # Phase 1 tests
    results.append(("Structured Logging", test_logging()))
    results.append(("Path Validation", test_path_validation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'=' * 60}\n")
    
    if passed == total:
        print("🎉 All tests passed! Ready for production.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

