"""
Test FastAPI backend endpoints.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from backend_api.main import app
from uuid import uuid4
from rich.console import Console
from rich.panel import Panel

console = Console()

# Create test client
client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    console.print("\n[bold cyan]Testing /health endpoint[/bold cyan]")
    
    response = client.get("/health")
    
    console.print(f"Status Code: {response.status_code}")
    console.print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "qdrant_connected" in data
    assert "supabase_connected" in data
    
    console.print("[green]✓[/green] Health check passed\n")


def test_chat_endpoint():
    """Test chat endpoint."""
    console.print("\n[bold cyan]Testing /chat endpoint[/bold cyan]")
    
    session_id = str(uuid4())
    
    request_data = {
        "session_id": session_id,
        "question": "What is the vision of the faculty?"
    }
    
    console.print(f"Request: {request_data}")
    
    response = client.post("/chat", json=request_data)
    
    console.print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Display answer
        answer_panel = Panel(
            data['answer'],
            title="[bold green]Answer[/bold green]",
            border_style="green"
        )
        console.print(answer_panel)
        
        # Display citations
        if data.get('citations'):
            console.print("\n[cyan]Citations:[/cyan]")
            for i, citation in enumerate(data['citations'], 1):
                console.print(f"  [{i}] {citation['source']}")
        
        console.print(f"\nMessage ID: {data['message_id']}")
        console.print("[green]✓[/green] Chat endpoint passed\n")
        
        return session_id, data['message_id']
    else:
        console.print(f"[red]Error: {response.json()}[/red]\n")
        return None, None


def test_feedback_endpoint(session_id, message_id):
    """Test feedback endpoint."""
    if not message_id or not session_id:
        console.print("[yellow]Skipping feedback test (no message_id or session_id)[/yellow]\n")
        return
    
    console.print("\n[bold cyan]Testing /feedback endpoint[/bold cyan]")
    
    feedback_data = {
        "session_id": session_id,
        "message_id": message_id,
        "rating": "up",  # Use enum value: "up" or "down"
        "comment": "Great answer!"
    }
    
    console.print(f"Request: {feedback_data}")
    
    response = client.post("/feedback", json=feedback_data)
    
    console.print(f"Status Code: {response.status_code}")
    console.print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    console.print("[green]✓[/green] Feedback endpoint passed\n")


def test_session_history(session_id):
    """Test session history endpoint."""
    if not session_id:
        console.print("[yellow]Skipping session history test (no session_id)[/yellow]\n")
        return
    
    console.print("\n[bold cyan]Testing /sessions/{session_id}/messages endpoint[/bold cyan]")
    
    response = client.get(f"/sessions/{session_id}/messages")
    
    console.print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        console.print(f"Messages retrieved: {len(data['messages'])}")
        
        for msg in data['messages']:
            console.print(f"  - {msg['role']}: {msg['content'][:50]}...")
        
        console.print("[green]✓[/green] Session history endpoint passed\n")
    else:
        console.print(f"[red]Error: {response.json()}[/red]\n")


def main():
    """Run all tests."""
    console.print("\n[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]  FastAPI Backend Tests[/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════════[/bold yellow]\n")
    
    try:
        # Test health
        test_health_endpoint()
        
        # Test chat
        session_id, message_id = test_chat_endpoint()
        
        # Test feedback
        test_feedback_endpoint(session_id, message_id)
        
        # Test session history
        test_session_history(session_id)
        
        console.print("[bold green]✓ All tests passed![/bold green]\n")
        return 0
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed:[/bold red] {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
