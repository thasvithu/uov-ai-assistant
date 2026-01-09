"""
Text chunking using LangChain's RecursiveCharacterTextSplitter.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from transformers import AutoTokenizer
from typing import List
from shared.config import settings
import hashlib
import logging

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Document chunker using LangChain and tokenizer-aware splitting."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        model_name: str = None
    ):
        """
        Initialize chunker with tokenizer-aware splitting.
        
        Args:
            chunk_size: Maximum tokens per chunk (default from config)
            chunk_overlap: Overlap between chunks in tokens (default from config)
            model_name: HuggingFace model name for tokenizer (default from config)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.model_name = model_name or settings.embedding_model
        
        # Load tokenizer
        logger.info(f"Loading tokenizer: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Create LangChain text splitter
        self.text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=self.tokenizer,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
        logger.info(
            f"Chunker initialized: chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap}"
        )
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Chunk documents into smaller pieces.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            List of chunked Document objects with metadata
        """
        chunked_docs = []
        
        for doc in documents:
            # Split document into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Add chunk metadata
            for i, chunk in enumerate(chunks):
                # Generate unique chunk ID
                chunk_id = hashlib.md5(
                    f"{doc.metadata.get('source_file', 'unknown')}_{i}".encode()
                ).hexdigest()
                
                # Count actual tokens
                token_count = len(self.tokenizer.encode(chunk.page_content))
                
                # Update metadata
                chunk.metadata.update({
                    'chunk_id': chunk_id,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'token_count': token_count,
                    'doc_id': doc.metadata.get('doc_id', chunk_id[:8])
                })
                
                chunked_docs.append(chunk)
        
        logger.info(
            f"Chunked {len(documents)} documents into {len(chunked_docs)} chunks"
        )
        
        return chunked_docs
    
    def chunk_text(self, text: str, metadata: dict = None) -> List[Document]:
        """
        Chunk raw text into documents.
        
        Args:
            text: Raw text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunked Document objects
        """
        # Create a document from text
        doc = Document(
            page_content=text,
            metadata=metadata or {}
        )
        
        return self.chunk_documents([doc])
