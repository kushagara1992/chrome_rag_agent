"""Main agent."""
from loguru import logger
from smart_search.agent.executor import AgentExecutor
from smart_search.agent.schemas import AgentRequest, AgentResponse

class SmartSearchAgent:
    """Main agent - Singleton."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing SmartSearchAgent...")
        self.executor = AgentExecutor()
        self._initialized = True
    
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute request."""
        logger.info(f"Executing: {request.action}")
        
        try:
            if request.action == "index":
                return await self._handle_index(request)
            elif request.action == "search":
                return await self._handle_search(request)
            else:
                return AgentResponse(success=False, action=request.action, message="Unknown action")
        except Exception as e:
            logger.error(f"Error: {e}")
            return AgentResponse(success=False, action=request.action, message=str(e))
    
    async def _handle_index(self, request: AgentRequest) -> AgentResponse:
        """Handle indexing."""
        if not all([request.page_url, request.page_title, request.page_content]):
            return AgentResponse(success=False, action="index", message="Missing fields")
        
        success, message, data = await self.executor.handle_index_request(
            request.page_url, request.page_title, request.page_content
        )
        
        return AgentResponse(success=success, action="index", message=message, data=data)
    
    async def _handle_search(self, request: AgentRequest) -> AgentResponse:
        """Handle search."""
        if not request.query:
            return AgentResponse(success=False, action="search", message="Missing query")
        
        success, message, data, results = await self.executor.handle_search_request(
            request.query, request.top_k
        )
        
        return AgentResponse(success=success, action="search", message=message, data=data, results=results)
    
    def get_status(self) -> dict:
        """Get status."""
        return self.executor.get_status()
