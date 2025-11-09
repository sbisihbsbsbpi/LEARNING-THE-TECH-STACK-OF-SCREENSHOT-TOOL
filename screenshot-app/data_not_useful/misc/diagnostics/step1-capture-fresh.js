// Step 1: Capture fresh storage snapshot with proper wait
// Run with: node step1-capture-fresh.js

const { chromium } = require('playwright');

(async () => {
  console.log('🔓 Step 1: Capturing fresh auth session...');
  console.log('');
  
  const browser = await chromium.launch({ 
    headless: false,
    channel: 'chrome'  // Use real Chrome
  });
  
  const context = await browser.newContext({
    viewport: { width: 1600, height: 900 },
    locale: 'en-US',
    timezone_id: 'America/New_York',
  });
  
  const page = await context.newPage();

  try {
    // 1️⃣ Go directly to Tekion app (not Okta link)
    console.log('📍 Navigating to Tekion app...');
    await page.goto('https://preprodapp.tekioncloud.com/', {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });
    
    console.log('✅ Page loaded');
    console.log('');
    console.log('📋 INSTRUCTIONS:');
    console.log('  1. Complete full Okta login manually (including MFA)');
    console.log('  2. Wait for dashboard to FULLY load');
    console.log('  3. Make sure you see NO errors:');
    console.log('     - No "Your role has been changed" message');
    console.log('     - No "Unable to fetch" errors');
    console.log('     - No JSON parsing errors');
    console.log('  4. Wait at least 2-3 minutes for everything to initialize');
    console.log('  5. Press ENTER in this terminal when ready');
    console.log('');
    
    // Wait for user to complete login
    await new Promise((resolve) => {
      process.stdin.once('data', () => {
        resolve();
      });
    });
    
    console.log('');
    console.log('🔍 Checking current page state...');
    
    // Check what page we're on
    const currentUrl = page.url();
    console.log(`   Current URL: ${currentUrl}`);
    
    // Check for errors
    const pageState = await page.evaluate(() => {
      const bodyText = document.body.innerText;
      return {
        hasRoleChangeError: bodyText.includes('Your role has been changed'),
        hasUnableToFetchError: bodyText.includes('Unable to fetch'),
        hasJSONError: bodyText.includes('Unexpected token') || bodyText.includes('valid JSON'),
        title: document.title,
        localStorageKeys: Object.keys(localStorage),
        localStorageCount: Object.keys(localStorage).length
      };
    });
    
    console.log(`   Page title: ${pageState.title}`);
    console.log(`   localStorage items: ${pageState.localStorageCount}`);
    
    if (pageState.hasRoleChangeError) {
      console.log('   ⚠️  WARNING: "Your role has been changed" error detected!');
    }
    if (pageState.hasUnableToFetchError) {
      console.log('   ⚠️  WARNING: "Unable to fetch" errors detected!');
    }
    if (pageState.hasJSONError) {
      console.log('   ⚠️  WARNING: JSON parsing errors detected!');
    }
    
    if (pageState.hasRoleChangeError || pageState.hasUnableToFetchError || pageState.hasJSONError) {
      console.log('');
      console.log('❌ ERRORS DETECTED! Please wait longer for the page to fully load.');
      console.log('   Close this script and try again when the dashboard is error-free.');
      await browser.close();
      process.exit(1);
    }
    
    console.log('');
    console.log('💾 Saving storage state...');
    
    // 3️⃣ Save storage + cookies together
    await context.storageState({ path: '../backend/auth_state.json' });
    
    // Get detailed stats
    const cookies = await context.cookies();
    
    console.log('');
    console.log('✅ Auth session saved to backend/auth_state.json');
    console.log('');
    console.log('📊 Captured data:');
    console.log(`   🍪 Cookies: ${cookies.length}`);
    console.log(`   💾 localStorage items: ${pageState.localStorageCount}`);
    
    // Show key cookies
    const authCookies = cookies.filter(c => {
      const name = c.name.toLowerCase();
      return name.includes('token') || name.includes('auth') || 
             name.includes('session') || name.includes('sid') || 
             name.includes('jsession');
    });
    
    if (authCookies.length > 0) {
      console.log('');
      console.log('🔑 Auth cookies found:');
      authCookies.forEach(c => {
        const expires = c.expires > 0 ? new Date(c.expires * 1000).toLocaleString() : 'Session';
        console.log(`   - ${c.name} (domain: ${c.domain}, expires: ${expires})`);
      });
    }
    
    // Show key localStorage items
    const authLSKeys = pageState.localStorageKeys.filter(k => {
      const name = k.toLowerCase();
      return name.includes('token') || name.includes('auth') || 
             name.includes('user') || name.includes('session');
    });
    
    if (authLSKeys.length > 0) {
      console.log('');
      console.log('💾 Auth localStorage items found:');
      authLSKeys.forEach(k => {
        console.log(`   - ${k}`);
      });
    }
    
    console.log('');
    console.log('🎉 Done! You can now close the browser.');
    console.log('');
    console.log('📝 Next step: Run step2-verify-session.js to test the captured session');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    // Don't close browser - let user close it manually
    console.log('');
    console.log('⏳ Browser will stay open. Close it manually when done.');
  }
})();

