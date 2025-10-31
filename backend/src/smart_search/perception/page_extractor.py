"""Page content extraction."""
import re
from loguru import logger

try:
    from bs4 import BeautifulSoup
    BS_AVAILABLE = True
except ImportError:
    BS_AVAILABLE = False

class PageExtractor:
    """Extracts content from pages."""
    
    REMOVE_TAGS = {'script', 'style', 'meta', 'link', 'noscript', 'iframe', 'embed', 'object'}
    
    @staticmethod
    def extract_from_html(html_content: str, url: str, title: str):
        """Extract text from HTML."""
        try:
            if BS_AVAILABLE:
                soup = BeautifulSoup(html_content, 'html.parser')
                for tag in PageExtractor.REMOVE_TAGS:
                    for element in soup.find_all(tag):
                        element.decompose()
                text = soup.get_text(separator=' ', strip=True)
            else:
                text = re.sub(r'<[^>]+>', ' ', html_content)
            
            from .schemas import PageData
            return PageData(url=url, title=title, content=text)
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            raise
