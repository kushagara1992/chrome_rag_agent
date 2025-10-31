"""Indexing actions."""
from loguru import logger
from smart_search.action.schemas import IndexAction, ActionType

class Indexer:
    """Handles indexing."""
    
    @staticmethod
    async def index_page(action: IndexAction, embedding, vector_store) -> dict:
        """Index page."""
        try:
            logger.info(f"Indexing: {action.url}")
            
            from ..memory.schemas import StoredPage
            from datetime import datetime
            
            page = StoredPage(
                url=action.url,
                title=action.title,
                content=action.content,
                timestamp=datetime.now(),
                embedding_dimension=len(embedding),
                metadata=action.metadata
            )
            
            count = vector_store.add(action.url, embedding, page)
            
            # if count % 10 == 0:
            vector_store.save()
            
            return {"success": True, "total_pages": count}
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            return {"success": False, "error": str(e)}
