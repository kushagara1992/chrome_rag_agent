"""Helper functions."""
from urllib.parse import urlparse
import hashlib

def extract_domain(url: str) -> str:
    """Extract domain."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except:
        return ""

def is_valid_url(url: str) -> bool:
    """Check if URL valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def truncate_text(text: str, length: int = 100) -> str:
    """Truncate text."""
    if len(text) <= length:
        return text
    return text[:length] + "..."

def generate_hash(data: str) -> str:
    """Generate hash."""
    return hashlib.sha256(data.encode()).hexdigest()
