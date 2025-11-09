"""
Diagnostic script to inspect Tekion page structure and find the scrollable element
"""
import asyncio
import sys
sys.path.insert(0, '/Users/tlreddy/Documents/project 1/screenshot-app/backend')

from screenshot_service import ScreenshotService

async def diagnose():
    print("="*80)
    print("🔍 TEKION PAGE SCROLL DIAGNOSTIC")
    print("="*80)
    print()
    
    service = ScreenshotService()
    
    try:
        # Connect to Chrome
        await service._connect_to_chrome_cdp()
        
        # Create new tab
        page = await service._create_new_tab_next_to_active()
        
        # Navigate to Tekion
        url = "https://preprodapp.tekioncloud.com/accounting/autoPostingSettings"
        print(f"📋 Loading: {url}")
        print()
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
        except:
            await page.goto(url, wait_until='load', timeout=30000)
        
        # Wait for page to load
        print("⏳ Waiting 5 seconds for initial load...")
        await asyncio.sleep(5.0)

        # Try waiting for network idle
        print("⏳ Waiting for network idle...")
        try:
            await page.wait_for_load_state('networkidle', timeout=10000)
            print("   ✅ Network idle")
        except:
            print("   ⚠️  Network still active")

        # Wait even longer for Tekion
        print("⏳ Waiting additional 10 seconds for Tekion content...")
        await asyncio.sleep(10.0)

        # Try clicking/interacting with the page
        print("🖱️  Trying to interact with the page...")
        try:
            await page.evaluate("""() => {
                // Try to focus the workspace
                const workspace = document.getElementById('tekion-workspace');
                if (workspace) {
                    workspace.focus();
                    workspace.click();
                }
            }""")
            await asyncio.sleep(2.0)
        except:
            pass
        
        # Inspect page structure
        print("🔍 INSPECTING PAGE STRUCTURE...")
        print("-" * 80)
        
        result = await page.evaluate("""() => {
            const results = {
                documentHeight: {
                    scrollHeight: document.documentElement.scrollHeight,
                    offsetHeight: document.documentElement.offsetHeight,
                    clientHeight: document.documentElement.clientHeight,
                },
                bodyHeight: {
                    scrollHeight: document.body.scrollHeight,
                    offsetHeight: document.body.offsetHeight,
                    clientHeight: document.body.clientHeight,
                },
                scrollableElements: [],
                mainElement: null,
            };
            
            // Find all scrollable elements
            const allElements = document.querySelectorAll('*');
            let maxScrollHeight = 0;
            let mainScrollable = null;
            
            for (const el of allElements) {
                const style = window.getComputedStyle(el);
                const hasOverflow = (
                    style.overflow === 'auto' || 
                    style.overflow === 'scroll' ||
                    style.overflowY === 'auto' || 
                    style.overflowY === 'scroll'
                );
                
                if (hasOverflow || el.scrollHeight > el.clientHeight + 50) {
                    const info = {
                        tag: el.tagName,
                        id: el.id || '(no id)',
                        class: el.className || '(no class)',
                        scrollHeight: el.scrollHeight,
                        clientHeight: el.clientHeight,
                        offsetHeight: el.offsetHeight,
                        overflow: style.overflow,
                        overflowY: style.overflowY,
                        canScroll: el.scrollHeight > el.clientHeight,
                    };
                    
                    results.scrollableElements.push(info);
                    
                    if (el.scrollHeight > maxScrollHeight) {
                        maxScrollHeight = el.scrollHeight;
                        mainScrollable = info;
                    }
                }
            }
            
            results.mainElement = mainScrollable;
            results.totalScrollableElements = results.scrollableElements.length;
            
            return results;
        }""")
        
        print("\n📊 DOCUMENT DIMENSIONS:")
        print(f"  document.documentElement.scrollHeight: {result['documentHeight']['scrollHeight']}px")
        print(f"  document.documentElement.offsetHeight: {result['documentHeight']['offsetHeight']}px")
        print(f"  document.documentElement.clientHeight: {result['documentHeight']['clientHeight']}px")
        
        print("\n📊 BODY DIMENSIONS:")
        print(f"  document.body.scrollHeight: {result['bodyHeight']['scrollHeight']}px")
        print(f"  document.body.offsetHeight: {result['bodyHeight']['offsetHeight']}px")
        print(f"  document.body.clientHeight: {result['bodyHeight']['clientHeight']}px")
        
        print(f"\n📊 SCROLLABLE ELEMENTS FOUND: {result['totalScrollableElements']}")
        
        if result['mainElement']:
            print("\n🎯 MAIN SCROLLABLE ELEMENT:")
            main = result['mainElement']
            print(f"  Tag: {main['tag']}")
            print(f"  ID: {main['id']}")
            print(f"  Class: {main['class'][:100]}...")
            print(f"  scrollHeight: {main['scrollHeight']}px")
            print(f"  clientHeight: {main['clientHeight']}px")
            print(f"  offsetHeight: {main['offsetHeight']}px")
            print(f"  overflow: {main['overflow']}")
            print(f"  overflowY: {main['overflowY']}")
            print(f"  Can scroll: {main['canScroll']}")
        
        print("\n📋 ALL SCROLLABLE ELEMENTS:")
        print("-" * 80)
        for i, el in enumerate(result['scrollableElements'][:10], 1):  # Show top 10
            print(f"\n{i}. {el['tag']} (scrollHeight: {el['scrollHeight']}px)")
            print(f"   ID: {el['id']}")
            print(f"   Class: {el['class'][:80]}...")
            print(f"   clientHeight: {el['clientHeight']}px")
            print(f"   overflow: {el['overflow']}, overflowY: {el['overflowY']}")
        
        # Test scrolling
        print("\n" + "="*80)
        print("🧪 TESTING SCROLL BEHAVIOR")
        print("="*80)
        
        scroll_test = await page.evaluate("""() => {
            // Find element with largest scrollHeight
            let maxEl = document.documentElement;
            let maxHeight = document.documentElement.scrollHeight;
            
            const allElements = document.querySelectorAll('*');
            for (const el of allElements) {
                if (el.scrollHeight > maxHeight) {
                    maxHeight = el.scrollHeight;
                    maxEl = el;
                }
            }
            
            // Try scrolling it
            const before = maxEl.scrollTop;
            maxEl.scrollTop = 99999;
            const after = maxEl.scrollTop;
            const scrolled = after - before;
            
            // Calculate total scrollable height
            const totalHeight = after + maxEl.clientHeight;
            
            return {
                element: maxEl.tagName,
                id: maxEl.id || '(no id)',
                scrollBefore: before,
                scrollAfter: after,
                scrollDistance: scrolled,
                clientHeight: maxEl.clientHeight,
                totalScrollableHeight: totalHeight,
                canScroll: scrolled > 0,
            };
        }""")
        
        print(f"\n📊 SCROLL TEST RESULTS:")
        print(f"  Element: {scroll_test['element']}")
        print(f"  ID: {scroll_test['id']}")
        print(f"  Scroll before: {scroll_test['scrollBefore']}px")
        print(f"  Scroll after: {scroll_test['scrollAfter']}px")
        print(f"  Scrolled distance: {scroll_test['scrollDistance']}px")
        print(f"  Client height: {scroll_test['clientHeight']}px")
        print(f"  Total scrollable height: {scroll_test['totalScrollableHeight']}px")
        print(f"  Can scroll: {scroll_test['canScroll']}")
        
        print("\n" + "="*80)
        print("✅ DIAGNOSTIC COMPLETE")
        print("="*80)
        print(f"\n💡 RECOMMENDATION:")
        if scroll_test['totalScrollableHeight'] > 1500:
            print(f"   The page IS scrollable! Total height: {scroll_test['totalScrollableHeight']}px")
            print(f"   We should capture ~{scroll_test['totalScrollableHeight'] // 918 + 1} segments")
        else:
            print(f"   The page appears to be short ({scroll_test['totalScrollableHeight']}px)")
            print(f"   This might be the actual page height, or content is not loaded yet")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await service.close()

asyncio.run(diagnose())

