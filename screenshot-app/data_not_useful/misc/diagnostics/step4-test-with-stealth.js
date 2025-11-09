// Step 4: Test with stealth mode (anti-detection)
// Run with: node step4-test-with-stealth.js

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  console.log('🥷 Step 4: Testing with stealth mode...');
  console.log('');
  
  const authFile = path.join(__dirname, '../backend/auth_state.json');
  
  if (!fs.existsSync(authFile)) {
    console.log('❌ Error: auth_state.json not found!');
    process.exit(1);
  }
  
  console.log('🚀 Launching browser with stealth settings...');
  
  const browser = await chromium.launch({ 
    headless: true,
    channel: 'chrome',
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process',
      '--enable-features=NetworkService,NetworkServiceInProcess',
    ]
  });
  
  try {
    const context = await browser.newContext({ 
      storageState: authFile,
      viewport: { width: 1920, height: 1080 },
      locale: 'en-US',
      timezone_id: 'America/New_York',
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      extraHTTPHeaders: {
        'Accept-Language': 'en-US,en;q=0.9',
      }
    });
    
    // Add stealth scripts
    await context.addInitScript(() => {
      // Remove webdriver flag
      Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
      });
      
      // Mock plugins
      Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
      });
      
      // Mock languages
      Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
      });
      
      // Chrome runtime
      window.chrome = {
        runtime: {},
      };
      
      // Permissions
      const originalQuery = window.navigator.permissions.query;
      window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
          Promise.resolve({ state: Notification.permission }) :
          originalQuery(parameters)
      );
    });
    
    const page = await context.newPage();
    
    console.log('📍 Navigating to Tekion app...');
    await page.goto('https://preprodapp.tekioncloud.com/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    
    await page.waitForTimeout(3000);
    
    const finalUrl = page.url();
    console.log(`   Final URL: ${finalUrl}`);
    
    // Check if redirected to login
    if (finalUrl.includes('okta.com') || finalUrl.includes('login')) {
      console.log('');
      console.log('❌ FAILED: Still redirected to login even with stealth mode!');
      console.log('');
      console.log('This confirms the issue is NOT bot detection.');
      console.log('The session itself is being rejected by the server.');
      console.log('');
      console.log('Likely causes:');
      console.log('  1. Session expired server-side');
      console.log('  2. Okta device binding (requires same device)');
      console.log('  3. IP address restriction');
      console.log('');
      await browser.close();
      process.exit(1);
    }
    
    // Check page state
    const pageState = await page.evaluate(() => {
      const bodyText = document.body.innerText;
      return {
        hasRoleChangeError: bodyText.includes('Your role has been changed'),
        hasUnableToFetchError: bodyText.includes('Unable to fetch'),
        hasJSONError: bodyText.includes('Unexpected token') || bodyText.includes('valid JSON'),
        title: document.title,
        url: window.location.href
      };
    });
    
    console.log(`   Page title: ${pageState.title}`);
    
    if (pageState.hasRoleChangeError || pageState.hasUnableToFetchError || pageState.hasJSONError) {
      console.log('');
      console.log('❌ FAILED: Errors still present with stealth mode!');
      console.log('');
      if (pageState.hasRoleChangeError) {
        console.log('   - "Your role has been changed" error');
      }
      if (pageState.hasUnableToFetchError) {
        console.log('   - "Unable to fetch" errors');
      }
      if (pageState.hasJSONError) {
        console.log('   - JSON parsing errors');
      }
      console.log('');
      console.log('The session was captured before the app fully initialized.');
      console.log('Re-run step1-capture-fresh.js and wait 3-5 minutes before saving.');
      await browser.close();
      process.exit(1);
    }
    
    console.log('');
    console.log('✅ SUCCESS with stealth mode!');
    console.log('');
    console.log('📸 Taking test screenshot...');
    
    await page.screenshot({ 
      path: path.join(__dirname, 'test-screenshot-stealth.png'),
      fullPage: false
    });
    
    console.log('   ✅ Screenshot saved to diagnostics/test-screenshot-stealth.png');
    console.log('');
    console.log('🎉 Your session is working with stealth mode!');
    console.log('   The screenshot tool should work now.');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
})();

