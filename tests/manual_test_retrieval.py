"""
Manual test script for retrieval layer.

This script tests the retrieval functionality with real queries against
ingested documents in Qdrant.

Usage:
    python tests/manual_test_retrieval.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend_api.retrieval import get_retriever
from shared.config import settings
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console = Console()


def test_retrieval_basic():
    """Test basic retrieval functionality."""
    console.print("\n[bold cyan]Test 1: Basic Retrieval[/bold cyan]")
    
    retriever = get_retriever()
    
    # Test query
    query = "What programs does the Faculty of Technology offer?"
    
    console.print(f"\n[yellow]Query:[/yellow] {query}")
    
    # Retrieve
    chunks = retriever.retrieve(query, top_k=5)
    
    console.print(f"\n[green]Retrieved {len(chunks)} chunks[/green]\n")
    
    # Display results
    for i, chunk in enumerate(chunks, 1):
        console.print(f"[bold]Chunk {i}[/bold] (Score: {chunk.score:.3f})")
        console.print(f"Source: {chunk.metadata.get('source_file', 'Unknown')}")
        if chunk.metadata.get('page'):
            console.print(f"Page: {chunk.metadata['page']}")
        if chunk.metadata.get('section'):
            console.print(f"Section: {chunk.metadata['section']}")
        console.print(f"Text: {chunk.text[:200]}...")
        console.print()


def test_retrieval_with_citations():
    """Test retrieval with citation extraction."""
    console.print("\n[bold cyan]Test 2: Retrieval with Citations[/bold cyan]")
    
    retriever = get_retriever()
    
    query = "What are the admission requirements?"
    
    console.print(f"\n[yellow]Query:[/yellow] {query}")
    
    # Retrieve with citations
    chunks, citations = retriever.retrieve_with_citations(query, top_k=5)
    
    console.print(f"\n[green]Retrieved {len(chunks)} chunks, {len(citations)} unique citations[/green]\n")
    
    # Display citations
    table = Table(title="Citations")
    table.add_column("Source", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Page", style="yellow")
    table.add_column("Section", style="green")
    table.add_column("Score", style="blue")
    
    for citation in citations:
        table.add_row(
            citation.source,
            citation.title,
            str(citation.page) if citation.page else "N/A",
            citation.section or "N/A",
            f"{citation.score:.3f}" if citation.score else "N/A"
        )
    
    console.print(table)


def test_context_formatting():
    """Test context formatting for LLM."""
    console.print("\n[bold cyan]Test 3: Context Formatting for LLM[/bold cyan]")
    
    retriever = get_retriever()
    
    query = "Tell me about scholarships"
    
    console.print(f"\n[yellow]Query:[/yellow] {query}")
    
    # Retrieve
    chunks = retriever.retrieve(query, top_k=3)
    
    # Format context
    context = retriever.format_context_for_llm(chunks)
    
    console.print(f"\n[green]Formatted Context ({len(context)} characters):[/green]\n")
    console.print(Panel(context, title="LLM Context", border_style="blue"))


def test_empty_results():
    """Test handling of queries with no results."""
    console.print("\n[bold cyan]Test 4: Empty Results Handling[/bold cyan]")
    
    retriever = get_retriever()
    
    query = "xyzabc123nonsensequery"
    
    console.print(f"\n[yellow]Query:[/yellow] {query}")
    
    # Retrieve with high threshold
    chunks = retriever.retrieve(query, top_k=5, score_threshold=0.9)
    
    if len(chunks) == 0:
        console.print("\n[green]✓ Correctly handled empty results[/green]")
    else:
        console.print(f"\n[yellow]Retrieved {len(chunks)} chunks (expected 0)[/yellow]")


def test_different_top_k():
    """Test different top_k values."""
    console.print("\n[bold cyan]Test 5: Different top_k Values[/bold cyan]")
    
    retriever = get_retriever()
    
    query = "What is the university about?"
    
    console.print(f"\n[yellow]Query:[/yellow] {query}")
    
    for k in [1, 3, 5, 10]:
        chunks = retriever.retrieve(query, top_k=k)
        console.print(f"top_k={k}: Retrieved {len(chunks)} chunks")


def test_score_threshold():
    """Test different score thresholds."""
    console.print("\n[bold cyan]Test 6: Different Score Thresholds[/bold cyan]")
    
    retriever = get_retriever()
    
    query = "Faculty programs and courses"
    
    console.print(f"\n[yellow]Query:[/yellow] {query}")
    
    for threshold in [0.3, 0.5, 0.7, 0.9]:
        chunks = retriever.retrieve(query, top_k=10, score_threshold=threshold)
        if chunks:
            avg_score = sum(c.score for c in chunks) / len(chunks)
            console.print(
                f"threshold={threshold}: Retrieved {len(chunks)} chunks "
                f"(avg score: {avg_score:.3f})"
            )
        else:
            console.print(f"threshold={threshold}: No results")


def main():
    """Run all manual tests."""
    console.print(Panel.fit(
        "[bold cyan]Retrieval Layer Manual Tests[/bold cyan]\n"
        f"Collection: {settings.qdrant_collection_name}\n"
        f"Embedding Model: {settings.embedding_model}",
        border_style="cyan"
    ))
    
    try:
        # Run tests
        test_retrieval_basic()
        test_retrieval_with_citations()
        test_context_formatting()
        test_empty_results()
        test_different_top_k()
        test_score_threshold()
        
        console.print("\n[bold green]✓ All manual tests completed![/bold green]\n")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error during testing:[/bold red] {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
