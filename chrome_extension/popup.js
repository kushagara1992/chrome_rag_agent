// ==========================================
// SMART PAGE SEARCH - POPUP LOGIC
// ==========================================

const API_BASE_URL = 'http://localhost:8000';
let currentQuery = '';

/**
 * Initialize popup
 */
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  const searchBtn = document.getElementById('searchBtn');
  const resultsDiv = document.getElementById('results');
  const statusDiv = document.getElementById('status');
  const loadingDiv = document.getElementById('loading');
  
  searchBtn.addEventListener('click', performSearch);
  searchInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      performSearch();
    }
  });
  
  /**
   * Perform search
   */
  async function performSearch() {
    const query = searchInput.value.trim();
    
    if (!query) {
      showStatus('Please enter a search query', 'warning');
      return;
    }
    
    currentQuery = query;
    showLoading(true);
    showStatus('', '');
    resultsDiv.innerHTML = '';
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, top_k: 5 })
      });
      
      if (response.ok) {
        const result = await response.json();
        displayResults(result);
      } else {
        showStatus('Search failed. Is backend running?', 'error');
      }
    } catch (error) {
      console.error('Search error:', error);
      showStatus('Error: Cannot connect to backend at ' + API_BASE_URL, 'error');
    } finally {
      showLoading(false);
    }
  }
  
  /**
   * Display results
   */
  function displayResults(result) {
    if (!result.success) {
      showStatus(result.message, 'warning');
      return;
    }
    
    if (!result.results || result.results.length === 0) {
      showStatus('No results found', 'info');
      return;
    }
    
    showStatus(`Found ${result.total_results} result(s) in ${result.search_time_ms.toFixed(0)}ms`, 'success');
    
    resultsDiv.innerHTML = '';
    
    result.results.forEach((result, index) => {
      const resultItem = createResultItem(result, index + 1);
      resultsDiv.appendChild(resultItem);
    });
  }
  
  /**
   * Create result item HTML
   */
  function createResultItem(result, index) {
    const item = document.createElement('div');
    item.className = 'result-item';
    
    const scorePercent = (result.score * 100).toFixed(0);
    
    item.innerHTML = `
      <div class="result-header">
        <span class="result-index">${index}</span>
        <h3 class="result-title">${escapeHtml(result.title)}</h3>
      </div>
      <a href="#" class="result-url" data-url="${result.url}">
        ${escapeHtml(result.url)}
      </a>
      <div class="result-meta">
        <span class="result-score">
          <span class="score-bar" style="width: ${scorePercent}%"></span>
          <span class="score-text">${scorePercent}%</span>
        </span>
        <span class="result-date">${formatDate(result.timestamp)}</span>
      </div>
      <p class="result-preview">${escapeHtml(result.content.substring(0, 150))}...</p>
    `;
    
    item.querySelector('.result-url').addEventListener('click', function(e) {
      e.preventDefault();
      // Use the snippet for highlighting if available, else fallback to query
      openAndHighlight(result.url, result.snippet || currentQuery);
    });
    
    return item;
  }
  
  /**
   * Open URL and highlight text
   */
  async function openAndHighlight(url, searchText) {
    chrome.tabs.create({ url: url }, function(tab) {
      chrome.tabs.onUpdated.addListener(function listener(tabId, changeInfo) {
        if (tabId === tab.id && changeInfo.status === 'complete') {
          chrome.tabs.onUpdated.removeListener(listener);
          
          // Wait a moment for content script to be ready
          setTimeout(() => {
            chrome.tabs.sendMessage(tabId, {
              action: 'highlightText',
              text: searchText
            });
          }, 100);
        }
      });
    });
  }
  
  /**
   * Show status message
   */
  function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = `status status-${type}`;
    statusDiv.style.display = message ? 'block' : 'none';
  }
  
  /**
   * Show/hide loading indicator
   */
  function showLoading(show) {
    loadingDiv.style.display = show ? 'flex' : 'none';
  }
});

/**
 * Escape HTML
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Format date
 */
function formatDate(isoDate) {
  try {
    const date = new Date(isoDate);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else if (diffDays < 30) {
      return `${Math.floor(diffDays / 7)} weeks ago`;
    } else {
      return `${Math.floor(diffDays / 30)} months ago`;
    }
  } catch (e) {
    return 'Unknown';
  }
}
