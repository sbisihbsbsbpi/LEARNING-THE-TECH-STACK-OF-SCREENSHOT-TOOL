#!/usr/bin/env python3
"""
Check what tabs are currently open in Brave
"""

import asyncio
from playwright.async_api import async_playwright

async def check_tabs():
    """Check open tabs"""
    
    async with async_playwright() as p:
        print("🔗 Connecting to Brave...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        
        print(f"\n📊 Browser contexts: {len(browser.contexts)}")
        
        for i, context in enumerate(browser.contexts):
            print(f"\n📁 Context {i+1}:")
            print(f"   Pages: {len(context.pages)}")
            
            for j, page in enumerate(context.pages):
                url = page.url
                title = await page.title()
                print(f"\n   📄 Tab {j+1}:")
                print(f"      Title: {title}")
                print(f"      URL: {url}")

if __name__ == "__main__":
    asyncio.run(check_tabs())

