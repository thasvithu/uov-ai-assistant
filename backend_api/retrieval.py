"""
Retrieval service for semantic search over document chunks.

This module orchestrates query embedding and similarity search using Qdrant,
returning formatted results with metadata and citations.
"""

from typing import List, Optional
from shared.embeddings import get_embedding_model
from shared.qdrant_client import get_qdrant_client
from shared.models import RetrievedChunk, Citation
from shared.config import settings
import logging

logger = logging.getLogger(__name__)


class RetrieverService:
    """Service for retrieving relevant document chunks based on queries."""
    
    def __init__(self):
        """Initialize retriever with embedding model and vector store."""
        logger.info("Initializing retriever service...")
        
        self.embedding_model = get_embedding_model()
        self.qdrant_client = get_qdrant_client()
        
        logger.info("Retriever service initialized")
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant document chunks for a query.
        
        Args:
            query: User query text
            top_k: Number of chunks to retrieve (default from config)
            score_threshold: Minimum similarity score (default from config)
            
        Returns:
            List of RetrievedChunk objects with metadata
        """
        logger.info(f"Retrieving documents for query: '{query[:50]}...'")
        
        # Use defaults from config if not provided
        top_k = top_k or settings.top_k_retrieval
        score_threshold = score_threshold or settings.similarity_threshold
        
        # Embed query with "query:" prefix (CRITICAL for E5 model)
        logger.debug("Embedding query with 'query:' prefix...")
        query_embedding = self.embedding_model.embed_query(query)
        
        # Search Qdrant
        logger.debug(f"Searching Qdrant (top_k={top_k}, threshold={score_threshold})...")
        raw_results = self.qdrant_client.search(
            query_vector=query_embedding.tolist(),
            limit=top_k,
            score_threshold=score_threshold
        )
        
        # Format results
        chunks = self._format_results(raw_results)
        
        logger.info(f"Retrieved {len(chunks)} relevant chunks")
        
        return chunks
    
    def _format_results(self, raw_results: List[dict]) -> List[RetrievedChunk]:
        """
        Format raw Qdrant results into RetrievedChunk objects.
        
        Args:
            raw_results: Raw search results from Qdrant
            
        Returns:
            List of RetrievedChunk objects
        """
        chunks = []
        
        for result in raw_results:
            chunk = RetrievedChunk(
                chunk_id=result['id'],
                text=result['text'],
                score=result['score'],
                metadata=result['metadata']
            )
            chunks.append(chunk)
        
        return chunks
    
    def extract_citations(self, chunks: List[RetrievedChunk]) -> List[Citation]:
        """
        Extract unique citations from retrieved chunks.
        
        Args:
            chunks: List of retrieved chunks
            
        Returns:
            List of unique Citation objects
        """
        citations = []
        seen_sources = set()
        
        for chunk in chunks:
            # Convert chunk to citation
            citation = chunk.to_citation()
            
            # Create unique key for deduplication
            source_key = (
                citation.source,
                citation.page if citation.page else -1
            )
            
            # Add if not seen before
            if source_key not in seen_sources:
                citations.append(citation)
                seen_sources.add(source_key)
        
        logger.debug(f"Extracted {len(citations)} unique citations from {len(chunks)} chunks")
        
        return citations
    
    def retrieve_with_citations(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> tuple[List[RetrievedChunk], List[Citation]]:
        """
        Retrieve chunks and extract citations in one call.
        
        Args:
            query: User query text
            top_k: Number of chunks to retrieve
            score_threshold: Minimum similarity score
            
        Returns:
            Tuple of (chunks, citations)
        """
        chunks = self.retrieve(query, top_k, score_threshold)
        citations = self.extract_citations(chunks)
        
        return chunks, citations
    
    def format_context_for_llm(self, chunks: List[RetrievedChunk]) -> str:
        """
        Format retrieved chunks into context string for LLM.
        
        Args:
            chunks: List of retrieved chunks
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            # Build source label
            source_label = f"[{i}] {chunk.metadata.get('source_file', 'Unknown')}"
            
            if chunk.metadata.get('page'):
                source_label += f" (Page {chunk.metadata['page']})"
            
            if chunk.metadata.get('section'):
                source_label += f" - {chunk.metadata['section']}"
            
            # Add chunk text
            context_parts.append(f"{source_label}\n{chunk.text}\n")
        
        context = "\n".join(context_parts)
        
        logger.debug(f"Formatted context: {len(context)} characters from {len(chunks)} chunks")
        
        return context


# Global retriever instance
_retriever: Optional[RetrieverService] = None


def get_retriever() -> RetrieverService:
    """
    Get the global retriever service instance.
    
    Returns:
        RetrieverService instance
    """
    global _retriever
    if _retriever is None:
        _retriever = RetrieverService()
    return _retriever
