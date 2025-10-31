"""In-memory cache."""
from typing import Dict, Optional, Any
from datetime import datetime
from loguru import logger

class CacheEntry:
    """Cache entry with TTL."""
    
    def __init__(self, value: Any, ttl_seconds: Optional[int] = None):
        self.value = value
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if expired."""
        if self.ttl_seconds is None:
            return False
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds

class MemoryCache:
    """In-memory cache with TTL."""
    
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = 3600) -> None:
        """Set cache entry."""
        self.cache[key] = CacheEntry(value, ttl_seconds)
        logger.debug(f"Cache set: {key}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache entry."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if entry.is_expired():
            del self.cache[key]
            logger.debug(f"Cache expired: {key}")
            return None
        
        logger.debug(f"Cache hit: {key}")
        return entry.value
    
    def delete(self, key: str) -> None:
        """Delete entry."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear all."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> None:
        """Remove expired entries."""
        expired = [k for k, e in self.cache.items() if e.is_expired()]
        for k in expired:
            del self.cache[k]
        if expired:
            logger.debug(f"Cleaned {len(expired)} expired entries")
