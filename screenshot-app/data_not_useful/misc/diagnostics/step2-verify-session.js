// Step 2: Verify the captured session works
// Run with: node step2-verify-session.js

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  console.log('🔍 Step 2: Verifying captured session...');
  console.log('');
  
  const authFile = path.join(__dirname, '../backend/auth_state.json');
  
  // Check if auth file exists
  if (!fs.existsSync(authFile)) {
    console.log('❌ Error: auth_state.json not found!');
    console.log('   Run step1-capture-fresh.js first to capture the session.');
    process.exit(1);
  }
  
  // Read and analyze auth file
  const authData = JSON.parse(fs.readFileSync(authFile, 'utf8'));
  
  console.log('📄 Auth file analysis:');
  console.log(`   🍪 Cookies: ${authData.cookies?.length || 0}`);
  console.log(`   🌐 Origins: ${authData.origins?.length || 0}`);
  
  if (authData.origins && authData.origins.length > 0) {
    const totalLS = authData.origins.reduce((sum, origin) => {
      return sum + (origin.localStorage?.length || 0);
    }, 0);
    console.log(`   💾 localStorage items: ${totalLS}`);
  } else {
    console.log('   ⚠️  WARNING: No localStorage section found!');
  }
  
  // Check cookie expiry
  console.log('');
  console.log('⏰ Cookie expiry check:');
  
  const now = Date.now() / 1000;
  let hasExpired = false;
  let expiringSoon = false;
  
  authData.cookies.forEach(cookie => {
    if (cookie.expires > 0) {
      const expiresDate = new Date(cookie.expires * 1000);
      const hoursUntilExpiry = (cookie.expires - now) / 3600;
      
      if (cookie.expires < now) {
        console.log(`   ❌ ${cookie.name}: EXPIRED (${expiresDate.toLocaleString()})`);
        hasExpired = true;
      } else if (hoursUntilExpiry < 1) {
        console.log(`   ⚠️  ${cookie.name}: Expires soon (${Math.round(hoursUntilExpiry * 60)} minutes)`);
        expiringSoon = true;
      } else if (hoursUntilExpiry < 24) {
        console.log(`   ⏰ ${cookie.name}: Expires in ${Math.round(hoursUntilExpiry)} hours`);
      }
    }
  });
  
  if (hasExpired) {
    console.log('');
    console.log('❌ Some cookies are EXPIRED! Re-capture the session with step1-capture-fresh.js');
    process.exit(1);
  }
  
  if (expiringSoon) {
    console.log('');
    console.log('⚠️  Some cookies expire soon. Session may fail shortly.');
  }
  
  console.log('');
  console.log('🚀 Testing session with headless browser...');
  
  const browser = await chromium.launch({ 
    headless: true  // Test in headless mode
  });
  
  try {
    const context = await browser.newContext({ 
      storageState: authFile,
      viewport: { width: 1920, height: 1080 },
      locale: 'en-US',
      timezone_id: 'America/New_York',
    });
    
    const page = await context.newPage();
    
    // Test URL
    const testUrl = 'https://preprodapp.tekioncloud.com/';
    
    console.log(`📍 Navigating to: ${testUrl}`);
    await page.goto(testUrl, {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    
    // Wait a bit for page to load
    await page.waitForTimeout(3000);
    
    const finalUrl = page.url();
    console.log(`   Final URL: ${finalUrl}`);
    
    // Check if redirected to Okta login
    if (finalUrl.includes('okta.com') || finalUrl.includes('login')) {
      console.log('');
      console.log('❌ FAILED: Redirected to login page!');
      console.log('   The session was not accepted by the server.');
      console.log('');
      console.log('Possible causes:');
      console.log('  1. Session expired server-side');
      console.log('  2. Okta device binding (requires same machine/browser)');
      console.log('  3. IP address changed');
      console.log('  4. Session was invalidated (logout, password change, etc.)');
      console.log('');
      console.log('Solutions:');
      console.log('  - Re-capture session with step1-capture-fresh.js');
      console.log('  - Run headless browser on same machine where you logged in');
      console.log('  - Ask IT for a non-MFA automation account');
      
      await browser.close();
      process.exit(1);
    }
    
    // Check page content
    const pageState = await page.evaluate(() => {
      const bodyText = document.body.innerText;
      return {
        hasRoleChangeError: bodyText.includes('Your role has been changed'),
        hasUnableToFetchError: bodyText.includes('Unable to fetch'),
        hasJSONError: bodyText.includes('Unexpected token') || bodyText.includes('valid JSON'),
        hasLoginForm: bodyText.toLowerCase().includes('sign in') || bodyText.toLowerCase().includes('log in'),
        title: document.title,
        bodyLength: bodyText.length
      };
    });
    
    console.log(`   Page title: ${pageState.title}`);
    console.log(`   Body length: ${pageState.bodyLength} chars`);
    
    if (pageState.hasLoginForm) {
      console.log('');
      console.log('❌ FAILED: Login form detected on page!');
      console.log('   The session is not working.');
      await browser.close();
      process.exit(1);
    }
    
    if (pageState.hasRoleChangeError) {
      console.log('');
      console.log('❌ FAILED: "Your role has been changed" error detected!');
      console.log('   The session was captured too early (before role initialization).');
      console.log('   Re-run step1-capture-fresh.js and wait longer before pressing ENTER.');
      await browser.close();
      process.exit(1);
    }
    
    if (pageState.hasUnableToFetchError || pageState.hasJSONError) {
      console.log('');
      console.log('⚠️  WARNING: Errors detected on page!');
      console.log('   The session may be incomplete or corrupted.');
    }
    
    // Take a test screenshot
    console.log('');
    console.log('📸 Taking test screenshot...');
    await page.screenshot({ 
      path: path.join(__dirname, 'test-screenshot.png'),
      fullPage: false
    });
    
    console.log('   ✅ Screenshot saved to diagnostics/test-screenshot.png');
    console.log('');
    console.log('✅ SUCCESS! Session is working!');
    console.log('');
    console.log('📝 Next steps:');
    console.log('  1. Check test-screenshot.png to verify it shows the dashboard (not login page)');
    console.log('  2. If it looks good, your screenshot tool should work now!');
    console.log('  3. If you see errors, run step3-debug-cookies.js for detailed analysis');
    
  } catch (error) {
    console.error('');
    console.error('❌ Error during verification:', error.message);
  } finally {
    await browser.close();
  }
})();

