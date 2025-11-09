// Manual script to save auth state for Tekion app
// Run with: node save-auth-manual.js

const { chromium } = require('playwright');

(async () => {
  console.log('🔓 Opening browser for manual login...');
  
  // Launch visible Chrome browser
  const browser = await chromium.launch({ 
    headless: false,
    channel: 'chrome'  // Use real Chrome
  });
  
  // Create context with larger viewport
  const context = await browser.newContext({
    viewport: { width: 1600, height: 900 },
    locale: 'en-US',
    timezone_id: 'America/New_York',
  });
  
  const page = await context.newPage();
  
  // Navigate to login page
  await page.goto('https://preprodapp.tekioncloud.com/home');
  
  console.log('✅ Browser opened!');
  console.log('');
  console.log('📋 INSTRUCTIONS:');
  console.log('  1. Complete your login (Okta/MFA/etc.)');
  console.log('  2. Wait until you see your dashboard');
  console.log('  3. Make sure NO errors are visible:');
  console.log('     - No "Your role has been changed" message');
  console.log('     - No "Unable to fetch" errors');
  console.log('     - No JSON parsing errors');
  console.log('  4. Press ENTER in this terminal when ready');
  console.log('');
  
  // Wait for user to press Enter
  await new Promise((resolve) => {
    process.stdin.once('data', () => {
      resolve();
    });
  });
  
  console.log('💾 Saving auth state...');
  
  // Save storage state (cookies + localStorage + sessionStorage)
  await context.storageState({ path: 'backend/auth_state.json' });
  
  console.log('✅ Auth state saved to backend/auth_state.json');
  console.log('');
  console.log('📊 You can now close the browser and use the screenshot tool!');
  
  await browser.close();
  
  console.log('🎉 Done! The screenshot tool will automatically use this auth state.');
})();

