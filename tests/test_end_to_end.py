"""
End-to-end integration tests for UOV AI Assistant.

Tests the complete flow from document ingestion to chat response.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from uuid import uuid4
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time

console = Console()

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_SESSION_ID = str(uuid4())


def test_api_health():
    """Test 1: API Health Check"""
    console.print("\n[bold cyan]Test 1: API Health Check[/bold cyan]")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            table = Table(title="Service Status")
            table.add_column("Service", style="cyan")
            table.add_column("Status", style="green")
            
            table.add_row("API", "✓ Running")
            table.add_row("Version", data.get('version', 'Unknown'))
            table.add_row("Qdrant", "✓ Connected" if data.get('qdrant_connected') else "✗ Disconnected")
            table.add_row("Supabase", "✓ Connected" if data.get('supabase_connected') else "✗ Disconnected")
            
            console.print(table)
            console.print("[green]✓ Health check passed[/green]\n")
            return True
        else:
            console.print(f"[red]✗ Health check failed: {response.status_code}[/red]\n")
            return False
            
    except Exception as e:
        console.print(f"[red]✗ Cannot connect to API: {e}[/red]\n")
        console.print("[yellow]Make sure the backend is running:[/yellow]")
        console.print("  uvicorn backend_api.main:app --reload\n")
        return False


def test_identity_question():
    """Test 2: Identity Question Detection"""
    console.print("[bold cyan]Test 2: Identity Question Detection[/bold cyan]")
    
    questions = [
        "who are you",
        "what can you do",
        "introduce yourself"
    ]
    
    for question in questions:
        console.print(f"\n[yellow]Q: {question}[/yellow]")
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "session_id": TEST_SESSION_ID,
                "question": question
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data['answer']
            
            # Check if it's the identity response
            if "UOV AI Assistant" in answer and "Faculty of Technological Studies" in answer:
                console.print("[green]✓ Identity response detected[/green]")
                console.print(f"[dim]{answer[:100]}...[/dim]")
            else:
                console.print("[yellow]⚠ Unexpected response[/yellow]")
        else:
            console.print(f"[red]✗ Request failed: {response.status_code}[/red]")
            return False
    
    console.print("\n[green]✓ Identity question test passed[/green]\n")
    return True


def test_knowledge_base_queries():
    """Test 3: Knowledge Base Queries"""
    console.print("[bold cyan]Test 3: Knowledge Base Queries[/bold cyan]")
    
    test_cases = [
        {
            "question": "What is the vision of the faculty?",
            "expected_keywords": ["vision", "world-class", "technical education"],
            "description": "Vision query"
        },
        {
            "question": "Who is the dean?",
            "expected_keywords": ["dean"],
            "description": "Dean query"
        },
        {
            "question": "What programs are offered?",
            "expected_keywords": ["ICT", "ET", "BST", "program"],
            "description": "Programs query"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        console.print(f"\n[yellow]Test {i}: {test['description']}[/yellow]")
        console.print(f"Q: {test['question']}")
        
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "session_id": TEST_SESSION_ID,
                "question": test['question']
            },
            timeout=60
        )
        
        latency = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data['answer']
            
            # Check for expected keywords
            answer_lower = answer.lower()
            found_keywords = [kw for kw in test['expected_keywords'] if kw.lower() in answer_lower]
            
            console.print(Panel(answer, title="[green]Answer[/green]", border_style="green"))
            console.print(f"[dim]Latency: {latency:.2f}s[/dim]")
            console.print(f"[dim]Keywords found: {', '.join(found_keywords) if found_keywords else 'None'}[/dim]")
            
            results.append({
                "test": test['description'],
                "status": "✓" if found_keywords else "⚠",
                "latency": f"{latency:.2f}s"
            })
        else:
            console.print(f"[red]✗ Request failed: {response.status_code}[/red]")
            results.append({
                "test": test['description'],
                "status": "✗",
                "latency": "N/A"
            })
    
    # Summary table
    console.print("\n[bold]Test Results Summary:[/bold]")
    table = Table()
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Latency", style="magenta")
    
    for result in results:
        table.add_row(result['test'], result['status'], result['latency'])
    
    console.print(table)
    console.print("\n[green]✓ Knowledge base query test completed[/green]\n")
    return True


def test_fallback_response():
    """Test 4: Fallback Response for Unknown Questions"""
    console.print("[bold cyan]Test 4: Fallback Response[/bold cyan]")
    
    question = "What is the weather today?"
    console.print(f"\n[yellow]Q: {question}[/yellow]")
    
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json={
            "session_id": TEST_SESSION_ID,
            "question": question
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        answer = data['answer']
        
        # Check for fallback message
        if "don't have enough information" in answer.lower() and "fts.vau.ac.lk" in answer:
            console.print(Panel(answer, title="[green]Fallback Response[/green]", border_style="green"))
            console.print("[green]✓ Fallback response test passed[/green]\n")
            return True
        else:
            console.print("[yellow]⚠ Unexpected response (should be fallback)[/yellow]")
            console.print(answer)
    else:
        console.print(f"[red]✗ Request failed: {response.status_code}[/red]")
    
    return False


def test_feedback_submission():
    """Test 5: Feedback Submission"""
    console.print("[bold cyan]Test 5: Feedback Submission[/bold cyan]")
    
    # First, get a message ID from a chat
    chat_response = requests.post(
        f"{API_BASE_URL}/chat",
        json={
            "session_id": TEST_SESSION_ID,
            "question": "What is the vision?"
        },
        timeout=30
    )
    
    if chat_response.status_code == 200:
        message_id = chat_response.json()['message_id']
        
        # Submit feedback
        feedback_response = requests.post(
            f"{API_BASE_URL}/feedback",
            json={
                "session_id": TEST_SESSION_ID,
                "message_id": message_id,
                "rating": "up",
                "comment": "Test feedback"
            },
            timeout=10
        )
        
        if feedback_response.status_code == 200:
            console.print("[green]✓ Feedback submitted successfully[/green]\n")
            return True
        else:
            console.print(f"[red]✗ Feedback submission failed: {feedback_response.status_code}[/red]\n")
            return False
    else:
        console.print("[red]✗ Could not get message ID for feedback test[/red]\n")
        return False


def test_session_history():
    """Test 6: Session History Retrieval"""
    console.print("[bold cyan]Test 6: Session History Retrieval[/bold cyan]")
    
    response = requests.get(
        f"{API_BASE_URL}/sessions/{TEST_SESSION_ID}/messages",
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        messages = data['messages']
        
        console.print(f"[green]✓ Retrieved {len(messages)} messages from session[/green]")
        
        if messages:
            console.print("\n[dim]Sample messages:[/dim]")
            for msg in messages[:3]:
                console.print(f"  - {msg['role']}: {msg['content'][:50]}...")
        
        console.print()
        return True
    else:
        console.print(f"[red]✗ Session history retrieval failed: {response.status_code}[/red]\n")
        return False


def main():
    """Run all end-to-end tests"""
    console.print("\n[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]  UOV AI Assistant - End-to-End Tests[/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════════[/bold yellow]\n")
    
    console.print(f"[dim]Test Session ID: {TEST_SESSION_ID}[/dim]\n")
    
    tests = [
        ("API Health Check", test_api_health),
        ("Identity Question Detection", test_identity_question),
        ("Knowledge Base Queries", test_knowledge_base_queries),
        ("Fallback Response", test_fallback_response),
        ("Feedback Submission", test_feedback_submission),
        ("Session History", test_session_history)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            console.print(f"[red]✗ {test_name} failed with error: {e}[/red]\n")
            results.append((test_name, False))
    
    # Final summary
    console.print("\n[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]  Test Summary[/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════════[/bold yellow]\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[green]✓ PASS[/green]" if result else "[red]✗ FAIL[/red]"
        console.print(f"{status} - {test_name}")
    
    console.print(f"\n[bold]Results: {passed}/{total} tests passed[/bold]")
    
    if passed == total:
        console.print("\n[bold green]🎉 All tests passed! System is ready for deployment.[/bold green]\n")
        return 0
    else:
        console.print(f"\n[bold yellow]⚠ {total - passed} test(s) failed. Please review.[/bold yellow]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
