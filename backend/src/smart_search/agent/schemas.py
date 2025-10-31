"""Agent schemas."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from smart_search.memory.schemas import SearchResult

class AgentRequest(BaseModel):
    action: str
    query: Optional[str] = None
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    page_content: Optional[str] = None
    top_k: int = Field(5, ge=1, le=20)

class AgentResponse(BaseModel):
    success: bool
    action: str
    message: str
    data: Optional[dict] = None
    results: Optional[List[SearchResult]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
