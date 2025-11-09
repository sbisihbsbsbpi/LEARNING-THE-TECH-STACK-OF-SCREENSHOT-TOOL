// Popup script for Auth State Monitor extension

let currentTab = null;
let authData = {
  cookies: [],
  localStorage: {},
  sessionStorage: {},
  authItems: []
};

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  await loadCurrentTab();
  await refreshData();
  
  // Set up event listeners
  document.getElementById('refresh').addEventListener('click', refreshData);
  document.getElementById('export-playwright').addEventListener('click', exportPlaywright);
  document.getElementById('export-cookies').addEventListener('click', exportCookies);
  document.getElementById('export-localstorage').addEventListener('click', exportLocalStorage);
  document.getElementById('export-sessionstorage').addEventListener('click', exportSessionStorage);
  document.getElementById('auto-save').addEventListener('click', autoSaveToTool);
});

// Load current tab
async function loadCurrentTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTab = tab;
  
  if (tab) {
    document.getElementById('current-url').textContent = tab.url;
  }
}

// Refresh all data
async function refreshData() {
  if (!currentTab) return;
  
  try {
    // Get cookies
    const url = new URL(currentTab.url);
    authData.cookies = await chrome.cookies.getAll({ url: currentTab.url });
    
    // Get localStorage and sessionStorage from content script
    const response = await chrome.tabs.sendMessage(currentTab.id, { action: 'getStorage' });
    
    if (response) {
      authData.localStorage = response.localStorage || {};
      authData.sessionStorage = response.sessionStorage || {};
    }
    
    // Analyze and display
    analyzeAuthData();
    updateUI();
    
  } catch (error) {
    console.error('Error refreshing data:', error);
    showStatus('Error loading data. Try refreshing the page.', 'error');
  }
}

// Analyze auth data to find tokens
function analyzeAuthData() {
  authData.authItems = [];
  
  // Check cookies for auth-related items
  authData.cookies.forEach(cookie => {
    if (isAuthRelated(cookie.name)) {
      authData.authItems.push({
        name: cookie.name,
        value: cookie.value,
        source: 'Cookie',
        domain: cookie.domain
      });
    }
  });
  
  // Check localStorage for auth-related items
  Object.entries(authData.localStorage).forEach(([key, value]) => {
    if (isAuthRelated(key)) {
      authData.authItems.push({
        name: key,
        value: value,
        source: 'localStorage'
      });
    }
  });
  
  // Check sessionStorage for auth-related items
  Object.entries(authData.sessionStorage).forEach(([key, value]) => {
    if (isAuthRelated(key)) {
      authData.authItems.push({
        name: key,
        value: value,
        source: 'sessionStorage'
      });
    }
  });
}

// Check if a key/name is auth-related
function isAuthRelated(name) {
  const keywords = [
    'token', 'auth', 'session', 'jwt', 'bearer',
    'access', 'refresh', 'sid', 'jsession',
    'user', 'login', 'credential', 'api_key',
    't_token', 'dse_t_user', 't_user'  // Tekion-specific
  ];
  
  const lowerName = name.toLowerCase();
  return keywords.some(keyword => lowerName.includes(keyword));
}

// Update UI with current data
function updateUI() {
  // Update counts
  document.getElementById('cookie-count').textContent = authData.cookies.length;
  document.getElementById('localstorage-count').textContent = Object.keys(authData.localStorage).length;
  document.getElementById('sessionstorage-count').textContent = Object.keys(authData.sessionStorage).length;
  document.getElementById('token-count').textContent = authData.authItems.length;
  
  // Update auth items list
  const authItemsContainer = document.getElementById('auth-items');
  
  if (authData.authItems.length === 0) {
    authItemsContainer.innerHTML = '<p class="placeholder">No auth items detected yet...</p>';
  } else {
    authItemsContainer.innerHTML = authData.authItems.map(item => `
      <div class="auth-item">
        <div class="auth-item-name">${escapeHtml(item.name)}</div>
        <div class="auth-item-value">${truncate(escapeHtml(item.value), 50)}</div>
        <div class="auth-item-source">Source: ${item.source}${item.domain ? ` (${item.domain})` : ''}</div>
      </div>
    `).join('');
  }
}

// Export as Playwright storage state
async function exportPlaywright() {
  try {
    const url = new URL(currentTab.url);
    
    // Build Playwright storage state format
    const storageState = {
      cookies: authData.cookies.map(cookie => ({
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain,
        path: cookie.path,
        expires: cookie.expirationDate || -1,
        httpOnly: cookie.httpOnly,
        secure: cookie.secure,
        sameSite: cookie.sameSite || 'Lax'
      })),
      origins: [
        {
          origin: url.origin,
          localStorage: Object.entries(authData.localStorage).map(([name, value]) => ({
            name,
            value
          }))
        }
      ]
    };
    
    // Download as JSON file
    downloadJSON(storageState, 'auth_state.json');
    showStatus('✅ Playwright storage state exported!', 'success');
    
  } catch (error) {
    console.error('Export error:', error);
    showStatus('❌ Export failed', 'error');
  }
}

// Export cookies only
async function exportCookies() {
  try {
    const cookiesData = authData.cookies.map(cookie => ({
      name: cookie.name,
      value: cookie.value,
      domain: cookie.domain,
      path: cookie.path,
      expires: cookie.expirationDate,
      httpOnly: cookie.httpOnly,
      secure: cookie.secure,
      sameSite: cookie.sameSite
    }));
    
    downloadJSON(cookiesData, 'cookies.json');
    showStatus('✅ Cookies exported!', 'success');
    
  } catch (error) {
    console.error('Export error:', error);
    showStatus('❌ Export failed', 'error');
  }
}

// Export localStorage only
async function exportLocalStorage() {
  try {
    downloadJSON(authData.localStorage, 'localStorage.json');
    showStatus('✅ localStorage exported!', 'success');
    
  } catch (error) {
    console.error('Export error:', error);
    showStatus('❌ Export failed', 'error');
  }
}

// Export sessionStorage only
async function exportSessionStorage() {
  try {
    downloadJSON(authData.sessionStorage, 'sessionStorage.json');
    showStatus('✅ sessionStorage exported!', 'success');
    
  } catch (error) {
    console.error('Export error:', error);
    showStatus('❌ Export failed', 'error');
  }
}

// Auto-save to screenshot tool backend
async function autoSaveToTool() {
  try {
    const url = new URL(currentTab.url);
    
    // Build Playwright storage state format
    const storageState = {
      cookies: authData.cookies.map(cookie => ({
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain,
        path: cookie.path,
        expires: cookie.expirationDate || -1,
        httpOnly: cookie.httpOnly,
        secure: cookie.secure,
        sameSite: cookie.sameSite || 'Lax'
      })),
      origins: [
        {
          origin: url.origin,
          localStorage: Object.entries(authData.localStorage).map(([name, value]) => ({
            name,
            value
          }))
        }
      ]
    };
    
    // Send to backend API
    const response = await fetch('http://127.0.0.1:8000/api/auth/save-from-extension', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(storageState)
    });
    
    if (response.ok) {
      showStatus('✅ Auto-saved to screenshot tool!', 'success');
    } else {
      throw new Error('Backend returned error');
    }
    
  } catch (error) {
    console.error('Auto-save error:', error);
    showStatus('❌ Auto-save failed. Is the backend running?', 'error');
  }
}

// Helper: Download JSON file
function downloadJSON(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  
  chrome.downloads.download({
    url: url,
    filename: filename,
    saveAs: true
  });
}

// Helper: Show status message
function showStatus(message, type = 'success') {
  const statusEl = document.getElementById('status-message');
  statusEl.textContent = message;
  statusEl.className = `status-message ${type}`;
  
  setTimeout(() => {
    statusEl.classList.add('hidden');
  }, 3000);
}

// Helper: Escape HTML
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Helper: Truncate text
function truncate(text, maxLength) {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

