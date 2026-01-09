"""
Database connection and operations for Supabase.
"""

from supabase import create_client, Client
from shared.config import settings
from shared.models import ChatSession, ChatMessage, Feedback
from typing import Optional, List
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class DatabaseClient:
    """Supabase database client wrapper."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    # ============================================
    # Chat Sessions
    # ============================================
    
    def create_session(self, session: ChatSession) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            session: ChatSession object
            
        Returns:
            Created ChatSession
        """
        try:
            result = self.client.table('chat_sessions').insert(
                session.model_dump(mode='json')
            ).execute()
            
            logger.info(f"Created session: {session.session_id}")
            return ChatSession(**result.data[0])
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    def get_session(self, session_id: UUID) -> Optional[ChatSession]:
        """
        Get a chat session by ID.
        
        Args:
            session_id: Session UUID
            
        Returns:
            ChatSession or None if not found
        """
        try:
            result = self.client.table('chat_sessions').select('*').eq(
                'session_id', str(session_id)
            ).execute()
            
            if result.data:
                return ChatSession(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            raise
    
    # ============================================
    # Chat Messages
    # ============================================
    
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Save a chat message.
        
        Args:
            message: ChatMessage object
            
        Returns:
            Saved ChatMessage
        """
        try:
            result = self.client.table('chat_messages').insert(
                message.model_dump(mode='json')
            ).execute()
            
            logger.info(f"Saved message: {message.message_id}")
            return ChatMessage(**result.data[0])
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise
    
    def get_session_messages(
        self, 
        session_id: UUID,
        limit: int = 50
    ) -> List[ChatMessage]:
        """
        Get all messages for a session.
        
        Args:
            session_id: Session UUID
            limit: Maximum number of messages to return
            
        Returns:
            List of ChatMessage objects
        """
        try:
            result = self.client.table('chat_messages').select('*').eq(
                'session_id', str(session_id)
            ).order('created_at', desc=False).limit(limit).execute()
            
            return [ChatMessage(**msg) for msg in result.data]
        except Exception as e:
            logger.error(f"Error getting session messages: {e}")
            raise
    
    # ============================================
    # Feedback
    # ============================================
    
    def save_feedback(self, feedback: Feedback) -> Feedback:
        """
        Save user feedback.
        
        Args:
            feedback: Feedback object
            
        Returns:
            Saved Feedback
        """
        try:
            result = self.client.table('feedback').insert(
                feedback.model_dump(mode='json')
            ).execute()
            
            logger.info(f"Saved feedback: {feedback.feedback_id}")
            return Feedback(**result.data[0])
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            raise
    
    # ============================================
    # Request Logs
    # ============================================
    
    def log_request(
        self,
        session_id: Optional[UUID],
        endpoint: str,
        latency_ms: int,
        error: Optional[str] = None
    ):
        """
        Log an API request.
        
        Args:
            session_id: Session UUID (optional)
            endpoint: API endpoint
            latency_ms: Request latency in milliseconds
            error: Error message if request failed
        """
        try:
            self.client.table('request_logs').insert({
                'session_id': str(session_id) if session_id else None,
                'endpoint': endpoint,
                'latency_ms': latency_ms,
                'error': error
            }).execute()
            
            logger.debug(f"Logged request to {endpoint}: {latency_ms}ms")
        except Exception as e:
            logger.error(f"Error logging request: {e}")
            # Don't raise - logging failures shouldn't break the app
    
    # ============================================
    # Health Check
    # ============================================
    
    def health_check(self) -> bool:
        """
        Check database connectivity.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            # Simple query to test connection
            self.client.table('chat_sessions').select('session_id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database client instance
_db_client: Optional[DatabaseClient] = None


def get_db() -> DatabaseClient:
    """
    Get the global database client instance.
    
    Returns:
        DatabaseClient instance
    """
    global _db_client
    if _db_client is None:
        _db_client = DatabaseClient()
    return _db_client
