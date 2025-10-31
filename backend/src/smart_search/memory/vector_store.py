"""FAISS vector storage."""
import os
from typing import List, Dict, Optional
import numpy as np
import faiss
from loguru import logger
from smart_search.core.config import get_settings
from smart_search.memory.schemas import StoredPage, SearchResult

class VectorStore:
    """FAISS vector storage."""
    
    def __init__(self, embedding_dimension: int):
        import pickle
        self.settings = get_settings()
        self.embedding_dimension = embedding_dimension
        # Use a new subfolder for all pages
        self.pages_dir = os.path.join(self.settings.data_dir, "pages")
        os.makedirs(self.pages_dir, exist_ok=True)
        self.index_file = os.path.join(self.pages_dir, "faiss_index.bin")
        self.metadata_file = os.path.join(self.pages_dir, "metadata.pkl")
        self.index = faiss.IndexFlatIP(embedding_dimension)
        self.metadata: List[StoredPage] = []
        self.url_to_idx: Dict[str, int] = {}
        self._load_or_create()
        logger.info(f"VectorStore initialized with {len(self.metadata)} pages")
    
    def _load_or_create(self) -> None:
        """Load or create index and metadata."""
        import pickle
        if os.path.exists(self.index_file):
            try:
                self.index = faiss.read_index(self.index_file)
                logger.info(f"Loaded index from {self.index_file}")
            except Exception as e:
                logger.warning(f"Could not load index: {e}")
                self.index = faiss.IndexFlatIP(self.embedding_dimension)
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "rb") as f:
                    self.metadata = pickle.load(f)
                self.url_to_idx = {page.url: i for i, page in enumerate(self.metadata)}
                logger.info(f"Loaded metadata from {self.metadata_file}")
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}")
    
    def add(self, url: str, embedding: np.ndarray, page_data: StoredPage) -> int:
        """Add page."""
        if url in self.url_to_idx:
            logger.info(f"Updating existing URL in index: {url}")
            idx = self.url_to_idx[url]
            self.metadata[idx] = page_data
        else:
            logger.info(f"Adding new URL to index: {url}")
            logger.info(f"Embedding shape: {embedding.shape}, dtype: {embedding.dtype}")
            embedding_2d = embedding.reshape(1, -1)
            self.index.add(embedding_2d)
            self.metadata.append(page_data)
            idx = len(self.metadata) - 1
            self.url_to_idx[url] = idx
            logger.info(f"Added at index {idx}: {url}")
            logger.info(f"Current number of vectors in FAISS index: {self.index.ntotal}")
        return len(self.metadata)
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        """Search pages."""
        if len(self.metadata) == 0:
            return []
        
        top_k = min(top_k, len(self.metadata))
        query_2d = query_embedding.reshape(1, -1)
        distances, indices = self.index.search(query_2d, top_k)
        # Flatten the results to 1D arrays
        distances = distances[0]
        indices = indices[0]
        results = []
        for idx, distance in zip(indices, distances):
            if 0 <= idx < len(self.metadata):
                page = self.metadata[idx]
                score = float(max(0, min(distance, 1.0)))
                results.append(SearchResult(
                    url=page.url, title=page.title,
                    content=page.content, score=score,
                    timestamp=page.timestamp
                ))
        return results
    
    def save(self) -> None:
        """Save index and metadata."""
        import pickle
        try:
            logger.info(f"Saving FAISS index to: {self.index_file}")
            logger.info(f"Number of vectors in index: {self.index.ntotal}")
            faiss.write_index(self.index, self.index_file)
            logger.info(f"Saved index at {self.index_file}")
            with open(self.metadata_file, "wb") as f:
                pickle.dump(self.metadata, f)
            logger.info(f"Saved metadata at {self.metadata_file}")
        except Exception as e:
            logger.error(f"Save error: {e}")
    
    def get_stats(self) -> Dict:
        """Get stats."""
        index_size = os.path.getsize(self.index_file) if os.path.exists(self.index_file) else 0
        return {
            "total_pages": len(self.metadata),
            "embedding_dimension": self.embedding_dimension,
            "index_file_size": index_size,
        }
    
