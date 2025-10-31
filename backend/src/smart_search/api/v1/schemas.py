"""API schemas."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from smart_search.memory.schemas import SearchResult

class IndexPageRequest(BaseModel):
    url: str
    title: str
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=20)

class SearchResponse(BaseModel):
    success: bool
    message: str
    total_results: int
    results: List[SearchResult] = []
    search_time_ms: float

class IndexResponse(BaseModel):
    success: bool
    message: str
    total_pages: int

class HealthResponse(BaseModel):
    status: str
    version: str
    ollama_running: bool
    total_pages_indexed: int

class StatsResponse(BaseModel):
    total_pages: int
    embedding_dimension: int
    index_file_size: int
