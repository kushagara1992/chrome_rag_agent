"""Agent execution logic."""
import time
from typing import Tuple
from loguru import logger

from smart_search.perception.content_processor import ContentProcessor
from smart_search.embeddings.embedding_generator import EmbeddingGenerator
from smart_search.memory.vector_store import VectorStore
from smart_search.memory.metadata_store import MetadataStore
from smart_search.memory.cache import MemoryCache
from smart_search.decision.searcher import Searcher
from smart_search.decision.ranker import Ranker
from smart_search.memory.schemas import StoredPage

class AgentExecutor:
    """Agent execution."""
    
    def __init__(self):
        logger.info("Initializing AgentExecutor...")
        
        self.embedding_gen = EmbeddingGenerator()
        self.content_processor = ContentProcessor()
        self.vector_store = VectorStore(self.embedding_gen.get_dimension())
        self.metadata_store = MetadataStore()
        self.cache = MemoryCache()
        
        logger.info("AgentExecutor initialized")
    
    async def handle_index_request(self, page_url: str, page_title: str, page_content: str) -> Tuple[bool, str, dict]:
        """Handle indexing with chunking and persistence."""
        import hashlib, pickle, os
        try:
            start_time = time.time()
            logger.info(f"Indexing: {page_url}")
            chunks, proc_time = self.content_processor.process(page_url, page_title, page_content)
            total_embeddings = 0
            chunk_metadata_list = []
            for chunk in chunks:
                try:
                    embedding = self.embedding_gen.generate(chunk.content)
                    page = StoredPage(
                        url=chunk.url,
                        title=chunk.title,
                        content=chunk.content,
                        timestamp=chunk.timestamp,
                        embedding_dimension=self.embedding_gen.get_dimension(),
                        metadata=chunk.metadata
                    )
                    self.vector_store.add(f"{chunk.url}#chunk{chunk.metadata['chunk_index']}", embedding, page)
                    chunk_metadata_list.append({
                        "url": chunk.url,
                        "title": chunk.title,
                        "chunk_index": chunk.metadata['chunk_index'],
                        "content": chunk.content,
                        "timestamp": str(chunk.timestamp),
                        "metadata": chunk.metadata
                    })
                    total_embeddings += 1
                except Exception as e:
                    logger.error(f"Embedding failed for chunk {chunk.metadata.get('chunk_index')}: {e}")
            self.vector_store.save()
            # Save full page content as HTML/text
            html_dir = os.path.join(self.vector_store.pages_dir, "../pages_html")
            os.makedirs(html_dir, exist_ok=True)
            url_hash = hashlib.sha256(page_url.encode()).hexdigest()
            html_path = os.path.join(html_dir, f"{url_hash}.txt")
            # Save the full page content (not truncated)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page_content if isinstance(page_content, str) else str(page_content))
            # Save all chunk metadata as JSON (append, don't overwrite)
            import json
            meta_path = os.path.join(self.vector_store.pages_dir, "chunk_metadata.json")
            existing_metadata = []
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        existing_metadata = json.load(f)
                except Exception:
                    existing_metadata = []
            # Remove any existing entries for this url to avoid duplicates
            url_set = set([chunk["url"] for chunk in chunk_metadata_list])
            filtered_metadata = [m for m in existing_metadata if m["url"] not in url_set]
            filtered_metadata.extend(chunk_metadata_list)
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(filtered_metadata, f, ensure_ascii=False, indent=2, default=str)
            total_time = time.time() - start_time
            return True, f"Indexed: {page_title}", {
                "total_chunks": len(chunks),
                "total_embeddings": total_embeddings,
                "processing_time_ms": proc_time,
                "total_time_ms": total_time * 1000,
                "html_path": html_path,
                "chunk_metadata_path": meta_path
            }
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            return False, f"Error: {str(e)}", {}
    
    async def handle_search_request(self, query: str, top_k: int = 5) -> Tuple[bool, str, dict, list]:
        """Handle search and return chunk-level results."""
        import pickle, os
        try:
            start_time = time.time()
            logger.info(f"Searching: {query}")
            if not Searcher.validate_query(query):
                return False, "Invalid query", {}, []
            query_embedding = self.embedding_gen.generate(query)
            results = self.vector_store.search(query_embedding, top_k)
            if not results:
                return True, "No results found", {"total_results": 0}, []
            # Load chunk metadata for snippet/highlighting (from JSON)
            import json
            meta_path = os.path.join(self.vector_store.pages_dir, "chunk_metadata.json")
            chunk_metadata = []
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    chunk_metadata = json.load(f)
            # Build chunk-level results with snippet
            chunk_results = []
            for res in results:
                # Find the chunk index from the url (format: url#chunkN)
                chunk_index = None
                if "#chunk" in res.url:
                    try:
                        chunk_index = int(res.url.split("#chunk")[-1])
                    except Exception:
                        chunk_index = None
                # Find the matching chunk metadata
                meta = next((m for m in chunk_metadata if m["url"] in res.url and m["chunk_index"] == chunk_index), None)
                snippet = meta["content"][:200] if meta else res.content[:200]
                # Always include 'content' for Pydantic validation
                chunk_results.append({
                    "url": res.url.split("#chunk")[0],
                    "title": res.title,
                    "chunk_index": chunk_index,
                    "score": res.score,
                    "snippet": snippet,
                    "content": meta["content"] if meta and "content" in meta else res.content,
                    "timestamp": str(res.timestamp)
                })
            search_time = time.time() - start_time
            return True, f"Found {len(chunk_results)} results", {
                "total_results": len(chunk_results),
                "search_time_ms": search_time * 1000
            }, chunk_results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return False, f"Error: {str(e)}", {}, []
    
    def get_status(self) -> dict:
        """Get status."""
        from ..embeddings.ollama_client import OllamaClient
        client = OllamaClient()
        health = client.check_health()
        
        return {
            "running": True,
            "total_pages": len(self.vector_store.metadata),
            "embedding_dimension": self.embedding_gen.get_dimension(),
            "ollama_health": health,
            "cache_size": len(self.cache.cache)
        }
