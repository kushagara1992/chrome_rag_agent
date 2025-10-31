import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    # API Configuration
    api_title: str = "Smart Page Search API"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_timeout: int = 30
    
    # Storage Configuration
    data_dir: str = "./data"
    index_file: str = "faiss_index.bin"
    metadata_file: str = "metadata.pkl"
    cache_dir: str = "./cache"
    
    # Search Configuration
    default_top_k: int = 5
    max_top_k: int = 20
    max_content_length: int = 500000
    # Chunking parameters
    chunk_size: int = 512
    chunk_overlap: int = 40
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Ensure data directories exist
settings = get_settings()
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(settings.cache_dir, exist_ok=True)
