"""Search decision logic."""
from loguru import logger

class Searcher:
    """Search decisions."""
    
    @staticmethod
    def validate_query(query: str) -> bool:
        """Validate query."""
        if not query:
            logger.warning("Empty query")
            return False
        
        if len(query) > 500:
            logger.warning("Query too long")
            return False
        
        forbidden = ['<', '>', '{', '}', '|', '&']
        if any(char in query for char in forbidden):
            logger.warning("Forbidden characters")
            return False
        
        return True
    
    @staticmethod
    def make_search_decision(query: str, top_k: int = 5) -> dict:
        """Make search decision."""
        logger.info(f"Search decision for: {query}")
        
        return {
            "query": query,
            "top_k": top_k,
            "min_score_threshold": 0.3,
            "apply_diversity": len(query.split()) > 3
        }
