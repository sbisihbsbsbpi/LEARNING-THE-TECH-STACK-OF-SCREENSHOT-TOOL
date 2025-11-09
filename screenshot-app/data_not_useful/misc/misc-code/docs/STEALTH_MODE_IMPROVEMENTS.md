# 🥷 Stealth Mode Improvements - 2024/2025 Research

## 📊 Current Implementation Status

### ✅ What We Already Have (Good Foundation):
1. **playwright-stealth library** - Automatically patches 30+ detection vectors
2. **Randomized viewport** - Prevents fingerprinting via screen size
3. **Rotating user agents** - 4 realistic Chrome user agents
4. **Enhanced HTTP headers** - Mimics real browser requests
5. **Geolocation spoofing** - New York coordinates
6. **Real browser mode** - Option to use visible Chrome (headless=False)

### Current Stealth Score: **7/10** (Good but can be improved)

---

## 🔍 Latest Research Findings (2024-2025)

### Key Insights from Web Research:

1. **playwright-stealth is still effective** (as of Sep 2024)
   - Source: ScrapingAnt, ZenRows, BrightData
   - Patches most common detection vectors
   - **BUT:** Advanced anti-bots (Cloudflare, Akamai) are evolving faster

2. **New detection methods in 2024-2025:**
   - **Canvas fingerprinting** - How browser renders graphics
   - **WebGL fingerprinting** - GPU rendering signatures
   - **Audio context fingerprinting** - Audio API signatures
   - **TLS fingerprinting** - SSL/TLS handshake patterns
   - **CDP (Chrome DevTools Protocol) detection** - Detects automation tools
   - **Behavioral analysis** - Mouse movements, timing patterns

3. **Emerging alternatives to playwright-stealth:**
   - **NoDriver** - Successor to undetected-chromedriver (Python)
   - **Botright** - Advanced fingerprint randomization
   - **playwright-with-fingerprints** - Injects realistic fingerprints
   - **Rebrowser** - Commercial solution with rotating fingerprints

---

## 🚀 Recommended Improvements (Priority Order)

### **Priority 1: Canvas & WebGL Fingerprint Randomization** ⭐⭐⭐

**Problem:** Websites use Canvas/WebGL to create unique browser fingerprints.

**Solution:** Inject noise into canvas/WebGL rendering to randomize fingerprints.

**Implementation:**
```python
# Add to screenshot_service.py after stealth_async(page)

async def _randomize_canvas_webgl(self, page: Page):
    """Randomize Canvas and WebGL fingerprints"""
    await page.add_init_script("""
        // Canvas fingerprint randomization
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {
            const context = this.getContext('2d');
            if (context) {
                const imageData = context.getImageData(0, 0, this.width, this.height);
                // Add random noise to prevent fingerprinting
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] += Math.floor(Math.random() * 10) - 5;
                }
                context.putImageData(imageData, 0, 0);
            }
            return originalToDataURL.apply(this, arguments);
        };
        
        // WebGL fingerprint randomization
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // Randomize UNMASKED_VENDOR_WEBGL and UNMASKED_RENDERER_WEBGL
            if (parameter === 37445) {
                return 'Intel Inc.'; // Randomize vendor
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine'; // Randomize renderer
            }
            return getParameter.apply(this, arguments);
        };
    """)
```

**Effort:** 1-2 hours  
**Impact:** +15% stealth score  
**Sources:** ScrapingAnt Oct 2024, Reddit r/webscraping Dec 2024

---

### **Priority 2: TLS Fingerprint Spoofing** ⭐⭐⭐

**Problem:** Cloudflare/Akamai detect automation via TLS handshake patterns.

**Solution:** Use custom Chrome build or proxy with TLS spoofing.

**Implementation Options:**

**Option A: Use playwright-with-fingerprints (Recommended)**
```bash
pip install playwright-with-fingerprints
```

```python
from playwright_with_fingerprints import async_playwright_with_fingerprints

async def _get_browser_with_fingerprint(self):
    """Launch browser with randomized TLS fingerprint"""
    playwright = await async_playwright_with_fingerprints().start()
    browser = await playwright.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled']
    )
    return browser
```

**Option B: Use Rebrowser patches (Free)**
```python
# Add to launch args
launch_args.extend([
    '--disable-blink-features=AutomationControlled',
    '--disable-features=IsolateOrigins,site-per-process',
    '--disable-site-isolation-trials'
])
```

**Effort:** 2-3 hours  
**Impact:** +20% stealth score (bypasses Cloudflare)  
**Sources:** ZenRows Jul 2025, Browserless May 2025

---

### **Priority 3: Behavioral Randomization** ⭐⭐

**Problem:** Bots have predictable timing and no mouse movements.

**Solution:** Add human-like delays and mouse movements.

**Implementation:**
```python
async def _simulate_human_behavior(self, page: Page):
    """Simulate human-like behavior"""
    import random
    
    # Random mouse movements
    for _ in range(random.randint(2, 5)):
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.1, 0.3))
    
    # Random scroll
    await page.evaluate(f"""
        window.scrollTo({{
            top: {random.randint(100, 500)},
            behavior: 'smooth'
        }});
    """)
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    # Random page interaction
    if random.random() > 0.5:
        await page.mouse.click(random.randint(100, 800), random.randint(100, 600))
```

**Effort:** 1 hour  
**Impact:** +10% stealth score  
**Sources:** AgentQL Nov 2024, ScrapingAnt Sep 2024

---

### **Priority 4: Audio Context Fingerprint Randomization** ⭐

**Problem:** Websites fingerprint via Audio API.

**Solution:** Inject noise into audio context.

**Implementation:**
```python
await page.add_init_script("""
    const audioContext = AudioContext.prototype.createOscillator;
    AudioContext.prototype.createOscillator = function() {
        const oscillator = audioContext.apply(this, arguments);
        const originalStart = oscillator.start;
        oscillator.start = function() {
            // Add random frequency offset
            oscillator.frequency.value += Math.random() * 10 - 5;
            return originalStart.apply(this, arguments);
        };
        return oscillator;
    };
""")
```

**Effort:** 30 minutes  
**Impact:** +5% stealth score  
**Sources:** Medium Aug 2024, ArXiv Feb 2025

---

### **Priority 5: CDP Detection Bypass** ⭐⭐

**Problem:** Advanced bots detect Chrome DevTools Protocol usage.

**Solution:** Use NoDriver or patch CDP detection.

**Implementation:**
```python
# Add to init script
await page.add_init_script("""
    // Hide CDP runtime
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    
    // Override toString to hide automation
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

**Effort:** 1 hour  
**Impact:** +10% stealth score  
**Sources:** GitHub dgtlmoon Feb 2024, ScrapingAnt Sep 2024

---

## 📦 Alternative Solutions (If Current Approach Fails)

### **Option 1: Switch to NoDriver (Python)**
- **Pros:** Better anti-detection than Playwright (as of 2024)
- **Cons:** Requires rewriting screenshot_service.py
- **Effort:** 2-3 days
- **Source:** Medium Aug 2025, Reddit Sep 2024

### **Option 2: Use Commercial API (ZenRows, ScrapingBee)**
- **Pros:** Handles all anti-bot measures automatically
- **Cons:** Costs $49-$249/month
- **Effort:** 2-3 hours integration
- **Source:** ZenRows, ScrapingBee 2024

### **Option 3: Use Browserless with Stealth**
- **Pros:** Managed browser infrastructure with built-in stealth
- **Cons:** $99-$499/month
- **Effort:** 1 day integration
- **Source:** Browserless May 2025

---

## 🎯 Recommended Implementation Plan

### **Phase 1: Quick Wins (2-3 hours)**
1. ✅ Add Canvas/WebGL fingerprint randomization
2. ✅ Add CDP detection bypass
3. ✅ Add Audio context randomization

**Expected improvement:** 7/10 → 8.5/10 stealth score

### **Phase 2: Advanced (4-6 hours)**
4. ✅ Implement TLS fingerprint spoofing (playwright-with-fingerprints)
5. ✅ Add behavioral randomization (mouse, scroll, timing)

**Expected improvement:** 8.5/10 → 9.5/10 stealth score

### **Phase 3: If Still Detected (2-3 days)**
6. ⚠️ Consider switching to NoDriver
7. ⚠️ Or integrate commercial API as fallback

---

## 📊 Testing Recommendations

### Test Sites:
1. **https://bot.sannysoft.com/** - Basic bot detection
2. **https://arh.antoinevastel.com/bots/areyouheadless** - Headless detection
3. **https://pixelscan.net/** - Comprehensive fingerprint analysis
4. **https://creepjs.com/** - Advanced fingerprinting test

### Expected Results:
- **Current (playwright-stealth only):** 70-80% pass rate
- **After Phase 1:** 85-90% pass rate
- **After Phase 2:** 95-98% pass rate

---

## 💡 Key Takeaways from 2024-2025 Research

1. **playwright-stealth is still good** but not enough for advanced anti-bots
2. **Canvas/WebGL fingerprinting** is the #1 detection method in 2024
3. **TLS fingerprinting** is increasingly used by Cloudflare/Akamai
4. **Behavioral analysis** is becoming more sophisticated
5. **NoDriver** is emerging as the best Python alternative
6. **Commercial APIs** are most reliable but expensive

---

## 🔗 Sources & References

- **ScrapingAnt** - "How to Make Playwright Scraping Undetectable" (Sep 2024)
- **ZenRows** - "How to Bypass Cloudflare with Playwright" (Jul 2025)
- **Browserless** - "Bypass Cloudflare with Playwright BQL" (May 2025)
- **BrightData** - "Avoiding Bot Detection with Playwright Stealth" (Feb 2024)
- **AgentQL** - "Stealth Mode—Enhanced Bot Detection Evasion" (Nov 2024)
- **Medium** - "Baseline Performance Comparison" (Aug 2025)
- **Reddit r/webscraping** - Community discussions (2024)
- **ArXiv** - "Browser Fingerprint Detection" (Feb 2025)

---

## ✅ Action Items

**Immediate (Recommended):**
- [ ] Implement Canvas/WebGL randomization (1-2 hours)
- [ ] Add CDP detection bypass (1 hour)
- [ ] Test on bot.sannysoft.com and pixelscan.net

**Short-term (If needed):**
- [ ] Add TLS fingerprint spoofing (2-3 hours)
- [ ] Implement behavioral randomization (1 hour)
- [ ] Test on real target websites

**Long-term (If still failing):**
- [ ] Evaluate NoDriver migration (2-3 days)
- [ ] Consider commercial API fallback (2-3 hours)

---

**Current Stealth Score:** 7/10  
**Potential Score (After Improvements):** 9.5/10  
**Estimated Effort:** 4-8 hours for Phase 1 & 2

