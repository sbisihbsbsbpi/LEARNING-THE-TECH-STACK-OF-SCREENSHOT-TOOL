#!/usr/bin/env python3
"""
Test screenshot with click element feature
Demonstrates clicking on "Customer Return w/ Restocking" before taking screenshot
"""

import requests
import json
import time

def test_screenshot_with_click():
    """Test screenshot with click element"""
    
    url = "http://localhost:8000/api/screenshots/capture"
    
    payload = {
        "urls": ["https://preprodapp.tekioncloud.com/parts/return-reasons"],
        "capture_mode": "viewport",  # Use viewport mode to capture the modal
        "use_real_browser": True,  # Use CDP mode
        "headless": False,  # Keep browser visible
        "viewport_width": 1920,
        "viewport_height": 1080,
        "click_elements": ["Customer Return w/ Restocking"]  # ✅ NEW: Click this element before screenshot
    }
    
    print("📸 Capturing screenshot with click element...")
    print(f"   URL: {payload['urls'][0]}")
    print(f"   Click element: {payload['click_elements']}")
    print()
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Screenshot captured successfully!")
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_screenshot_with_click()

