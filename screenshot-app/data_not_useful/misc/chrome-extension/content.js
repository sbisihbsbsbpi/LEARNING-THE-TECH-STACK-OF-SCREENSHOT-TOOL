// Content script - runs in the context of web pages
// Has access to localStorage and sessionStorage

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getStorage') {
    try {
      // Get all localStorage items
      const localStorageData = {};
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        localStorageData[key] = localStorage.getItem(key);
      }
      
      // Get all sessionStorage items
      const sessionStorageData = {};
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        sessionStorageData[key] = sessionStorage.getItem(key);
      }
      
      sendResponse({
        localStorage: localStorageData,
        sessionStorage: sessionStorageData
      });
    } catch (error) {
      console.error('Error getting storage:', error);
      sendResponse({
        localStorage: {},
        sessionStorage: {},
        error: error.message
      });
    }
  }
  
  return true; // Keep message channel open for async response
});

// Monitor storage changes and notify background script
window.addEventListener('storage', (event) => {
  chrome.runtime.sendMessage({
    action: 'storageChanged',
    key: event.key,
    oldValue: event.oldValue,
    newValue: event.newValue,
    storageArea: event.storageArea === localStorage ? 'localStorage' : 'sessionStorage'
  });
});

// Monitor cookie changes (via MutationObserver on document.cookie)
let lastCookies = document.cookie;
setInterval(() => {
  const currentCookies = document.cookie;
  if (currentCookies !== lastCookies) {
    chrome.runtime.sendMessage({
      action: 'cookiesChanged',
      cookies: currentCookies
    });
    lastCookies = currentCookies;
  }
}, 1000);

console.log('🔐 Auth State Monitor extension loaded');

