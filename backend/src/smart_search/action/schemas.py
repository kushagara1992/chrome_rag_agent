"""Action schemas."""
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    INDEX = "index"
    SEARCH = "search"
    HIGHLIGHT = "highlight"

class IndexAction(BaseModel):
    url: str
    title: str
    content: str
    metadata: dict = Field(default_factory=dict)

class HighlightAction(BaseModel):
    url: str
    text_to_highlight: str
