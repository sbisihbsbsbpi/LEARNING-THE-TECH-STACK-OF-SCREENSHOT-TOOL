"""
Debug script to see what's actually in localStorage after navigation
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def debug_localstorage():
    auth_state_path = Path("auth_state.json")
    with open(auth_state_path, 'r') as f:
        auth_state = json.load(f)
    
    print("=" * 80)
    print("🔍 LOCALSTORAGE DEBUG TEST")
    print("=" * 80)
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    
    context = await browser.new_context(
        storage_state=str(auth_state_path),
        viewport={'width': 1920, 'height': 1080}
    )
    
    page = await context.new_page()
    
    print(f"\n🌐 Navigating to https://preprodapp.tekioncloud.com/home...")
    await page.goto("https://preprodapp.tekioncloud.com/home", wait_until='networkidle', timeout=30000)
    
    print(f"📍 Final URL: {page.url}")
    
    # Get ALL localStorage items
    local_storage = await page.evaluate("""
        () => {
            const data = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                data[key] = localStorage.getItem(key);
            }
            return data;
        }
    """)
    
    print(f"\n💾 LocalStorage items ({len(local_storage)} total):")
    for key, value in local_storage.items():
        value_preview = value[:100] + "..." if len(value) > 100 else value
        print(f"   {key}: {value_preview}")
    
    # Check what SHOULD be there
    print(f"\n🔍 Expected auth tokens:")
    for origin in auth_state.get('origins', []):
        if 'preprodapp.tekioncloud.com' in origin['origin']:
            for item in origin.get('localStorage', []):
                if item['name'] in ['t_token', 't_user', 'dse_t_user', 'currentActiveDealerId']:
                    if item['name'] in local_storage:
                        print(f"   ✅ {item['name']}: FOUND")
                    else:
                        print(f"   ❌ {item['name']}: MISSING")
    
    await browser.close()
    await playwright.stop()


if __name__ == "__main__":
    asyncio.run(debug_localstorage())

