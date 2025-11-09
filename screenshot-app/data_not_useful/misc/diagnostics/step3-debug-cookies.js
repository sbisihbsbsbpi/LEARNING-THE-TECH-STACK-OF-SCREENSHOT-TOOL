// Step 3: Deep dive into cookies and storage
// Run with: node step3-debug-cookies.js

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  console.log('🔬 Step 3: Deep cookie and storage analysis...');
  console.log('');
  
  const authFile = path.join(__dirname, '../backend/auth_state.json');
  
  if (!fs.existsSync(authFile)) {
    console.log('❌ Error: auth_state.json not found!');
    process.exit(1);
  }
  
  const authData = JSON.parse(fs.readFileSync(authFile, 'utf8'));
  
  console.log('═══════════════════════════════════════════════════════');
  console.log('📄 FILE CONTENTS ANALYSIS');
  console.log('═══════════════════════════════════════════════════════');
  console.log('');
  
  // Analyze cookies
  console.log('🍪 COOKIES IN FILE:');
  console.log('');
  
  authData.cookies.forEach((cookie, index) => {
    const expires = cookie.expires > 0 ? new Date(cookie.expires * 1000).toLocaleString() : 'Session';
    const isExpired = cookie.expires > 0 && cookie.expires < (Date.now() / 1000);
    
    console.log(`${index + 1}. ${cookie.name}`);
    console.log(`   Domain: ${cookie.domain}`);
    console.log(`   Path: ${cookie.path}`);
    console.log(`   Value: ${cookie.value.substring(0, 50)}${cookie.value.length > 50 ? '...' : ''}`);
    console.log(`   Expires: ${expires} ${isExpired ? '❌ EXPIRED' : '✅'}`);
    console.log(`   HttpOnly: ${cookie.httpOnly ? '✅' : '❌'}`);
    console.log(`   Secure: ${cookie.secure ? '✅' : '❌'}`);
    console.log(`   SameSite: ${cookie.sameSite || 'None'}`);
    console.log('');
  });
  
  // Analyze localStorage
  console.log('═══════════════════════════════════════════════════════');
  console.log('💾 LOCALSTORAGE IN FILE:');
  console.log('═══════════════════════════════════════════════════════');
  console.log('');
  
  if (authData.origins && authData.origins.length > 0) {
    authData.origins.forEach(origin => {
      console.log(`Origin: ${origin.origin}`);
      console.log('');
      
      if (origin.localStorage && origin.localStorage.length > 0) {
        origin.localStorage.forEach((item, index) => {
          console.log(`${index + 1}. ${item.name}`);
          console.log(`   Value: ${item.value.substring(0, 100)}${item.value.length > 100 ? '...' : ''}`);
          console.log('');
        });
      } else {
        console.log('   (No localStorage items)');
        console.log('');
      }
    });
  } else {
    console.log('⚠️  No origins found in auth file!');
    console.log('');
  }
  
  // Now test in browser
  console.log('═══════════════════════════════════════════════════════');
  console.log('🌐 RUNTIME VERIFICATION (Headless Browser)');
  console.log('═══════════════════════════════════════════════════════');
  console.log('');
  
  const browser = await chromium.launch({ headless: true });
  
  try {
    const context = await browser.newContext({ 
      storageState: authFile 
    });
    
    // Check cookies loaded in context
    const loadedCookies = await context.cookies();
    
    console.log('🍪 COOKIES LOADED IN BROWSER:');
    console.log('');
    console.log(`Total: ${loadedCookies.length}`);
    console.log('');
    
    loadedCookies.forEach((cookie, index) => {
      console.log(`${index + 1}. ${cookie.name} (${cookie.domain})`);
    });
    
    console.log('');
    
    // Compare
    const fileCookieNames = authData.cookies.map(c => c.name).sort();
    const loadedCookieNames = loadedCookies.map(c => c.name).sort();
    
    const missing = fileCookieNames.filter(name => !loadedCookieNames.includes(name));
    const extra = loadedCookieNames.filter(name => !fileCookieNames.includes(name));
    
    if (missing.length > 0) {
      console.log('⚠️  Cookies in file but NOT loaded:');
      missing.forEach(name => console.log(`   - ${name}`));
      console.log('');
    }
    
    if (extra.length > 0) {
      console.log('ℹ️  Extra cookies loaded (not in file):');
      extra.forEach(name => console.log(`   - ${name}`));
      console.log('');
    }
    
    if (missing.length === 0 && extra.length === 0) {
      console.log('✅ All cookies loaded correctly!');
      console.log('');
    }
    
    // Check localStorage in page
    const page = await context.newPage();
    await page.goto('https://preprodapp.tekioncloud.com/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    
    await page.waitForTimeout(2000);
    
    const lsData = await page.evaluate(() => {
      const items = {};
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        items[key] = localStorage.getItem(key);
      }
      return items;
    });
    
    console.log('═══════════════════════════════════════════════════════');
    console.log('💾 LOCALSTORAGE LOADED IN PAGE:');
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
    console.log(`Total: ${Object.keys(lsData).length}`);
    console.log('');
    
    Object.entries(lsData).forEach(([key, value], index) => {
      console.log(`${index + 1}. ${key}`);
      console.log(`   Value: ${value.substring(0, 100)}${value.length > 100 ? '...' : ''}`);
      console.log('');
    });
    
    // Check for specific Tekion tokens
    console.log('═══════════════════════════════════════════════════════');
    console.log('🔑 TEKION-SPECIFIC AUTH ITEMS:');
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
    
    const tekionKeys = ['t_token', 'dse_t_user', 't_user', 'expiryTime'];
    const foundKeys = tekionKeys.filter(key => key in lsData);
    
    if (foundKeys.length > 0) {
      console.log('✅ Found Tekion auth items:');
      foundKeys.forEach(key => {
        console.log(`   - ${key}: ${lsData[key].substring(0, 50)}...`);
      });
    } else {
      console.log('❌ No Tekion auth items found!');
      console.log('   Expected: t_token, dse_t_user, t_user');
      console.log('   This means the session was not captured correctly.');
    }
    
    console.log('');
    
    // Check for Okta cookies
    const oktaCookies = loadedCookies.filter(c => c.domain.includes('okta'));
    
    if (oktaCookies.length > 0) {
      console.log('🔐 Okta cookies found:');
      oktaCookies.forEach(c => {
        console.log(`   - ${c.name} (${c.domain})`);
      });
    } else {
      console.log('⚠️  No Okta cookies found!');
      console.log('   This may cause authentication issues.');
    }
    
    console.log('');
    console.log('═══════════════════════════════════════════════════════');
    console.log('📊 SUMMARY');
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
    console.log(`Cookies in file: ${authData.cookies.length}`);
    console.log(`Cookies loaded: ${loadedCookies.length}`);
    console.log(`localStorage items: ${Object.keys(lsData).length}`);
    console.log(`Tekion auth items: ${foundKeys.length}/${tekionKeys.length}`);
    console.log(`Okta cookies: ${oktaCookies.length}`);
    console.log('');
    
    if (foundKeys.length === tekionKeys.length && oktaCookies.length > 0) {
      console.log('✅ Session looks complete!');
    } else {
      console.log('⚠️  Session may be incomplete. Re-capture with step1-capture-fresh.js');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
})();

