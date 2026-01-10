"""
Response caching module for RAG pipeline.

Uses TTL (Time-To-Live) cache to store answers for frequent queries.
"""

from typing import Optional, Dict, Any
from cachetools import TTLCache
import hashlib
import logging

logger = logging.getLogger(__name__)

# Cache configuration
# Max 1000 items, expire after 1 hour (3600 seconds)
_response_cache = TTLCache(maxsize=1000, ttl=3600)

def _normalize_query(query: str) -> str:
    """
    Normalize query for cache key generation.
    - Lowercase
    - Strip whitespace
    - Remove common punctuation
    """
    import string
    return query.lower().strip().translate(str.maketrans("", "", string.punctuation))

def get_cached_response(query: str) -> Optional[Dict[str, Any]]:
    """
    Get cached response for a query.
    
    Args:
        query: User question
        
    Returns:
        Cached response dict or None if not found
    """
    key = _normalize_query(query)
    
    if key in _response_cache:
        logger.info(f"Cache hit for query: '{query}'")
        return _response_cache[key]
    
    return None

def cache_response(query: str, response: Dict[str, Any]):
    """
    Cache a response for a query.
    
    Args:
        query: User question
        response: Response dictionary to cache
    """
    # Only cache if successful and has content
    if not response or not response.get('answer'):
        return
        
    # Don't cache error responses or fallbacks if desired (optional policy)
    if response.get('confidence') == 'low' and "don't have enough information" in response.get('answer', ''):
        return

    key = _normalize_query(query)
    _response_cache[key] = response
    logger.debug(f"Cached response for: '{query}'")

def clear_cache():
    """Clear all cached responses."""
    _response_cache.clear()
    logger.info("Cache cleared")
