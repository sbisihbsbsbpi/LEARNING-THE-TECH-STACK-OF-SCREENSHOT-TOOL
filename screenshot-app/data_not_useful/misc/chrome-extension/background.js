// Background service worker
// Handles background tasks and message passing

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'storageChanged') {
    console.log('Storage changed:', request);
    // Could notify popup or store in chrome.storage if needed
  }
  
  if (request.action === 'cookiesChanged') {
    console.log('Cookies changed');
    // Could notify popup or store in chrome.storage if needed
  }
  
  return true;
});

// Listen for extension icon click
chrome.action.onClicked.addListener((tab) => {
  // Open popup (default behavior)
});

// Optional: Badge to show number of auth items
async function updateBadge(tabId) {
  try {
    const url = (await chrome.tabs.get(tabId)).url;
    const cookies = await chrome.cookies.getAll({ url });
    
    // Count auth-related cookies
    const authCookies = cookies.filter(cookie => {
      const name = cookie.name.toLowerCase();
      return name.includes('token') || 
             name.includes('auth') || 
             name.includes('session') ||
             name.includes('jwt');
    });
    
    if (authCookies.length > 0) {
      chrome.action.setBadgeText({ 
        text: authCookies.length.toString(),
        tabId 
      });
      chrome.action.setBadgeBackgroundColor({ 
        color: '#667eea',
        tabId 
      });
    } else {
      chrome.action.setBadgeText({ text: '', tabId });
    }
  } catch (error) {
    console.error('Error updating badge:', error);
  }
}

// Update badge when tab is updated
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete') {
    updateBadge(tabId);
  }
});

// Update badge when tab is activated
chrome.tabs.onActivated.addListener((activeInfo) => {
  updateBadge(activeInfo.tabId);
});

console.log('🔐 Auth State Monitor background service worker loaded');

