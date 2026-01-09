"""
Test document ingestion pipeline.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.pipeline import IngestionPipeline
from rich.console import Console

console = Console()


def test_ingestion():
    """Test ingestion with sample data."""
    console.print("\n[bold cyan]Testing Document Ingestion Pipeline[/bold cyan]\n")
    
    try:
        # Initialize pipeline
        console.print("Initializing pipeline...")
        pipeline = IngestionPipeline()
        console.print("[green]✓[/green] Pipeline initialized\n")
        
        # Test with data directory
        data_dir = Path(__file__).parent.parent / "data" / "raw"
        
        if not data_dir.exists():
            console.print(f"[yellow]⚠[/yellow] Data directory not found: {data_dir}")
            console.print("Please add documents to data/raw/ directory")
            return 1
        
        console.print(f"Processing: {data_dir}\n")
        
        # Process documents
        pipeline.process_directory(
            directory=str(data_dir),
            clean_text=True,
            recreate_collection=True  # Fresh start for testing
        )
        
        # Display stats
        stats = pipeline.get_stats()
        console.print(f"\n[bold green]✓ Test Complete![/bold green]")
        console.print(f"Collection: {stats['collection_name']}")
        console.print(f"Total chunks: {stats['total_chunks']}")
        console.print(f"Embedding dimension: {stats['embedding_dimension']}\n")
        
        return 0
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed:[/bold red] {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_ingestion())
