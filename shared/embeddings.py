"""
Embedding model wrapper for multilingual-e5-base.

IMPORTANT: This model requires specific prefixes:
- Queries: "query: <text>"
- Passages: "passage: <text>"
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
from shared.config import settings
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wrapper for multilingual-e5-base embedding model."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize embedding model.
        
        Args:
            model_name: HuggingFace model name (default from config)
        """
        self.model_name = model_name or settings.embedding_model
        
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
        logger.info(
            f"Model loaded. Embedding dimension: {settings.embedding_dimension}"
        )
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a query with "query:" prefix.
        
        CRITICAL: The E5 model requires "query:" prefix for queries.
        
        Args:
            query: User query text
            
        Returns:
            Embedding vector (768 dimensions)
        """
        # Add required prefix
        prefixed_query = f"query: {query}"
        
        # Generate embedding
        embedding = self.model.encode(
            prefixed_query,
            normalize_embeddings=True
        )
        
        return embedding
    
    def embed_passage(self, passage: str) -> np.ndarray:
        """
        Embed a passage with "passage:" prefix.
        
        CRITICAL: The E5 model requires "passage:" prefix for documents.
        
        Args:
            passage: Document passage text
            
        Returns:
            Embedding vector (768 dimensions)
        """
        # Add required prefix
        prefixed_passage = f"passage: {passage}"
        
        # Generate embedding
        embedding = self.model.encode(
            prefixed_passage,
            normalize_embeddings=True
        )
        
        return embedding
    
    def embed_passages(self, passages: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Embed multiple passages in batches.
        
        Args:
            passages: List of passage texts
            batch_size: Batch size for encoding
            
        Returns:
            Array of embedding vectors
        """
        # Add required prefix to all passages
        prefixed_passages = [f"passage: {p}" for p in passages]
        
        # Generate embeddings in batches
        embeddings = self.model.encode(
            prefixed_passages,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        
        logger.info(f"Generated {len(embeddings)} passage embeddings")
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Get embedding dimension.
        
        Returns:
            Embedding dimension (768 for multilingual-e5-base)
        """
        return self.model.get_sentence_embedding_dimension()


# Global embedding model instance
_embedding_model: EmbeddingModel = None


def get_embedding_model() -> EmbeddingModel:
    """
    Get the global embedding model instance.
    
    Returns:
        EmbeddingModel instance
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model
