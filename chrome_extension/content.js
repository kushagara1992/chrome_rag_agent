// ==========================================
// SMART PAGE SEARCH - CONTENT SCRIPT
// ==========================================

console.log('✓ Smart Page Search content script loaded');

/**
 * Listen for messages from popup/background
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'highlightText') {
    highlightTextOnPage(request.text);
    sendResponse({ success: true });
  }
});

/**
 * Highlight text on page
 */
function highlightTextOnPage(searchText) {
  removeHighlights();
  
  if (!searchText || searchText.trim() === '') {
    return;
  }
  
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null,
    false
  );
  
  const textNodes = [];
  let node;
  
  while (node = walker.nextNode()) {
    textNodes.push(node);
  }
  
  let firstMatch = null;
  
  textNodes.forEach(textNode => {
    const text = textNode.textContent;
    const lowerText = text.toLowerCase();
    const lowerSearch = searchText.toLowerCase();
    
    if (lowerText.includes(lowerSearch)) {
      const parent = textNode.parentNode;
      const parts = text.split(new RegExp(`(${escapeRegExp(searchText)})`, 'gi'));
      const fragment = document.createDocumentFragment();
      
      parts.forEach(part => {
        if (part.toLowerCase() === lowerSearch) {
          const span = document.createElement('span');
          span.className = 'smart-search-highlight';
          span.textContent = part;
          fragment.appendChild(span);
          
          if (!firstMatch) {
            firstMatch = span;
          }
        } else {
          fragment.appendChild(document.createTextNode(part));
        }
      });
      
      parent.replaceChild(fragment, textNode);
    }
  });
  
  if (firstMatch) {
    firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

/**
 * Remove all highlights
 */
function removeHighlights() {
  const highlights = document.querySelectorAll('.smart-search-highlight');
  highlights.forEach(highlight => {
    const parent = highlight.parentNode;
    parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
    parent.normalize();
  });
}

/**
 * Escape regex special characters
 */
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Add styles for highlights
const style = document.createElement('style');
style.textContent = `
  .smart-search-highlight {
    background: linear-gradient(90deg, #ffe9a7 0%, #fffbe6 100%);
    color: #222 !important;
    padding: 2px 6px;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(255, 215, 0, 0.15);
    font-weight: 600;
    transition: background 0.3s;
    border-bottom: 2px solid #ffd700;
  }
`;
document.head.appendChild(style);
