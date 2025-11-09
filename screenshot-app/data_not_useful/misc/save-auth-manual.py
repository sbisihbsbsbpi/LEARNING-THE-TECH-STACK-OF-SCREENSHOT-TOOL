#!/usr/bin/env python3
"""
Manual script to save auth state for Tekion app
Run with: python save-auth-manual.py
"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    print('🔓 Opening browser for manual login...')
    
    async with async_playwright() as p:
        # Launch visible Chrome browser
        browser = await p.chromium.launch(
            headless=False,
            channel='chrome'  # Use real Chrome
        )
        
        # Create context with larger viewport
        context = await browser.new_context(
            viewport={'width': 1600, 'height': 900},
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        page = await context.new_page()
        
        # Navigate to login page
        await page.goto('https://preprodapp.tekioncloud.com/home')
        
        print('✅ Browser opened!')
        print('')
        print('📋 INSTRUCTIONS:')
        print('  1. Complete your login (Okta/MFA/etc.)')
        print('  2. Wait until you see your dashboard')
        print('  3. Make sure NO errors are visible:')
        print('     - No "Your role has been changed" message')
        print('     - No "Unable to fetch" errors')
        print('     - No JSON parsing errors')
        print('  4. Press ENTER in this terminal when ready')
        print('')
        
        # Wait for user to press Enter
        input('Press ENTER when you are logged in and dashboard is fully loaded...')
        
        print('💾 Saving auth state...')
        
        # Save storage state (cookies + localStorage + sessionStorage)
        await context.storage_state(path='backend/auth_state.json')
        
        print('✅ Auth state saved to backend/auth_state.json')
        print('')
        print('📊 You can now close the browser and use the screenshot tool!')
        
        await browser.close()
        
        print('🎉 Done! The screenshot tool will automatically use this auth state.')

if __name__ == '__main__':
    asyncio.run(main())

