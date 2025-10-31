"""FastAPI main."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

from smart_search.core.config import get_settings
from smart_search.core.logging_config import setup_logging
from smart_search.api.v1 import endpoints, health
from smart_search.utils.exceptions import SmartSearchException

setup_logging()
settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Smart Page Search Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(SmartSearchException)
async def exception_handler(request: Request, exc: SmartSearchException):
    """Exception handler."""
    logger.error(f"Exception: {exc}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.on_event("startup")
async def startup():
    """Startup."""
    logger.info(f"🚀 API starting at {settings.api_host}:{settings.api_port}")

app.include_router(health.router)
app.include_router(endpoints.router)

def run_server():
    """Run server."""
    uvicorn.run("smart_search.main:app", host=settings.api_host, port=settings.api_port, reload=settings.debug)

if __name__ == "__main__":
    run_server()
