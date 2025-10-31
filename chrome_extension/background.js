// ==========================================
// SMART PAGE SEARCH - BACKGROUND.js (DEBUG VERSION)
// ==========================================

const API_BASE_URL = 'http://localhost:8000';
const INDEXING_DEBOUNCE = 500; // Reduced from 2000

// Domains to skip for privacy
const SKIP_DOMAINS = [
  'mail.google.com',
  'web.whatsapp.com',
  'accounts.google.com',
  'accounts.microsoft.com',
  'github.com/login',
  'login.facebook.com',
  'banking',
  'signin',
  'login'
];

const pendingIndexing = new Map();

// ============ HEALTH MONITORING ============

chrome.runtime.onInstalled.addListener(async () => {
  console.log('✓✓✓ Smart Page Search INSTALLED ✓✓✓');
  console.log('Backend URL:', API_BASE_URL);
  await chrome.storage.local.set({ 
    extensionActive: true,
    installTime: new Date().toISOString()
  });
});

chrome.runtime.onStartup.addListener(() => {
  console.log('✓ Extension started');
});

// Health check every minute
chrome.alarms.create('healthCheck', { periodInMinutes: 1 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'healthCheck') {
    console.log('✓ [HEALTH CHECK]', new Date().toISOString());
    
    // Check backend
    fetch(`${API_BASE_URL}/ping`)
      .then(r => r.json())
      .then(data => console.log('✓ Backend responsive:', data))
      .catch(e => console.error('✗ Backend unreachable:', e.message));
  }
});

// ============ URL VALIDATION ============

function shouldIndexUrl(url) {
  if (!url) {
    console.log('⊘ Skipped: no URL');
    return false;
  }
  
  if (url.startsWith('chrome://') || url.startsWith('chrome-extension://')) {
    console.log('⊘ Skipped: system URL');
    return false;
  }
  
  for (const domain of SKIP_DOMAINS) {
    if (url.includes(domain)) {
      console.log(`⊘ Skipped: blocked domain "${domain}"`);
      return false;
    }
  }
  
  console.log('✓ Will index URL:', url.substring(0, 60) + '...');
  return true;
}

// ============ CONTENT EXTRACTION ============

function extractPageContent(tabId) {
  return new Promise((resolve) => {
    console.log(`📄 Extracting content from tab ${tabId}...`);
    
    chrome.scripting.executeScript({
      target: { tabId, allFrames: true },
      func: () => {
        function extractContentWithRetry(retries = 3, delay = 500) {
          return new Promise((resolve) => {
            function tryExtract(attempt) {
              if (document.readyState !== 'complete' && document.readyState !== 'interactive') {
                document.addEventListener('DOMContentLoaded', () => tryExtract(attempt), { once: true });
                return;
              }
              try {
                const frameInfo = window === window.top ? '[TOP FRAME]' : '[IFRAME]';
                const title = document.title || 'Untitled';
                const url = window.location.href;
                // Extract the full visible text content from the page
                const bodyText = document.body ? document.body.innerText || '' : '';
                console.log(`${frameInfo} [ContentScript] bodyText:`, bodyText.substring(0, 200));
                const metaDescription = document.querySelector('meta[name="description"]');
                const description = metaDescription ? metaDescription.getAttribute('content') : '';
                // Do not strip or truncate content, keep it as full as possible
                let content = `${title} ${description} ${bodyText}`;
                content = content.replace(/\s+/g, ' ').trim();
                const originalLength = content.length;
                // No truncation here; backend will handle chunking/limits
                console.log(`${frameInfo} [ContentScript] Content extracted: ${content.length}/${originalLength} chars`);
                if ((!content || content === 'No content found') && attempt < retries) {
                  setTimeout(() => tryExtract(attempt + 1), delay);
                } else {
                  resolve({
                    url,
                    title,
                    content: content || 'No content found',
                    timestamp: new Date().toISOString(),
                    frame: frameInfo
                  });
                }
              } catch (error) {
                console.error('[ContentScript] Extraction error:', error.message);
                resolve(null);
              }
            }
            tryExtract(0);
          });
        }
        return extractContentWithRetry();
      },
      args: []
    }, (results) => {
      if (chrome.runtime.lastError) {
        console.error('✗ Script execution error:', chrome.runtime.lastError.message);
        resolve(null);
        return;
      }
      
      if (results && Array.isArray(results)) {
        // Find the frame with the most content
        let best = null;
        for (const r of results) {
          if (r && r.result && r.result.content && r.result.content !== 'No content found') {
            if (!best || r.result.content.length > best.content.length) {
              best = r.result;
            }
          }
        }
        if (best) {
          console.log('✓ Content extracted from frame:', best.frame, best.content.substring(0, 50) + '...');
          resolve(best);
        } else {
          console.warn('⊘ No content in any frame');
          resolve(null);
        }
      } else {
        console.error('✗ No script results');
        resolve(null);
      }
    });
  });
}

// ============ BACKEND INDEXING ============

async function indexPageToBackend(pageData) {
  try {
    console.log(`📤 Sending to backend: ${pageData.title}`);
    console.log(`   URL: ${pageData.url}`);
    console.log(`   Backend: ${API_BASE_URL}`);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/index`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(pageData),
      mode: 'cors',
      credentials: 'omit'
    });
    
    if (!response.ok) {
      console.error(`✗ Backend error: ${response.status} ${response.statusText}`);
      const text = await response.text();
      console.error('Response:', text.substring(0, 200));
      return;
    }
    
    const result = await response.json();
    console.log('✓ INDEXED:', result.message);
    console.log('  Total pages:', result.total_pages);
    
  } catch (error) {
    console.error('✗ Network error:', error.message);
    console.error('  Check: Is backend running at', API_BASE_URL, '?');
    console.error('  Check: Is Ollama running?');
  }
}

// ============ TAB MONITORING ============

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete') {
    console.log(`\n🔄 Tab ${tabId} loaded: ${tab.url}`);
    
    if (!tab.url) {
      console.log('⊘ No URL for this tab');
      return;
    }
    
    if (!shouldIndexUrl(tab.url)) {
      return;
    }
    
    // Clear previous timeout
    if (pendingIndexing.has(tabId)) {
      console.log('  Cancelling previous indexing request');
      clearTimeout(pendingIndexing.get(tabId));
    }
    
    // Schedule indexing
    console.log(`⏱️  Scheduling indexing in ${INDEXING_DEBOUNCE}ms...`);
    
    const timeoutId = setTimeout(async () => {
      console.log(`\n⚡ INDEXING TAB ${tabId}...`);
      try {
        const pageData = await extractPageContent(tabId);
        
        if (!pageData) {
          console.warn('⊘ Extraction failed');
          pendingIndexing.delete(tabId);
          return;
        }
        
        if (!pageData.content || pageData.content.trim() === '') {
          console.warn('⊘ No content to index');
          pendingIndexing.delete(tabId);
          return;
        }
        
        await indexPageToBackend(pageData);
        
      } catch (error) {
        console.error('✗ INDEXING ERROR:', error.message);
      }
      
      pendingIndexing.delete(tabId);
    }, INDEXING_DEBOUNCE);
    
    pendingIndexing.set(tabId, timeoutId);
  }
});

// ============ MESSAGE HANDLING ============

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('📨 Message received:', request.action);
  
  if (request.action === 'search') {
    performSearch(request.query)
      .then(results => {
        console.log('✓ Search completed, results:', results);
        sendResponse({ success: true, results });
      })
      .catch(error => {
        console.error('✗ Search error:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true;
  }
});

async function performSearch(query) {
  console.log(`🔍 Searching for: "${query}"`);
  
  const response = await fetch(`${API_BASE_URL}/api/v1/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: 5 })
  });
  
  if (!response.ok) {
    throw new Error(`Search failed: ${response.status}`);
  }
  
  return await response.json();
}

console.log('✓✓✓ Background.js loaded successfully ✓✓✓');
