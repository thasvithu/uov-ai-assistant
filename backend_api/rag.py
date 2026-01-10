"""
RAG (Retrieval-Augmented Generation) orchestration using LangChain.

This module integrates retrieval and LLM to generate contextual answers
with proper citations.
"""

from typing import List, Optional, Dict, Any
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from backend_api.retrieval import get_retriever
from shared.models import Citation
from shared.config import settings
import logging
import re

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline for question answering with citations."""
    
    def __init__(self):
        """Initialize RAG pipeline with retriever and LLM."""
        logger.info("Initializing RAG pipeline...")
        
        # Initialize retriever
        self.retriever = get_retriever()
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            model=settings.groq_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            api_key=settings.groq_api_key
        )
        
        # Create prompt template
        self.prompt = self._create_prompt_template()
        
        logger.info(f"RAG pipeline initialized with model: {settings.groq_model}")
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """
        Create prompt template for RAG.
        
        Returns:
            ChatPromptTemplate for RAG
        """
        system_message = """You are an AI assistant for the Faculty of Technological Studies at the University of Vavuniya.

Your role is to answer questions about the faculty using ONLY the information provided in the context below.

IMPORTANT RULES:
1. Answer ONLY based on the provided context
2. If the context doesn't contain enough information, say "I don't have enough information to answer that question based on the available documents."
3. Be concise, clear, and accurate
4. If you're not sure, say so
5. Support multiple languages (English, Tamil, Sinhala) - respond in the same language as the question
6. Do NOT include citation numbers like [1], [2] in your answer - just provide the information naturally

Context:
{context}

Remember: Only use information from the context above. Do not make up information. Provide answers in a natural, conversational way without citation numbers."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{question}")
        ])
        
        return prompt
    
    def _is_identity_question(self, question: str) -> bool:
        """
        Check if user is asking about the chatbot itself.
        
        Args:
            question: User question
            
        Returns:
            True if identity question, False otherwise
        """
        identity_keywords = [
            # Who are you variations
            "who are you", "who r u", "who r you", "who are u",
            "what are you", "what r u", "what r you", "what are u",
            
            # Name questions
            "your name", "what's your name", "whats your name",
            "tell me your name", "what is your name",
            
            # Purpose questions
            "what can you do", "what do you do", "what can u do",
            "what is your purpose", "what's your purpose",
            "what are your capabilities", "what can you help with",
            "how can you help", "what can you help me with",
            
            # Introduction requests
            "introduce yourself", "tell me about yourself",
            "describe yourself", "about you",
            
            # Function questions
            "what is this", "what is this chatbot", "what is this bot",
            "what does this do", "what's this for", "whats this for",
            
            # Multilingual variations (Tamil/Sinhala)
            "நீங்கள் யார்", "ඔබ කවුද",
        ]
        
        question_lower = question.lower().strip()
        
        # Check for exact matches or if keyword is in question
        return any(keyword in question_lower for keyword in identity_keywords)
    
    def _get_identity_response(self) -> str:
        """
        Get predefined response for identity questions.
        
        Returns:
            Helpful introduction message
        """
        return """I'm the UOV AI Assistant for the Faculty of Technological Studies at the University of Vavuniya.

I can help you with information about:

• Faculty programs and courses
• Admission requirements and procedures
• Faculty leadership and staff
• Facilities and resources
• Academic calendar and events
• Department information
• Vision, mission, and objectives

Feel free to ask me any questions about the Faculty of Technological Studies!"""
    
    def generate_answer(
        self,
        question: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate answer for a question using RAG.
        
        Args:
            question: User question
            top_k: Number of chunks to retrieve
            score_threshold: Minimum similarity score
            
        Returns:
            Dictionary with answer, citations, and metadata
        """
        logger.info(f"Generating answer for: '{question[:50]}...'")
        
        # Check if identity question
        if self._is_identity_question(question):
            logger.info("Identity question detected, returning predefined response")
            return {
                'answer': self._get_identity_response(),
                'citations': [],
                'chunks_retrieved': 0,
                'confidence': 'high',
                'is_identity_question': True
            }
        
        try:
            # Retrieve relevant chunks
            chunks, citations = self.retriever.retrieve_with_citations(
                query=question,
                top_k=top_k,
                score_threshold=score_threshold
            )
            
            # Handle empty retrieval
            if not chunks:
                logger.warning("No relevant chunks found")
                return {
                    'answer': "I don't have enough information to answer that question.\n\nFor more details, please visit our website: https://fts.vau.ac.lk/",
                    'citations': [],
                    'chunks_retrieved': 0,
                    'confidence': 'low'
                }
            
            # Format context for LLM
            context = self.retriever.format_context_for_llm(chunks)
            
            # Generate answer using LLM
            logger.debug("Generating answer with LLM...")
            messages = self.prompt.format_messages(
                context=context,
                question=question
            )
            
            response = self.llm.invoke(messages)
            answer = response.content
            
            # Determine confidence based on retrieval scores
            avg_score = sum(c.score for c in chunks) / len(chunks)
            confidence = self._determine_confidence(avg_score, len(chunks))
            
            logger.info(f"Answer generated (confidence: {confidence})")
            
            return {
                'answer': answer,
                'citations': [c.model_dump() for c in citations],
                'chunks_retrieved': len(chunks),
                'confidence': confidence,
                'avg_retrieval_score': round(avg_score, 3)
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def _determine_confidence(self, avg_score: float, num_chunks: int) -> str:
        """
        Determine confidence level based on retrieval metrics.
        
        Args:
            avg_score: Average retrieval score
            num_chunks: Number of chunks retrieved
            
        Returns:
            Confidence level: 'high', 'medium', or 'low'
        """
        if avg_score >= 0.7 and num_chunks >= 3:
            return 'high'
        elif avg_score >= 0.5 and num_chunks >= 2:
            return 'medium'
        else:
            return 'low'
    
    def generate_answer_stream(
        self,
        question: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ):
        """
        Generate answer with streaming (for real-time display).
        
        Args:
            question: User question
            top_k: Number of chunks to retrieve
            score_threshold: Minimum similarity score
            
        Yields:
            Chunks of the answer as they're generated
        """
        logger.info(f"Generating streaming answer for: '{question[:50]}...'")
        
        try:
            # Retrieve relevant chunks
            chunks, citations = self.retriever.retrieve_with_citations(
                query=question,
                top_k=top_k,
                score_threshold=score_threshold
            )
            
            # Handle empty retrieval
            if not chunks:
                yield {
                    'type': 'answer',
                    'content': "I don't have enough information to answer that question based on the available documents."
                }
                yield {
                    'type': 'citations',
                    'content': []
                }
                yield {
                    'type': 'metadata',
                    'content': {
                        'chunks_retrieved': 0,
                        'confidence': 'low'
                    }
                }
                return
            
            # Format context
            context = self.retriever.format_context_for_llm(chunks)
            
            # Generate streaming answer
            messages = self.prompt.format_messages(
                context=context,
                question=question
            )
            
            # Stream answer chunks
            for chunk in self.llm.stream(messages):
                yield {
                    'type': 'answer_chunk',
                    'content': chunk.content
                }
            
            # Send citations
            yield {
                'type': 'citations',
                'content': [c.model_dump() for c in citations]
            }
            
            # Send metadata
            avg_score = sum(c.score for c in chunks) / len(chunks)
            confidence = self._determine_confidence(avg_score, len(chunks))
            
            yield {
                'type': 'metadata',
                'content': {
                    'chunks_retrieved': len(chunks),
                    'confidence': confidence,
                    'avg_retrieval_score': round(avg_score, 3)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            yield {
                'type': 'error',
                'content': str(e)
            }


# Global RAG pipeline instance
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """
    Get the global RAG pipeline instance.
    
    Returns:
        RAGPipeline instance
    """
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
