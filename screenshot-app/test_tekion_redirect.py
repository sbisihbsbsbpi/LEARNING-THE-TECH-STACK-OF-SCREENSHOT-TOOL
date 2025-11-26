#!/usr/bin/env python3
"""
Test script to check if Tekion URLs redirect
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

async def test_redirect():
    """Test if URLs redirect"""
    
    # Load cookies
    storage_file = Path("browser_sessions/playwright_storage_state.json")
    if not storage_file.exists():
        print("❌ No cookies found. Please extract cookies first.")
        return
    
    # Load and fix storage state
    with open(storage_file, 'r') as f:
        storage_state = json.load(f)
    
    # Fix cookie expires format
    if 'cookies' in storage_state:
        for cookie in storage_state['cookies']:
            if 'expires' in cookie and not isinstance(cookie['expires'], (int, float)):
                cookie['expires'] = -1
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            storage_state=storage_state,
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # Test URLs
        test_urls = [
            "https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=SERVICE",
            "https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=NEW_VEHICLE",
            "https://preprodapp.tekioncloud.com/accounting/glaccountmapping/list?module=TEKION_PAY"
        ]
        
        for url in test_urls:
            print(f"\n{'='*80}")
            print(f"Testing: {url}")
            print(f"{'='*80}")
            
            # Navigate
            print(f"🌐 Navigating...")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Wait a bit for any JS redirects
            await asyncio.sleep(3)
            
            # Check final URL
            final_url = page.url
            print(f"📍 Initial URL:  {url}")
            print(f"📍 Final URL:    {final_url}")
            
            if url != final_url:
                print(f"⚠️  REDIRECT DETECTED!")
                print(f"   From: {url.split('module=')[1] if 'module=' in url else url}")
                print(f"   To:   {final_url.split('module=')[1] if 'module=' in final_url else final_url}")
            else:
                print(f"✅ No redirect - URL stayed the same")
            
            # Check page title
            title = await page.title()
            print(f"📄 Page title: {title}")
            
            # Wait for user to inspect
            print(f"\n⏸️  Browser will stay open for 10 seconds...")
            await asyncio.sleep(10)
        
        await browser.close()
        print(f"\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_redirect())

