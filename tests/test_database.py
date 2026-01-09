"""
Test database connection and operations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database import get_db
from shared.models import ChatSession, ChatMessage, Feedback, MessageRole, FeedbackRating
from uuid import uuid4
from rich.console import Console
from rich import print as rprint

console = Console()


def test_database_connection():
    """Test database connection."""
    console.print("\n[bold cyan]Testing Database Connection...[/bold cyan]\n")
    
    try:
        db = get_db()
        is_connected = db.health_check()
        
        if is_connected:
            console.print("[green]✓[/green] Database connected successfully!")
            return True
        else:
            console.print("[red]✗[/red] Database connection failed")
            return False
    except Exception as e:
        console.print(f"[red]✗[/red] Database connection error: {e}")
        return False


def test_crud_operations():
    """Test CRUD operations."""
    console.print("\n[bold cyan]Testing CRUD Operations...[/bold cyan]\n")
    
    try:
        db = get_db()
        
        # Create session
        session = ChatSession(session_id=uuid4())
        created_session = db.create_session(session)
        console.print(f"[green]✓[/green] Created session: {created_session.session_id}")
        
        # Save user message
        user_message = ChatMessage(
            session_id=created_session.session_id,
            role=MessageRole.USER,
            content="Test question"
        )
        saved_user_msg = db.save_message(user_message)
        console.print(f"[green]✓[/green] Saved user message: {saved_user_msg.message_id}")
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=created_session.session_id,
            role=MessageRole.ASSISTANT,
            content="Test answer",
            citations=[]
        )
        saved_assistant_msg = db.save_message(assistant_message)
        console.print(f"[green]✓[/green] Saved assistant message: {saved_assistant_msg.message_id}")
        
        # Get session messages
        messages = db.get_session_messages(created_session.session_id)
        console.print(f"[green]✓[/green] Retrieved {len(messages)} messages")
        
        # Save feedback
        feedback = Feedback(
            session_id=created_session.session_id,
            message_id=saved_assistant_msg.message_id,
            rating=FeedbackRating.UP,
            comment="Test feedback"
        )
        saved_feedback = db.save_feedback(feedback)
        console.print(f"[green]✓[/green] Saved feedback: {saved_feedback.feedback_id}")
        
        # Log request
        db.log_request(
            session_id=created_session.session_id,
            endpoint="/chat",
            latency_ms=150
        )
        console.print(f"[green]✓[/green] Logged request")
        
        console.print("\n[green]All CRUD operations successful![/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗[/red] CRUD operations failed: {e}")
        return False


def main():
    """Run all database tests."""
    console.print("\n[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]  Database Connection Test[/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════════[/bold yellow]\n")
    
    # Test connection
    connection_ok = test_database_connection()
    
    if not connection_ok:
        console.print("\n[bold red]Database connection failed. Please check your .env configuration.[/bold red]\n")
        return 1
    
    # Test CRUD operations
    crud_ok = test_crud_operations()
    
    # Summary
    console.print("\n[bold cyan]Summary:[/bold cyan]")
    if connection_ok and crud_ok:
        console.print("[bold green]✓ All database tests passed![/bold green]\n")
        return 0
    else:
        console.print("[bold red]✗ Some tests failed. Please check the errors above.[/bold red]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
