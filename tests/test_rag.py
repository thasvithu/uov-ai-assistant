"""
Test RAG pipeline functionality.

Tests question answering with retrieval and LLM generation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend_api.rag import get_rag_pipeline
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint

console = Console()


def test_rag_pipeline():
    """Test RAG pipeline with sample questions."""
    console.print("\n[bold cyan]Testing RAG Pipeline[/bold cyan]\n")
    
    # Sample questions
    test_questions = [
        "What is the vision of the Faculty of Technological Studies?",
        "Who is the dean of the faculty?",
        "What degree programs are offered by the faculty?",
        "When was the faculty established?",
        "What is the BICT program about?"
    ]
    
    try:
        # Initialize RAG pipeline
        console.print("Initializing RAG pipeline...")
        rag = get_rag_pipeline()
        console.print("[green]✓[/green] RAG pipeline initialized\n")
        
        # Test each question
        for i, question in enumerate(test_questions, 1):
            console.print(f"\n[bold yellow]Question {i}:[/bold yellow] {question}")
            console.print("─" * 80)
            
            # Generate answer
            result = rag.generate_answer(question)
            
            # Display answer
            answer_panel = Panel(
                result['answer'],
                title="[bold green]Answer[/bold green]",
                border_style="green"
            )
            console.print(answer_panel)
            
            # Display metadata
            console.print(f"\n[cyan]Metadata:[/cyan]")
            console.print(f"  • Chunks retrieved: {result['chunks_retrieved']}")
            console.print(f"  • Confidence: {result['confidence']}")
            if 'avg_retrieval_score' in result:
                console.print(f"  • Avg retrieval score: {result['avg_retrieval_score']}")
            
            # Display citations
            if result['citations']:
                console.print(f"\n[cyan]Citations:[/cyan]")
                for j, citation in enumerate(result['citations'], 1):
                    cite_str = f"  [{j}] {citation['source']}"
                    if citation.get('page'):
                        cite_str += f" (Page {citation['page']})"
                    if citation.get('title'):
                        cite_str += f" - {citation['title']}"
                    console.print(cite_str)
            
            console.print()
        
        console.print("\n[bold green]✓ All RAG tests passed![/bold green]\n")
        return 0
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed:[/bold red] {e}\n")
        import traceback
        traceback.print_exc()
        return 1


def test_streaming():
    """Test streaming answer generation."""
    console.print("\n[bold cyan]Testing Streaming Generation[/bold cyan]\n")
    
    try:
        rag = get_rag_pipeline()
        
        question = "What is the vision of the faculty?"
        console.print(f"[yellow]Question:[/yellow] {question}\n")
        console.print("[cyan]Streaming answer:[/cyan]")
        console.print("─" * 80)
        
        answer_chunks = []
        citations = []
        metadata = {}
        
        # Stream answer
        for chunk in rag.generate_answer_stream(question):
            if chunk['type'] == 'answer_chunk':
                console.print(chunk['content'], end='')
                answer_chunks.append(chunk['content'])
            elif chunk['type'] == 'citations':
                citations = chunk['content']
            elif chunk['type'] == 'metadata':
                metadata = chunk['content']
            elif chunk['type'] == 'error':
                console.print(f"\n[red]Error: {chunk['content']}[/red]")
                return 1
        
        console.print("\n" + "─" * 80)
        
        # Display metadata
        if metadata:
            console.print(f"\n[cyan]Metadata:[/cyan]")
            console.print(f"  • Chunks retrieved: {metadata.get('chunks_retrieved', 0)}")
            console.print(f"  • Confidence: {metadata.get('confidence', 'unknown')}")
        
        # Display citations
        if citations:
            console.print(f"\n[cyan]Citations:[/cyan]")
            for i, citation in enumerate(citations, 1):
                cite_str = f"  [{i}] {citation['source']}"
                if citation.get('page'):
                    cite_str += f" (Page {citation['page']})"
                console.print(cite_str)
        
        console.print("\n[green]✓[/green] Streaming test passed\n")
        return 0
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed:[/bold red] {e}\n")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Run all RAG tests."""
    console.print("\n[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]  RAG Pipeline Tests[/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════════[/bold yellow]\n")
    
    # Test regular generation
    result1 = test_rag_pipeline()
    
    # Test streaming
    result2 = test_streaming()
    
    # Summary
    if result1 == 0 and result2 == 0:
        console.print("[bold green]✓ All tests passed![/bold green]\n")
        return 0
    else:
        console.print("[bold red]✗ Some tests failed[/bold red]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
