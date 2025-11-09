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
            slow_mo=100,  # Human-like pacing
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            locale='en-US',
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )

        page = await context.new_page()

        try:
            try:
                await page.goto("https://example.com", wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                print(f"⚠️  Navigation warning: {e}")
                # Try again with load event
                await page.goto("https://example.com", wait_until="load", timeout=30000)
            await page.wait_for_timeout(500)
            await page.wait_for_selector("h1", timeout=5000)
            await page.screenshot(path="bot_test_artifacts/example_com.png", full_page=True)

            # Capture artifacts for evidence
            await context.storage_state(path='bot_test_artifacts/Example.com - Simple Page Visit_session.json')

            print('✅ Test completed successfully')
        except Exception as error:
            print(f'❌ Test failed: {error}')
            await page.screenshot(path='bot_test_artifacts/Example.com - Simple Page Visit_error.png', full_page=True)
            raise
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
