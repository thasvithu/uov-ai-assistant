"""
Tests for the retrieval layer.

Tests query embedding, similarity search, metadata extraction, and result formatting.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend_api.retrieval import RetrieverService, get_retriever
from shared.models import RetrievedChunk, Citation
import numpy as np


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model."""
    with patch('backend_api.retrieval.get_embedding_model') as mock:
        model = Mock()
        model.embed_query.return_value = np.array([0.1] * 768)
        mock.return_value = model
        yield model


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client."""
    with patch('backend_api.retrieval.get_qdrant_client') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_qdrant_results():
    """Sample Qdrant search results."""
    return [
        {
            'id': 'chunk_001',
            'score': 0.92,
            'text': 'The Faculty of Technology offers programs in Engineering and Computer Science.',
            'metadata': {
                'source_file': 'faculty_handbook_2024.pdf',
                'title': 'Faculty Handbook 2024',
                'page': 12,
                'section': 'Programs',
                'chunk_index': 0,
                'total_chunks': 5
            }
        },
        {
            'id': 'chunk_002',
            'score': 0.87,
            'text': 'Admission requirements include A-Level qualifications with minimum grades.',
            'metadata': {
                'source_file': 'admissions_guide.pdf',
                'title': 'Admissions Guide',
                'page': 3,
                'section': 'Requirements',
                'chunk_index': 1,
                'total_chunks': 8
            }
        },
        {
            'id': 'chunk_003',
            'score': 0.85,
            'text': 'The university provides scholarships for outstanding students.',
            'metadata': {
                'source_file': 'faculty_handbook_2024.pdf',
                'title': 'Faculty Handbook 2024',
                'page': 45,
                'section': 'Financial Aid',
                'chunk_index': 2,
                'total_chunks': 5
            }
        }
    ]


class TestRetrieverService:
    """Test RetrieverService class."""
    
    def test_initialization(self, mock_embedding_model, mock_qdrant_client):
        """Test retriever initialization."""
        retriever = RetrieverService()
        
        assert retriever.embedding_model is not None
        assert retriever.qdrant_client is not None
    
    def test_retrieve_with_defaults(
        self,
        mock_embedding_model,
        mock_qdrant_client,
        sample_qdrant_results
    ):
        """Test retrieve with default parameters."""
        mock_qdrant_client.search.return_value = sample_qdrant_results
        
        retriever = RetrieverService()
        chunks = retriever.retrieve("What programs are offered?")
        
        # Verify query was embedded with correct prefix
        mock_embedding_model.embed_query.assert_called_once_with("What programs are offered?")
        
        # Verify Qdrant search was called
        assert mock_qdrant_client.search.called
        
        # Verify results
        assert len(chunks) == 3
        assert all(isinstance(chunk, RetrievedChunk) for chunk in chunks)
        assert chunks[0].chunk_id == 'chunk_001'
        assert chunks[0].score == 0.92
        assert chunks[0].text.startswith('The Faculty of Technology')
    
    def test_retrieve_with_custom_parameters(
        self,
        mock_embedding_model,
        mock_qdrant_client,
        sample_qdrant_results
    ):
        """Test retrieve with custom top_k and threshold."""
        mock_qdrant_client.search.return_value = sample_qdrant_results[:2]
        
        retriever = RetrieverService()
        chunks = retriever.retrieve(
            "What are the admission requirements?",
            top_k=5,
            score_threshold=0.8
        )
        
        # Verify search was called with custom parameters
        call_args = mock_qdrant_client.search.call_args
        assert call_args.kwargs['limit'] == 5
        assert call_args.kwargs['score_threshold'] == 0.8
        
        assert len(chunks) == 2
    
    def test_retrieve_empty_results(
        self,
        mock_embedding_model,
        mock_qdrant_client
    ):
        """Test retrieve with no matching results."""
        mock_qdrant_client.search.return_value = []
        
        retriever = RetrieverService()
        chunks = retriever.retrieve("Completely unrelated query")
        
        assert len(chunks) == 0
        assert isinstance(chunks, list)
    
    def test_format_results(
        self,
        mock_embedding_model,
        mock_qdrant_client,
        sample_qdrant_results
    ):
        """Test result formatting."""
        retriever = RetrieverService()
        chunks = retriever._format_results(sample_qdrant_results)
        
        assert len(chunks) == 3
        
        # Check first chunk
        chunk = chunks[0]
        assert chunk.chunk_id == 'chunk_001'
        assert chunk.score == 0.92
        assert 'Faculty of Technology' in chunk.text
        assert chunk.metadata['source_file'] == 'faculty_handbook_2024.pdf'
        assert chunk.metadata['page'] == 12
    
    def test_extract_citations(
        self,
        mock_embedding_model,
        mock_qdrant_client,
        sample_qdrant_results
    ):
        """Test citation extraction from chunks."""
        retriever = RetrieverService()
        chunks = retriever._format_results(sample_qdrant_results)
        citations = retriever.extract_citations(chunks)
        
        # Should have 2 unique citations (2 from handbook, 1 from admissions)
        # But different pages count as different citations
        assert len(citations) == 3
        assert all(isinstance(citation, Citation) for citation in citations)
        
        # Check citation details
        assert citations[0].source == 'faculty_handbook_2024.pdf'
        assert citations[0].page == 12
        assert citations[0].section == 'Programs'
    
    def test_extract_citations_deduplication(
        self,
        mock_embedding_model,
        mock_qdrant_client
    ):
        """Test that duplicate citations are removed."""
        # Create chunks with duplicate sources
        duplicate_results = [
            {
                'id': 'chunk_001',
                'score': 0.92,
                'text': 'Text 1',
                'metadata': {
                    'source_file': 'handbook.pdf',
                    'title': 'Handbook',
                    'page': 12,
                    'section': 'Section A'
                }
            },
            {
                'id': 'chunk_002',
                'score': 0.90,
                'text': 'Text 2',
                'metadata': {
                    'source_file': 'handbook.pdf',
                    'title': 'Handbook',
                    'page': 12,  # Same page
                    'section': 'Section A'
                }
            }
        ]
        
        retriever = RetrieverService()
        chunks = retriever._format_results(duplicate_results)
        citations = retriever.extract_citations(chunks)
        
        # Should only have 1 citation (duplicates removed)
        assert len(citations) == 1
    
    def test_retrieve_with_citations(
        self,
        mock_embedding_model,
        mock_qdrant_client,
        sample_qdrant_results
    ):
        """Test combined retrieve and citation extraction."""
        mock_qdrant_client.search.return_value = sample_qdrant_results
        
        retriever = RetrieverService()
        chunks, citations = retriever.retrieve_with_citations("Test query")
        
        assert len(chunks) == 3
        assert len(citations) == 3
        assert all(isinstance(chunk, RetrievedChunk) for chunk in chunks)
        assert all(isinstance(citation, Citation) for citation in citations)
    
    def test_format_context_for_llm(
        self,
        mock_embedding_model,
        mock_qdrant_client,
        sample_qdrant_results
    ):
        """Test context formatting for LLM."""
        retriever = RetrieverService()
        chunks = retriever._format_results(sample_qdrant_results)
        context = retriever.format_context_for_llm(chunks)
        
        # Verify context structure
        assert '[1] faculty_handbook_2024.pdf (Page 12) - Programs' in context
        assert '[2] admissions_guide.pdf (Page 3) - Requirements' in context
        assert '[3] faculty_handbook_2024.pdf (Page 45) - Financial Aid' in context
        
        # Verify chunk texts are included
        assert 'Faculty of Technology offers programs' in context
        assert 'Admission requirements include' in context
        assert 'scholarships for outstanding students' in context
    
    def test_format_context_empty_chunks(
        self,
        mock_embedding_model,
        mock_qdrant_client
    ):
        """Test context formatting with empty chunks."""
        retriever = RetrieverService()
        context = retriever.format_context_for_llm([])
        
        assert context == ""
    
    def test_format_context_missing_metadata(
        self,
        mock_embedding_model,
        mock_qdrant_client
    ):
        """Test context formatting with missing metadata."""
        results = [
            {
                'id': 'chunk_001',
                'score': 0.92,
                'text': 'Some text without full metadata',
                'metadata': {
                    'source_file': 'document.pdf'
                    # Missing page and section
                }
            }
        ]
        
        retriever = RetrieverService()
        chunks = retriever._format_results(results)
        context = retriever.format_context_for_llm(chunks)
        
        # Should still format correctly without page/section
        assert '[1] document.pdf' in context
        assert 'Some text without full metadata' in context


class TestGetRetriever:
    """Test global retriever instance."""
    
    def test_get_retriever_singleton(
        self,
        mock_embedding_model,
        mock_qdrant_client
    ):
        """Test that get_retriever returns singleton instance."""
        retriever1 = get_retriever()
        retriever2 = get_retriever()
        
        assert retriever1 is retriever2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
