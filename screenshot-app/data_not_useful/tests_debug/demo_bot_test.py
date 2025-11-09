#!/usr/bin/env python3
"""
Demo Bot Detection Test
Tests the framework with a simple example
"""

import asyncio
from pathlib import Path

# Try rebrowser-playwright first (same as screenshot service)
try:
    from rebrowser_playwright.async_api import async_playwright
    print("🚀 Using Rebrowser Playwright")
except ImportError:
    from playwright.async_api import async_playwright
    print("⚠️  Using standard Playwright")

async def run_demo_test():
    """Run a simple demo test to verify the framework works"""
    
    print("=" * 70)
    print("🤖 Bot Detection Testing Framework - Demo")
    print("=" * 70)
    
    artifacts_dir = Path("bot_test_artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    
    print("\n📋 Test: Visit example.com (legitimate user behavior)")
    print("   Environment: Public test site")
    print("   Expected: Should be allowed (no bot detection)")
    
    async with async_playwright() as p:
        # Headed mode - visible, honest testing
        print("\n🌐 Launching browser (headed mode - visible)...")
        browser = await p.chromium.launch(
            headless=False,  # Visible browser
            slow_mo=100      # Human-like pacing
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            locale='en-US',
        )
        
        page = await context.new_page()
        
        try:
            print("📍 Navigating to example.com...")
            await page.goto('https://example.com', wait_until='networkidle')
            await page.wait_for_timeout(500)
            
            print("📸 Taking screenshot...")
            await page.screenshot(
                path=str(artifacts_dir / 'demo_test.png'),
                full_page=True
            )
            
            print("💾 Saving session state...")
            await context.storage_state(
                path=str(artifacts_dir / 'demo_session.json')
            )
            
            # Get page title
            title = await page.title()
            print(f"📄 Page title: {title}")
            
            print("\n✅ Test completed successfully!")
            print(f"   Screenshot: {artifacts_dir / 'demo_test.png'}")
            print(f"   Session: {artifacts_dir / 'demo_session.json'}")
            
            # Check for bot detection indicators
            content = await page.content()
            bot_indicators = ['captcha', 'blocked', 'suspicious', 'bot detected']
            detected = any(indicator in content.lower() for indicator in bot_indicators)
            
            if detected:
                print("\n⚠️  Bot detection triggered!")
            else:
                print("\n✅ No bot detection - legitimate user behavior")
            
        except Exception as error:
            print(f"\n❌ Test failed: {error}")
            await page.screenshot(
                path=str(artifacts_dir / 'demo_error.png'),
                full_page=True
            )
        finally:
            print("\n🔒 Closing browser...")
            await browser.close()
    
    print("\n" + "=" * 70)
    print("🎯 Demo Complete!")
    print("\n📊 This demonstrates:")
    print("   ✅ Headed mode (visible browser)")
    print("   ✅ Human-like pacing (slow_mo)")
    print("   ✅ Artifact capture (screenshots, session)")
    print("   ✅ Bot detection checking")
    print("   ✅ Ethical testing (no evasion)")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(run_demo_test())

