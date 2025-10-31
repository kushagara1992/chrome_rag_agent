"""API endpoints."""
import time
from fastapi import APIRouter, HTTPException
from loguru import logger
from smart_search.api.v1.schemas import IndexPageRequest, SearchRequest, SearchResponse, IndexResponse, HealthResponse, StatsResponse
from smart_search.agent.agent import SmartSearchAgent
from smart_search.agent.schemas import AgentRequest
from smart_search.core.config import get_settings

router = APIRouter(prefix="/api/v1", tags=["search"])
agent = SmartSearchAgent()
settings = get_settings()

@router.post("/index", response_model=IndexResponse)
async def index_page(request: IndexPageRequest) -> IndexResponse:
    """Index page."""
    try:
        logger.info(f"Indexing: {request.url}")
        
        agent_req = AgentRequest(
            action="index",
            page_url=request.url,
            page_title=request.title,
            page_content=request.content
        )
        
        response = await agent.execute(agent_req)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        return IndexResponse(
            success=True,
            message=response.message,
            total_pages=response.data.get("total_pages", 0) if response.data else 0
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    """Search."""
    try:
        logger.info(f"Searching: {request.query}")
        
        start_time = time.time()
        
        agent_req = AgentRequest(
            action="search",
            query=request.query,
            top_k=request.top_k
        )
        
        response = await agent.execute(agent_req)
        search_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            success=response.success,
            message=response.message,
            total_results=len(response.results) if response.results else 0,
            results=response.results or [],
            search_time_ms=search_time
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check."""
    try:
        status = agent.get_status()
        
        return HealthResponse(
            status="healthy",
            version=settings.api_version,
            ollama_running=status.get("ollama_health", {}).get("ollama_running", False),
            total_pages_indexed=status.get("total_pages", 0)
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        return HealthResponse(status="error", version=settings.api_version, ollama_running=False, total_pages_indexed=0)

@router.get("/stats", response_model=StatsResponse)
async def get_stats() -> StatsResponse:
    """Stats."""
    try:
        status = agent.get_status()
        stats = agent.executor.vector_store.get_stats()
        
        return StatsResponse(
            total_pages=status.get("total_pages", 0),
            embedding_dimension=status.get("embedding_dimension", 0),
            index_file_size=stats.get("index_file_size", 0)
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/index")
async def clear_index() -> dict:
    """Clear index."""
    try:
        logger.info("Clearing index...")
        agent.executor.vector_store._create_new_index = lambda: setattr(agent.executor.vector_store, 'index', None)
        agent.executor.metadata_store.clear()
        agent.executor.cache.clear()
        
        return {"success": True, "message": "Index cleared"}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
