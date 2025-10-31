"""Decision schemas."""
from typing import List
from enum import Enum
from pydantic import BaseModel, Field
from smart_search.memory.schemas import SearchResult

class RankingStrategy(str, Enum):
    RELEVANCE = "relevance"
    RECENCY = "recency"
    HYBRID = "hybrid"

class RankedResult(BaseModel):
    result: SearchResult
    relevance_score: float
    recency_score: float
    final_score: float
    rank: int
