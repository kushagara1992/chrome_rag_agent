"""Metadata storage."""
import os
import pickle
from typing import List
from loguru import logger
from smart_search.core.config import get_settings
from smart_search.memory.schemas import StoredPage

class MetadataStore:
    """Persists metadata."""
    
    def __init__(self):
        self.settings = get_settings()
        self.metadata_file = os.path.join(self.settings.data_dir, self.settings.metadata_file)
        self.metadata: List[StoredPage] = []
        self._load()
    
    def _load(self) -> None:
        """Load metadata."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded {len(self.metadata)} pages")
            except Exception as e:
                logger.error(f"Load error: {e}")
    
    def save(self) -> None:
        """Save metadata."""
        try:
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            logger.debug(f"Saved {len(self.metadata)} pages")
        except Exception as e:
            logger.error(f"Save error: {e}")
    
    def add(self, page: StoredPage) -> None:
        """Add page."""
        self.metadata.append(page)
    
    def clear(self) -> None:
        """Clear metadata."""
        self.metadata = []
        self.save()
