#!/usr/bin/env python3
import asyncio

# Try rebrowser-playwright first (same as screenshot service)
try:
    from rebrowser_playwright.async_api import async_playwright
except ImportError:
    from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        # Headed mode - visible, honest testing
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=100  # Human-like pacing
        )

        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            locale='en-US',
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        page = await context.new_page()

        try:
            await page.goto("https://example.com", wait_until="networkidle")
            await page.wait_for_timeout(500)
            await page.wait_for_selector("h1", timeout=5000)
            await page.screenshot(path="bot_test_artifacts/simple_visit.png", full_page=True)

            # Capture artifacts for evidence
            await context.storage_state(path='bot_test_artifacts/Simple Page Visit_session.json')

            print('✅ Test completed successfully')
        except Exception as error:
            print(f'❌ Test failed: {error}')
            await page.screenshot(path='bot_test_artifacts/Simple Page Visit_error.png', full_page=True)
            raise
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
