"""
Test retrieval functionality.

Tests query embedding, similarity search, and result formatting.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend_api.retrieval import get_retriever
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


def test_retrieval():
    """Test retrieval with sample queries."""
    console.print("\n[bold cyan]Testing Retrieval Layer[/bold cyan]\n")
    
    # Sample queries
    test_queries = [
        "What is the vision of the faculty?",
        "Who is the dean of the faculty?",
        "What degree programs are offered?",
        "When was the faculty established?",
        "What is BICT program?"
    ]
    
    try:
        # Initialize retriever
        console.print("Initializing retriever...")
        retriever = get_retriever()
        console.print("[green]✓[/green] Retriever initialized\n")
        
        # Test each query
        for query in test_queries:
            console.print(f"\n[bold yellow]Query:[/bold yellow] {query}")
            console.print("─" * 60)
            
            # Retrieve chunks
            chunks, citations = retriever.retrieve_with_citations(
                query=query,
                top_k=5,
                score_threshold=0.3
            )
            
            if not chunks:
                console.print("[red]No results found[/red]\n")
                continue
            
            # Display results table
            table = Table(title=f"Retrieved {len(chunks)} Chunks")
            table.add_column("Rank", style="cyan", width=6)
            table.add_column("Score", style="green", width=8)
            table.add_column("Source", style="yellow", width=30)
            table.add_column("Preview", style="white", width=50)
            
            for i, chunk in enumerate(chunks, 1):
                source = chunk.metadata.get('source_file', 'Unknown')
                page = chunk.metadata.get('page')
                if page:
                    source += f" (p.{page})"
                
                preview = chunk.text[:100] + "..." if len(chunk.text) > 100 else chunk.text
                
                table.add_row(
                    str(i),
                    f"{chunk.score:.3f}",
                    source,
                    preview
                )
            
            console.print(table)
            
            # Display citations
            if citations:
                console.print(f"\n[cyan]Citations:[/cyan]")
                for i, citation in enumerate(citations, 1):
                    cite_str = f"  [{i}] {citation.source}"
                    if citation.page:
                        cite_str += f" (Page {citation.page})"
                    if citation.title:
                        cite_str += f" - {citation.title}"
                    console.print(cite_str)
            
            console.print()
        
        console.print("\n[bold green]✓ All retrieval tests passed![/bold green]\n")
        return 0
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed:[/bold red] {e}\n")
        import traceback
        traceback.print_exc()
        return 1


def test_context_formatting():
    """Test context formatting for LLM."""
    console.print("\n[bold cyan]Testing Context Formatting[/bold cyan]\n")
    
    try:
        retriever = get_retriever()
        
        query = "What is the vision of the faculty?"
        console.print(f"[yellow]Query:[/yellow] {query}\n")
        
        # Retrieve chunks
        chunks = retriever.retrieve(query, top_k=3)
        
        # Format context
        context = retriever.format_context_for_llm(chunks)
        
        console.print("[cyan]Formatted Context for LLM:[/cyan]")
        console.print("─" * 60)
        console.print(context)
        console.print("─" * 60)
        
        console.print(f"\n[green]✓[/green] Context formatted: {len(context)} characters\n")
        return 0
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed:[/bold red] {e}\n")
        return 1


def main():
    """Run all retrieval tests."""
    console.print("\n[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]  Retrieval Layer Tests[/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════════[/bold yellow]\n")
    
    # Test retrieval
    result1 = test_retrieval()
    
    # Test context formatting
    result2 = test_context_formatting()
    
    # Summary
    if result1 == 0 and result2 == 0:
        console.print("[bold green]✓ All tests passed![/bold green]\n")
        return 0
    else:
        console.print("[bold red]✗ Some tests failed[/bold red]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
