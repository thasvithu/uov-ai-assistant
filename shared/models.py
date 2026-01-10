"""
Pydantic models for data validation and serialization.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class MessageRole(str, Enum):
    """Chat message role."""
    USER = "user"
    ASSISTANT = "assistant"


class FeedbackRating(str, Enum):
    """Feedback rating."""
    UP = "up"
    DOWN = "down"


class Citation(BaseModel):
    """Citation metadata for a source document."""
    
    source: str = Field(..., description="Source file name")
    title: str = Field(..., description="Document title")
    page: Optional[int] = Field(None, description="Page number (for PDFs)")
    section: Optional[str] = Field(None, description="Section name")
    score: Optional[float] = Field(None, description="Similarity score", ge=0.0, le=1.0)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source": "faculty_handbook_2024.pdf",
                "title": "Faculty Handbook 2024",
                "page": 12,
                "section": "Admissions",
                "score": 0.87
            }
        }
    )


class RetrievedChunk(BaseModel):
    """Retrieved document chunk with metadata."""
    
    chunk_id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Chunk text content")
    score: float = Field(..., description="Similarity score", ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    
    def to_citation(self) -> Citation:
        """Convert to Citation object."""
        return Citation(
            source=self.metadata.get("source_file", "Unknown"),
            title=self.metadata.get("title", "Unknown"),
            page=self.metadata.get("page"),
            section=self.metadata.get("section"),
            score=self.score
        )


class ChatMessage(BaseModel):
    """Chat message model."""
    
    message_id: UUID = Field(default_factory=uuid4, description="Unique message ID")
    session_id: UUID = Field(..., description="Session ID")
    role: MessageRole = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    citations: Optional[List[Citation]] = Field(None, description="Source citations")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message_id": "123e4567-e89b-12d3-a456-426614174000",
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "role": "assistant",
                "content": "The Faculty of Technology offers programs in Engineering...",
                "citations": [
                    {
                        "source": "faculty_handbook_2024.pdf",
                        "title": "Faculty Handbook 2024",
                        "page": 12,
                        "section": "Programs",
                        "score": 0.87
                    }
                ],
                "created_at": "2024-01-09T10:00:00Z"
            }
        }
    )


class ChatSession(BaseModel):
    """Chat session model."""
    
    session_id: UUID = Field(default_factory=uuid4, description="Unique session ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "created_at": "2024-01-09T10:00:00Z"
            }
        }
    )


class Feedback(BaseModel):
    """User feedback model."""
    
    feedback_id: UUID = Field(default_factory=uuid4, description="Unique feedback ID")
    session_id: UUID = Field(..., description="Session ID")
    message_id: UUID = Field(..., description="Message ID")
    rating: FeedbackRating = Field(..., description="Feedback rating (up/down)")
    comment: Optional[str] = Field(None, description="Optional comment")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "feedback_id": "123e4567-e89b-12d3-a456-426614174002",
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "message_id": "123e4567-e89b-12d3-a456-426614174000",
                "rating": "up",
                "comment": "Very helpful!",
                "created_at": "2024-01-09T10:05:00Z"
            }
        }
    )


class ChatRequest(BaseModel):
    """Chat request model."""
    
    session_id: Optional[UUID] = Field(None, description="Session ID (auto-generated if not provided)")
    question: str = Field(..., description="User question", min_length=1, max_length=1000)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "question": "What are the admission requirements for the Faculty of Technology?"
            }
        }
    )


class ChatResponse(BaseModel):
    """Chat response model."""
    
    session_id: UUID = Field(..., description="Session ID")
    message_id: UUID = Field(..., description="Message ID")
    answer: str = Field(..., description="Assistant answer")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "message_id": "123e4567-e89b-12d3-a456-426614174000",
                "answer": "The Faculty of Technology requires...",
                "citations": [
                    {
                        "source": "faculty_handbook_2024.pdf",
                        "title": "Faculty Handbook 2024",
                        "page": 12,
                        "section": "Admissions",
                        "score": 0.87
                    }
                ]
            }
        }
    )


class FeedbackRequest(BaseModel):
    """Feedback request model."""
    
    session_id: UUID = Field(..., description="Session ID")
    message_id: UUID = Field(..., description="Message ID")
    rating: FeedbackRating = Field(..., description="Feedback rating")
    comment: Optional[str] = Field(None, description="Optional comment", max_length=500)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "message_id": "123e4567-e89b-12d3-a456-426614174000",
                "rating": "up",
                "comment": "Very helpful!"
            }
        }
    )


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    qdrant_connected: bool = Field(..., description="Qdrant connection status")
    supabase_connected: bool = Field(..., description="Supabase connection status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "qdrant_connected": True,
                "supabase_connected": True,
                "timestamp": "2024-01-09T10:00:00Z"
            }
        }
    )
