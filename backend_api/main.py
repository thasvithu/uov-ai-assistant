"""
FastAPI backend application for UOV AI Assistant.

Provides REST API endpoints for chat, health checks, and feedback.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import json
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend_api.rag import get_rag_pipeline
from backend_api.retrieval import get_retriever
from shared.database import get_db
from shared.models import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ChatSession,
    FeedbackRequest,
    Feedback,
    HealthResponse,
    MessageRole
)
from shared.config import settings

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting UOV AI Assistant API...")
    
    # Initialize services (warm up models)
    try:
        get_rag_pipeline()
        get_retriever()
        get_db()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down UOV AI Assistant API...")


# Create FastAPI app
app = FastAPI(
    title="UOV AI Assistant API",
    description="RAG-based chatbot for University of Vavuniya Faculty of Technology",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Health Check Endpoint
# ============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with service status
    """
    try:
        # Check database
        db = get_db()
        db_healthy = db.health_check()
        
        # Check Qdrant
        retriever = get_retriever()
        qdrant_healthy = retriever.qdrant_client.health_check()
        
        # Overall status
        status = "healthy" if (db_healthy and qdrant_healthy) else "degraded"
        
        return HealthResponse(
            status=status,
            version="1.0.0",
            qdrant_connected=qdrant_healthy,
            supabase_connected=db_healthy,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            qdrant_connected=False,
            supabase_connected=False,
            timestamp=datetime.utcnow()
        )


# ============================================
# Chat Endpoint (Non-Streaming)
# ============================================

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """
    Chat endpoint for question answering.
    
    Args:
        request: FastAPI request object (required for rate limiting)
        chat_request: ChatRequest with session_id and question
        
    Returns:
        ChatResponse with answer and citations
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"Chat request - Session: {chat_request.session_id}, Question: {chat_request.question[:50]}...")
        
        # Get or create session
        db = get_db()
        session = db.get_session(chat_request.session_id)
        
        if not session:
            # Create new session
            session = ChatSession(session_id=chat_request.session_id)
            db.create_session(session)
            logger.info(f"Created new session: {chat_request.session_id}")
        
        # Save user message
        user_message = ChatMessage(
            session_id=chat_request.session_id,
            role=MessageRole.USER,
            content=chat_request.question
        )
        db.save_message(user_message)
        
        # Generate answer using RAG
        rag = get_rag_pipeline()
        result = rag.generate_answer(chat_request.question)
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=chat_request.session_id,
            role=MessageRole.ASSISTANT,
            content=result['answer'],
            citations=result.get('citations', [])
        )
        db.save_message(assistant_message)
        
        # Log request
        end_time = datetime.utcnow()
        latency = (end_time - start_time).total_seconds()
        
        db.log_request(
            session_id=chat_request.session_id,
            endpoint="/chat",
            latency_ms=int(latency * 1000),
            error=None
        )
        
        logger.info(f"Chat response generated - Latency: {latency:.2f}s, Confidence: {result.get('confidence', 'unknown')}")
        
        # Return response
        return ChatResponse(
            session_id=chat_request.session_id,
            answer=result['answer'],
            citations=result.get('citations', []),
            message_id=assistant_message.message_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Chat Endpoint (Streaming)
# ============================================

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint for real-time responses.
    
    Args:
        request: ChatRequest with session_id and question
        
    Returns:
        StreamingResponse with SSE events
    """
    async def generate() -> AsyncGenerator[str, None]:
        """Generate SSE events."""
        try:
            logger.info(f"Streaming chat request - Session: {request.session_id}")
            
            # Get or create session
            db = get_db()
            session = db.get_session(request.session_id)
            
            if not session:
                session = ChatSession(session_id=request.session_id)
                db.create_session(session)
            
            # Save user message
            user_message = ChatMessage(
                session_id=request.session_id,
                role=MessageRole.USER,
                content=request.question
            )
            db.save_message(user_message)
            
            # Stream answer
            rag = get_rag_pipeline()
            full_answer = ""
            citations = []
            
            for chunk in rag.generate_answer_stream(request.question):
                if chunk['type'] == 'answer_chunk':
                    full_answer += chunk['content']
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk['content']})}\n\n"
                
                elif chunk['type'] == 'citations':
                    citations = chunk['content']
                    yield f"data: {json.dumps({'type': 'citations', 'content': citations})}\n\n"
                
                elif chunk['type'] == 'metadata':
                    yield f"data: {json.dumps({'type': 'metadata', 'content': chunk['content']})}\n\n"
                
                elif chunk['type'] == 'error':
                    yield f"data: {json.dumps({'type': 'error', 'content': chunk['content']})}\n\n"
                    return
            
            # Save assistant message
            assistant_message = ChatMessage(
                session_id=request.session_id,
                role=MessageRole.ASSISTANT,
                content=full_answer,
                citations=citations
            )
            db.save_message(assistant_message)
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'message_id': str(assistant_message.message_id)})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ============================================
# Feedback Endpoint
# ============================================

@app.post("/feedback")
async def submit_feedback(feedback_request: FeedbackRequest):
    """
    Submit feedback for a message.
    
    Args:
        feedback_request: FeedbackRequest with message_id and rating
        
    Returns:
        Success message
    """
    try:
        logger.info(f"Feedback submitted - Message: {feedback_request.message_id}, Rating: {feedback_request.rating}")
        
        # Create feedback
        feedback = Feedback(
            session_id=feedback_request.session_id,
            message_id=feedback_request.message_id,
            rating=feedback_request.rating,
            comment=feedback_request.comment
        )
        
        # Save to database
        db = get_db()
        db.save_feedback(feedback)
        
        return {"status": "success", "message": "Feedback saved"}
        
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Session History Endpoint
# ============================================

@app.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, limit: int = 50):
    """
    Get chat history for a session.
    
    Args:
        session_id: Session UUID
        limit: Maximum number of messages to return
        
    Returns:
        List of messages
    """
    try:
        from uuid import UUID
        session_uuid = UUID(session_id)
        
        db = get_db()
        messages = db.get_session_messages(session_uuid, limit=limit)
        
        return {"messages": [msg.model_dump() for msg in messages]}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Error Handlers
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.backend_host,
        port=settings.backend_port,
        log_level=settings.log_level.lower()
    )
