"""Embedding schemas."""
from typing import List
from pydantic import BaseModel, Field

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    dimension: int
    model: str
