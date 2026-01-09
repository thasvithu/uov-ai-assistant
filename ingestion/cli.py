"""
CLI for document ingestion.

Usage:
    python ingestion/cli.py --input ./data/raw
    python ingestion/cli.py --file ./data/raw/pdf/handbook.pdf
"""

import argparse
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.pipeline import IngestionPipeline
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console = Console()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest documents into Qdrant vector store"
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input',
        '-i',
        type=str,
        help='Directory containing documents to ingest'
    )
    input_group.add_argument(
        '--file',
        '-f',
        type=str,
        help='Single file to ingest'
    )
    
    # Processing options
    parser.add_argument(
        '--extensions',
        '-e',
        nargs='+',
        help='File extensions to process (e.g., .pdf .docx)',
        default=None
    )
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Skip text cleaning'
    )
    parser.add_argument(
        '--recreate',
        action='store_true',
        help='Recreate Qdrant collection (deletes existing data!)'
    )
    
    args = parser.parse_args()
    
    # Display header
    console.print("\n[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]  UoV AI Assistant - Document Ingestion[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════[/bold cyan]\n")
    
    try:
        # Initialize pipeline
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing pipeline...", total=None)
            pipeline = IngestionPipeline()
            progress.update(task, completed=True)
        
        console.print("[green]✓[/green] Pipeline initialized\n")
        
        # Process documents
        if args.input:
            console.print(f"[cyan]Processing directory:[/cyan] {args.input}")
            if args.recreate:
                console.print("[yellow]⚠ Warning: Recreating collection (existing data will be deleted)[/yellow]")
            
            pipeline.process_directory(
                directory=args.input,
                extensions=args.extensions,
                clean_text=not args.no_clean,
                recreate_collection=args.recreate
            )
        
        elif args.file:
            console.print(f"[cyan]Processing file:[/cyan] {args.file}")
            
            pipeline.process_file(
                file_path=args.file,
                clean_text=not args.no_clean
            )
        
        # Display statistics
        console.print("\n[bold green]✓ Ingestion Complete![/bold green]\n")
        
        stats = pipeline.get_stats()
        console.print(f"[cyan]Collection:[/cyan] {stats['collection_name']}")
        console.print(f"[cyan]Total chunks:[/cyan] {stats['total_chunks']}")
        console.print(f"[cyan]Embedding dimension:[/cyan] {stats['embedding_dimension']}\n")
        
        return 0
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}\n")
        logging.exception("Ingestion failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
