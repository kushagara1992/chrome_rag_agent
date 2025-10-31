"""Exceptions."""

class SmartSearchException(Exception):
    """Base exception."""
    pass

class OllamaException(SmartSearchException):
    """Ollama error."""
    pass

class IndexingException(SmartSearchException):
    """Indexing error."""
    pass

class SearchException(SmartSearchException):
    """Search error."""
    pass

class ValidationException(SmartSearchException):
    """Validation error."""
    pass
