"""Highlighting actions."""
from loguru import logger
from smart_search.action.schemas import HighlightAction, ActionType

class Highlighter:
    """Handles highlighting."""
    
    @staticmethod
    def prepare_highlight(action: HighlightAction) -> dict:
        """Prepare highlight."""
        try:
            logger.info(f"Preparing highlight for: {action.url}")
            
            return {
                "success": True,
                "url": action.url,
                "text": action.text_to_highlight,
                "style": "yellow_background"
            }
        except Exception as e:
            logger.error(f"Highlight error: {e}")
            return {"success": False, "error": str(e)}
