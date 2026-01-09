"""
Document loaders using LangChain.

LangChain provides 40+ document loaders for various formats.
"""

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredHTMLLoader,
    TextLoader
)
from langchain.schema import Document
from typing import List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DocumentLoaderFactory:
    """Factory for creating appropriate document loaders."""
    
    @staticmethod
    def get_loader(file_path: str):
        """
        Get appropriate loader based on file extension.
        
        Args:
            file_path: Path to document file
            
        Returns:
            LangChain document loader instance
            
        Raises:
            ValueError: If file type is not supported
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.doc': Docx2txtLoader,
            '.html': UnstructuredHTMLLoader,
            '.htm': UnstructuredHTMLLoader,
            '.txt': TextLoader,
        }
        
        loader_class = loaders.get(extension)
        if not loader_class:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {', '.join(loaders.keys())}"
            )
        
        # TextLoader needs encoding specified
        if extension == '.txt':
            return loader_class(str(file_path), encoding='utf-8')
        
        return loader_class(str(file_path))
    
    @staticmethod
    def load_document(file_path: str) -> List[Document]:
        """
        Load a document using appropriate loader.
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of LangChain Document objects
        """
        try:
            loader = DocumentLoaderFactory.get_loader(file_path)
            documents = loader.load()
            
            # Add source file to metadata
            for doc in documents:
                doc.metadata['source_file'] = Path(file_path).name
                doc.metadata['file_path'] = str(file_path)
            
            logger.info(f"Loaded {len(documents)} pages from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise


def load_documents_from_directory(directory: str, extensions: List[str] = None) -> List[Document]:
    """
    Load all documents from a directory.
    
    Args:
        directory: Path to directory containing documents
        extensions: List of file extensions to include (e.g., ['.pdf', '.docx'])
                   If None, loads all supported types
    
    Returns:
        List of all loaded documents
    """
    if extensions is None:
        extensions = ['.pdf', '.docx', '.doc', '.html', '.htm', '.txt']
    
    directory = Path(directory)
    all_documents = []
    
    for ext in extensions:
        for file_path in directory.rglob(f'*{ext}'):
            try:
                documents = DocumentLoaderFactory.load_document(str(file_path))
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                continue
    
    logger.info(f"Loaded {len(all_documents)} total documents from {directory}")
    return all_documents
