"""Perception schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class PageData(BaseModel):
    url: str
    title: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)

class ProcessedContent(BaseModel):
    url: str
    title: str
    content: str
    original_length: int
    processed_length: int
    extraction_quality: float
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    timestamp: datetime = Field(default_factory=datetime.now) 
