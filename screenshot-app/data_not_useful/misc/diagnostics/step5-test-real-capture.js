// Step 5: Test real screenshot capture with auth
// Run with: node step5-test-real-capture.js

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  console.log('📸 Step 5: Testing real screenshot capture...');
  console.log('');
  
  const authFile = path.join(__dirname, '../backend/auth_state.json');
  
  if (!fs.existsSync(authFile)) {
    console.log('❌ Error: auth_state.json not found!');
    console.log('   Run step1-capture-fresh.js first.');
    process.exit(1);
  }
  
  // Test URLs (sample from your 56 URLs)
  const testUrls = [
    'https://preprodapp.tekioncloud.com/',
    'https://preprodapp.tekioncloud.com/dse-v2/scheduling-settings/general',
    'https://preprodapp.tekioncloud.com/dse-v2/scheduling-settings/appointment-types',
  ];
  
  console.log(`🎯 Testing ${testUrls.length} URLs with saved auth state...`);
  console.log('');
  
  const browser = await chromium.launch({ 
    headless: true,
    channel: 'chrome',
    args: [
      '--disable-blink-features=AutomationControlled',
      '--enable-features=NetworkService,NetworkServiceInProcess',
    ]
  });
  
  try {
    const context = await browser.newContext({ 
      storageState: authFile,
      viewport: { width: 1920, height: 1080 },
      locale: 'en-US',
      timezone_id: 'America/New_York',
    });
    
    // Add stealth
    await context.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
      });
    });
    
    const page = await context.newPage();
    
    let successCount = 0;
    let failCount = 0;
    
    for (let i = 0; i < testUrls.length; i++) {
      const url = testUrls[i];
      const urlName = url.split('/').pop() || 'home';
      
      console.log(`[${i + 1}/${testUrls.length}] ${url}`);
      
      try {
        // Navigate
        await page.goto(url, {
          waitUntil: 'domcontentloaded',
          timeout: 30000
        });
        
        // Wait for page to settle
        await page.waitForTimeout(2000);
        
        const finalUrl = page.url();
        
        // Check if redirected to login
        if (finalUrl.includes('okta.com') || finalUrl.includes('login')) {
          console.log(`   ❌ FAILED: Redirected to login`);
          failCount++;
          continue;
        }
        
        // Check for errors
        const pageState = await page.evaluate(() => {
          const bodyText = document.body.innerText;
          return {
            hasRoleChangeError: bodyText.includes('Your role has been changed'),
            hasUnableToFetchError: bodyText.includes('Unable to fetch'),
            hasJSONError: bodyText.includes('Unexpected token') || bodyText.includes('valid JSON'),
            hasLoginForm: bodyText.toLowerCase().includes('sign in') || bodyText.toLowerCase().includes('log in'),
            title: document.title
          };
        });
        
        if (pageState.hasLoginForm) {
          console.log(`   ❌ FAILED: Login form detected`);
          failCount++;
          continue;
        }
        
        if (pageState.hasRoleChangeError) {
          console.log(`   ❌ FAILED: "Your role has been changed" error`);
          failCount++;
          continue;
        }
        
        if (pageState.hasUnableToFetchError || pageState.hasJSONError) {
          console.log(`   ⚠️  WARNING: Errors on page (but not login)`);
        }
        
        // Take screenshot
        const screenshotPath = path.join(__dirname, `test-capture-${i + 1}-${urlName}.png`);
        await page.screenshot({ 
          path: screenshotPath,
          fullPage: true
        });
        
        console.log(`   ✅ SUCCESS: Screenshot saved`);
        successCount++;
        
      } catch (error) {
        console.log(`   ❌ ERROR: ${error.message}`);
        failCount++;
      }
      
      console.log('');
    }
    
    console.log('═══════════════════════════════════════════════════════');
    console.log('📊 RESULTS');
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
    console.log(`Total URLs tested: ${testUrls.length}`);
    console.log(`✅ Success: ${successCount}`);
    console.log(`❌ Failed: ${failCount}`);
    console.log('');
    
    if (successCount === testUrls.length) {
      console.log('🎉 ALL TESTS PASSED!');
      console.log('');
      console.log('Your auth state is working perfectly!');
      console.log('The screenshot tool should work for all 56 URLs now.');
      console.log('');
      console.log('📝 Next steps:');
      console.log('  1. Check the test-capture-*.png files to verify quality');
      console.log('  2. Run your screenshot tool with all 56 URLs');
      console.log('  3. Enjoy automated screenshots! 🚀');
    } else if (successCount > 0) {
      console.log('⚠️  PARTIAL SUCCESS');
      console.log('');
      console.log('Some URLs worked, some failed.');
      console.log('This could mean:');
      console.log('  - Session is working but some pages have errors');
      console.log('  - Some pages require additional permissions');
      console.log('  - Some pages take longer to load');
      console.log('');
      console.log('Try increasing wait times or checking failed URLs manually.');
    } else {
      console.log('❌ ALL TESTS FAILED');
      console.log('');
      console.log('The auth state is not working.');
      console.log('');
      console.log('Troubleshooting:');
      console.log('  1. Re-run step1-capture-fresh.js');
      console.log('  2. Wait 3-5 minutes before pressing ENTER');
      console.log('  3. Make sure no errors on dashboard');
      console.log('  4. Run step2-verify-session.js to diagnose');
    }
    
  } catch (error) {
    console.error('❌ Fatal error:', error.message);
  } finally {
    await browser.close();
  }
})();

