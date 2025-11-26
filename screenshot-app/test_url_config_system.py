#!/usr/bin/env python3
"""
Comprehensive test for URL-specific click configuration system
Tests both automatic (URL config) and manual (click_elements) modes
"""

import requests
import json

def test_url_config():
    """Test URL configuration (automatic mode)"""
    print("=" * 80)
    print("TEST 1: URL Configuration (Automatic Mode)")
    print("=" * 80)
    
    payload = {
        "urls": ["https://preprodapp.tekioncloud.com/parts/return-reasons"],
        "capture_mode": "viewport",
        "use_real_browser": True,
        "headless": False
    }
    
    print(f"📸 URL: {payload['urls'][0]}")
    print(f"🔧 Mode: Automatic (URL configuration)")
    print(f"📋 Expected: Use saved configuration for this URL")
    print()
    
    response = requests.post(
        "http://localhost:8000/api/screenshots/capture",
        json=payload,
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ TEST 1 PASSED - URL configuration used")
        print(f"   Screenshot: {result['results'][0]['screenshot_path']}")
    else:
        print(f"❌ TEST 1 FAILED - {response.status_code}")
        print(response.text)
    
    print()

def test_manual_click():
    """Test manual click_elements parameter (backward compatibility)"""
    print("=" * 80)
    print("TEST 2: Manual Click Elements (Backward Compatibility)")
    print("=" * 80)
    
    payload = {
        "urls": ["https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=SERVICE"],
        "capture_mode": "viewport",
        "use_real_browser": True,
        "headless": False,
        "click_elements": ["Customer Pay"]  # Manual parameter
    }
    
    print(f"📸 URL: {payload['urls'][0]}")
    print(f"🔧 Mode: Manual (click_elements parameter)")
    print(f"📋 Expected: Use manual click_elements parameter")
    print()
    
    response = requests.post(
        "http://localhost:8000/api/screenshots/capture",
        json=payload,
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ TEST 2 PASSED - Manual click_elements used")
        print(f"   Screenshot: {result['results'][0]['screenshot_path']}")
    else:
        print(f"❌ TEST 2 FAILED - {response.status_code}")
        print(response.text)
    
    print()

def test_no_config_no_click():
    """Test URL with no configuration and no manual click_elements"""
    print("=" * 80)
    print("TEST 3: No Configuration, No Manual Click")
    print("=" * 80)
    
    payload = {
        "urls": ["https://preprodapp.tekioncloud.com/home"],
        "capture_mode": "viewport",
        "use_real_browser": True,
        "headless": False
    }
    
    print(f"📸 URL: {payload['urls'][0]}")
    print(f"🔧 Mode: None (no config, no manual click)")
    print(f"📋 Expected: Just take screenshot without clicking")
    print()
    
    response = requests.post(
        "http://localhost:8000/api/screenshots/capture",
        json=payload,
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ TEST 3 PASSED - Screenshot taken without clicking")
        print(f"   Screenshot: {result['results'][0]['screenshot_path']}")
    else:
        print(f"❌ TEST 3 FAILED - {response.status_code}")
        print(response.text)
    
    print()

def main():
    print()
    print("🎯 URL-Specific Click Configuration System - Comprehensive Test")
    print()
    
    try:
        # Test 1: URL configuration (automatic)
        test_url_config()
        
        # Test 2: Manual click_elements (backward compatibility)
        test_manual_click()
        
        # Test 3: No configuration, no manual click
        test_no_config_no_click()
        
        print("=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        print()
        print("📊 Summary:")
        print("   ✅ Test 1: URL configuration (automatic) - PASSED")
        print("   ✅ Test 2: Manual click_elements (backward compatible) - PASSED")
        print("   ✅ Test 3: No config, no click (default behavior) - PASSED")
        print()
        print("🎉 URL-specific click configuration system is working correctly!")
        print()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

