"""
Qdrant vector store client and operations.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from shared.config import settings
from typing import List, Dict, Any, Optional
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Qdrant vector store client wrapper."""
    
    def __init__(self):
        """Initialize Qdrant client."""
        logger.info(f"Connecting to Qdrant: {settings.qdrant_url}")
        
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        
        self.collection_name = settings.qdrant_collection_name
        
        logger.info(f"Qdrant client initialized for collection: {self.collection_name}")
    
    def create_collection(self, recreate: bool = False):
        """
        Create Qdrant collection if it doesn't exist.
        
        Args:
            recreate: If True, delete and recreate collection
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if collection_exists and recreate:
                logger.warning(f"Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
                collection_exists = False
            
            if not collection_exists:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection created: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def upsert_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Upsert documents to Qdrant.
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
        """
        if not (len(texts) == len(embeddings) == len(metadatas)):
            raise ValueError("texts, embeddings, and metadatas must have same length")
        
        points = []
        for text, embedding, metadata in zip(texts, embeddings, metadatas):
            point_id = str(uuid4())
            
            # Add text to metadata
            metadata['text'] = text
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=metadata
                )
            )
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            logger.info(f"Upserted batch {i//batch_size + 1}: {len(batch)} points")
        
        logger.info(f"Total upserted: {len(points)} documents")
    
    def search(
        self,
        query_vector: List[float],
        limit: int = None,
        score_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_vector: Query embedding vector
            limit: Number of results to return (default from config)
            score_threshold: Minimum similarity score (default from config)
            
        Returns:
            List of search results with scores and metadata
        """
        limit = limit or settings.top_k_retrieval
        score_threshold = score_threshold or settings.similarity_threshold
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'id': result.id,
                'score': result.score,
                'text': result.payload.get('text', ''),
                'metadata': {k: v for k, v in result.payload.items() if k != 'text'}
            })
        
        logger.info(f"Found {len(formatted_results)} results")
        
        return formatted_results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get collection information.
        
        Returns:
            Collection info dictionary
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': info.config.params.vectors.size,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}
    
    def health_check(self) -> bool:
        """
        Check Qdrant connectivity.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False


# Global Qdrant client instance
_qdrant_client: Optional[QdrantVectorStore] = None


def get_qdrant_client() -> QdrantVectorStore:
    """
    Get the global Qdrant client instance.
    
    Returns:
        QdrantVectorStore instance
    """
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantVectorStore()
    return _qdrant_client
