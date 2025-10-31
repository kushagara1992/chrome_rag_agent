"""Embedding generation."""
import numpy as np
from typing import List
from loguru import logger
from smart_search.embeddings.ollama_client import OllamaClient

class EmbeddingGenerator:
    """Generates embeddings."""
    
    def __init__(self):
        self.client = OllamaClient()
        self.embedding_dimension = 0
        self._initialize_dimension()
    
    def _initialize_dimension(self) -> None:
        """Get embedding dimension."""
        try:
            test_embedding = self.client.generate_embedding("test")
            self.embedding_dimension = len(test_embedding)
            logger.info(f"Embedding dimension: {self.embedding_dimension}")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise
    
    def generate(self, text: str) -> np.ndarray:
        """Generate normalized embedding."""
        try:
            embedding = self.client.generate_embedding(text)
            embedding_array = np.array(embedding, dtype=np.float32)
            
            norm = np.linalg.norm(embedding_array)
            if norm > 0:
                embedding_array = embedding_array / norm
            
            return embedding_array
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dimension
