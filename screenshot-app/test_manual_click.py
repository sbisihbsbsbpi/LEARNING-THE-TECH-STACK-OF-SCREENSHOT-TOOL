#!/usr/bin/env python3
"""
Test manual click_elements parameter (backward compatibility test)
This should use the manual click_elements parameter since the URL is not in the config
"""

import requests
import json

# Test with a URL that's NOT in the configuration
payload = {
    "urls": ["https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=SERVICE"],
    "capture_mode": "viewport",
    "use_real_browser": True,
    "headless": False,
    "click_elements": ["Customer Pay"]  # Manual click element
}

print("📸 Testing manual click_elements (backward compatibility)...")
print(f"   URL: {payload['urls'][0]}")
print(f"   Manual click element: {payload['click_elements']}")
print()

response = requests.post(
    "http://localhost:8000/api/screenshots/capture",
    json=payload,
    timeout=120
)

if response.status_code == 200:
    print("✅ Screenshot captured successfully!")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

