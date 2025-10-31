"""Ollama API client."""
import requests
from typing import List
from loguru import logger
from smart_search.core.config import get_settings

class OllamaClient:
    """Client for Ollama API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.ollama_base_url
        self.timeout = self.settings.ollama_timeout
        self.model = self.settings.ollama_embedding_model
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding."""
        try:
            logger.debug(f"Generating embedding for text of length {len(text)} {text}")
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                embedding = data.get("embedding", [])
                logger.debug(f"Generated embedding of dimension {len(embedding)}")
                return embedding
            else:
                raise Exception(f"Ollama error: {response.status_code}")
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise
    
    def check_health(self) -> dict:
        """Check Ollama health."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                model_available = any(self.model in name for name in model_names)
                
                return {
                    "ollama_running": True,
                    "model_available": model_available,
                    "available_models": model_names,
                    "current_model": self.model
                }
            else:
                return {
                    "ollama_running": False,
                    "model_available": False,
                    "available_models": [],
                    "current_model": self.model,
                    "error": f"Status {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                "ollama_running": False,
                "model_available": False,
                "available_models": [],
                "current_model": self.model,
                "error": str(e)
            }
