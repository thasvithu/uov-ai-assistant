"""
Test configuration script to validate environment setup.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config import get_settings
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


def test_configuration():
    """Test configuration loading."""
    console.print("\n[bold cyan]Testing Configuration Loading...[/bold cyan]\n")
    
    try:
        settings = get_settings()
        console.print("[green]✓[/green] Configuration loaded successfully!")
        
        # Display configuration
        table = Table(title="Configuration Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        # Supabase
        table.add_row("Supabase URL", settings.supabase_url)
        table.add_row("Supabase Key", f"{settings.supabase_key[:20]}..." if len(settings.supabase_key) > 20 else settings.supabase_key)
        
        # Qdrant
        table.add_row("Qdrant URL", settings.qdrant_url)
        table.add_row("Qdrant Collection", settings.qdrant_collection_name)
        
        # Groq
        table.add_row("Groq Model", settings.groq_model)
        
        # Embedding
        table.add_row("Embedding Model", settings.embedding_model)
        table.add_row("Embedding Dimension", str(settings.embedding_dimension))
        
        # Chunking
        table.add_row("Chunk Size", str(settings.chunk_size))
        table.add_row("Chunk Overlap", str(settings.chunk_overlap))
        
        # Retrieval
        table.add_row("Top-K Retrieval", str(settings.top_k_retrieval))
        table.add_row("Similarity Threshold", str(settings.similarity_threshold))
        
        # LLM
        table.add_row("LLM Temperature", str(settings.llm_temperature))
        table.add_row("LLM Max Tokens", str(settings.llm_max_tokens))
        
        console.print(table)
        return True
        
    except Exception as e:
        console.print(f"[red]✗[/red] Configuration loading failed: {e}")
        return False


def test_imports():
    """Test critical imports."""
    console.print("\n[bold cyan]Testing Critical Imports...[/bold cyan]\n")
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("streamlit", "Streamlit"),
        ("langchain", "LangChain"),
        ("sentence_transformers", "Sentence Transformers"),
        ("qdrant_client", "Qdrant Client"),
        ("supabase", "Supabase"),
        ("groq", "Groq"),
    ]
    
    results = []
    for module, name in imports_to_test:
        try:
            __import__(module)
            console.print(f"[green]✓[/green] {name}")
            results.append(True)
        except ImportError:
            console.print(f"[red]✗[/red] {name} - Not installed")
            results.append(False)
    
    return all(results)


def main():
    """Run all tests."""
    console.print("\n[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]  UoV AI Assistant - Environment Test[/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════════[/bold yellow]\n")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test configuration
    config_ok = test_configuration()
    
    # Summary
    console.print("\n[bold cyan]Summary:[/bold cyan]")
    if imports_ok and config_ok:
        console.print("[bold green]✓ All tests passed! Environment is ready.[/bold green]\n")
        return 0
    else:
        console.print("[bold red]✗ Some tests failed. Please check the errors above.[/bold red]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
