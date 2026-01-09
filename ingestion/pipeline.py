"""
Main document ingestion pipeline.

Orchestrates: loading → cleaning → chunking → embedding → upserting to Qdrant
"""

from ingestion.loaders import load_documents_from_directory, DocumentLoaderFactory
from ingestion.cleaner import clean_document_text
from ingestion.chunker import DocumentChunker
from shared.embeddings import get_embedding_model
from shared.qdrant_client import get_qdrant_client
from langchain.schema import Document
from typing import List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Main ingestion pipeline orchestrator."""
    
    def __init__(self):
        """Initialize pipeline components."""
        logger.info("Initializing ingestion pipeline...")
        
        self.chunker = DocumentChunker()
        self.embedding_model = get_embedding_model()
        self.qdrant_client = get_qdrant_client()
        
        logger.info("Pipeline initialized")
    
    def process_directory(
        self,
        directory: str,
        extensions: List[str] = None,
        clean_text: bool = True,
        recreate_collection: bool = False
    ):
        """
        Process all documents in a directory.
        
        Args:
            directory: Path to directory containing documents
            extensions: File extensions to process (default: all supported)
            clean_text: Whether to clean text before chunking
            recreate_collection: Whether to recreate Qdrant collection
        """
        logger.info(f"Processing directory: {directory}")
        
        # Create/verify Qdrant collection
        self.qdrant_client.create_collection(recreate=recreate_collection)
        
        # Load documents
        logger.info("Loading documents...")
        documents = load_documents_from_directory(directory, extensions)
        
        if not documents:
            logger.warning("No documents found!")
            return
        
        # Clean text if requested
        if clean_text:
            logger.info("Cleaning document text...")
            for doc in documents:
                doc.page_content = clean_document_text(doc.page_content)
        
        # Chunk documents
        logger.info("Chunking documents...")
        chunks = self.chunker.chunk_documents(documents)
        
        # Extract texts and metadata
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedding_model.embed_passages(texts)
        
        # Upsert to Qdrant
        logger.info("Upserting to Qdrant...")
        self.qdrant_client.upsert_documents(
            texts=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )
        
        logger.info(f"✅ Ingestion complete! Processed {len(chunks)} chunks from {len(documents)} documents")
    
    def process_file(
        self,
        file_path: str,
        clean_text: bool = True
    ):
        """
        Process a single file.
        
        Args:
            file_path: Path to file
            clean_text: Whether to clean text before chunking
        """
        logger.info(f"Processing file: {file_path}")
        
        # Ensure collection exists
        self.qdrant_client.create_collection(recreate=False)
        
        # Load document
        documents = DocumentLoaderFactory.load_document(file_path)
        
        # Clean text if requested
        if clean_text:
            for doc in documents:
                doc.page_content = clean_document_text(doc.page_content)
        
        # Chunk documents
        chunks = self.chunker.chunk_documents(documents)
        
        # Extract texts and metadata
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedding_model.embed_passages(texts)
        
        # Upsert to Qdrant
        self.qdrant_client.upsert_documents(
            texts=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )
        
        logger.info(f"✅ File processed! {len(chunks)} chunks added to Qdrant")
    
    def get_stats(self):
        """
        Get ingestion statistics.
        
        Returns:
            Dictionary with statistics
        """
        info = self.qdrant_client.get_collection_info()
        return {
            'collection_name': self.qdrant_client.collection_name,
            'total_chunks': info.get('points_count', 0),
            'embedding_dimension': self.embedding_model.get_embedding_dimension()
        }
