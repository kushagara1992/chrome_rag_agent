"""Memory schemas."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class StoredPage(BaseModel):
    url: str
    title: str
    content: str
    timestamp: datetime
    embedding_dimension: int
    metadata: dict = Field(default_factory=dict)

class SearchResult(BaseModel):
    url: str
    title: str
    content: str
    score: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)

class MemoryStats(BaseModel):
    total_pages: int
    embedding_dimension: int
    index_file_size: int
    cache_size: int
