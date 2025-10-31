"""Content processing."""
import re
import time
from datetime import datetime
from typing import Tuple
from loguru import logger
from smart_search.core.config import get_settings
from smart_search.perception.schemas import ProcessedContent

class ContentProcessor:
    """Processes content."""
    
    def __init__(self):
        self.settings = get_settings()
        # Set chunk size and overlap, fallback to defaults if not present in settings
        self.chunk_size = getattr(self.settings, 'chunk_size', 256)
        self.chunk_overlap = getattr(self.settings, 'chunk_overlap', 40)
    
    def process(self, url: str, title: str, content: str, metadata: dict = None) -> Tuple:
        """Process content and split into overlapping chunks."""
        start_time = time.time()
        original_length = len(content)
        cleaned = self._clean_content(content)
        normalized = self._normalize_whitespace(cleaned)
        chunk_size = self.chunk_size
        overlap = self.chunk_overlap
        chunks = []
        i = 0
        start = 0
        while start < len(normalized):
            end = min(start + chunk_size, len(normalized))
            chunk_text = normalized[start:end]
            quality_score = self._calculate_quality_score(content, chunk_text)
            chunk_metadata = dict(metadata or {})
            chunk_metadata['chunk_index'] = i
            processed = ProcessedContent(
                url=url,
                title=title,
                content=chunk_text,
                original_length=original_length,
                processed_length=len(chunk_text),
                extraction_quality=quality_score,
                metadata=chunk_metadata,
                timestamp=datetime.now()
            )
            chunks.append(processed)
            i += 1
            start += chunk_size - overlap
        processing_time = (time.time() - start_time) * 1000
        return chunks, processing_time
    
    @staticmethod
    def _clean_content(content: str) -> str:
        """Clean content."""
        content = re.sub(r'http\S+|www\S+', '', content)
        content = re.sub(r'\S+@\S+', '', content)
        content = re.sub(r'[!?]{2,}', '!', content)
        content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
        return content
    
    @staticmethod
    def _normalize_whitespace(content: str) -> str:
        """Normalize whitespace."""
        content = re.sub(r'\n{2,}', '\n', content)
        content = re.sub(r' {2,}', ' ', content)
        content = content.replace('\t', ' ')
        return content.strip()
    
    @staticmethod
    def _calculate_quality_score(original: str, processed: str) -> float:
        """Calculate quality score."""
        if not original:
            return 0.0
        retention = len(processed) / len(original)
        score = min(retention, 1.0) * 0.7
        if len(processed.split()) > 10:
            score += 0.15
        if '.' in processed:
            score += 0.15
        return min(score, 1.0)
