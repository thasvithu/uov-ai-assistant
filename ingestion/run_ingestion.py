"""
Automated incremental ingestion runner.

Scans data folder, tracks processed files, and only processes new/changed files.

Usage:
    python ingestion/run_ingestion.py
"""

import sys
from pathlib import Path
import json
import hashlib
from datetime import datetime
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.pipeline import IngestionPipeline
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
TRACKER_FILE = DATA_DIR / "processed_files.json"
SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.html', '.htm', '.txt']


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate MD5 hash of a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        MD5 hash string
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def load_tracker() -> dict:
    """
    Load processed files tracker.
    
    Returns:
        Dictionary of processed files
    """
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_tracker(tracker: dict):
    """
    Save processed files tracker.
    
    Args:
        tracker: Dictionary of processed files
    """
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKER_FILE, 'w') as f:
        json.dump(tracker, f, indent=2)


def find_all_documents(data_dir: Path) -> list:
    """
    Find all supported documents in data directory.
    
    Args:
        data_dir: Path to data directory
        
    Returns:
        List of file paths
    """
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(data_dir.rglob(f'*{ext}'))
    return files


def should_process_file(file_path: Path, tracker: dict) -> tuple:
    """
    Check if file should be processed.
    
    Args:
        file_path: Path to file
        tracker: Processed files tracker
        
    Returns:
        Tuple of (should_process: bool, reason: str)
    """
    file_key = str(file_path.relative_to(DATA_DIR))
    
    # New file
    if file_key not in tracker:
        return True, "new file"
    
    # Check if file changed
    current_hash = calculate_file_hash(file_path)
    stored_hash = tracker[file_key].get('file_hash')
    
    if current_hash != stored_hash:
        return True, "file modified"
    
    return False, "already processed"


def run_ingestion():
    """Main ingestion runner."""
    console.print("\n[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]  Automated Document Ingestion Runner[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════[/bold cyan]\n")
    
    try:
        # Load tracker
        tracker = load_tracker()
        console.print(f"[cyan]Tracker loaded:[/cyan] {len(tracker)} files previously processed\n")
        
        # Find all documents
        console.print(f"[cyan]Scanning directory:[/cyan] {DATA_DIR}")
        all_files = find_all_documents(DATA_DIR)
        console.print(f"[green]✓[/green] Found {len(all_files)} documents\n")
        
        # Determine which files to process
        files_to_process = []
        skipped_files = []
        
        for file_path in all_files:
            should_process, reason = should_process_file(file_path, tracker)
            if should_process:
                files_to_process.append((file_path, reason))
            else:
                skipped_files.append(file_path)
        
        # Display summary
        console.print(f"[yellow]Files to process:[/yellow] {len(files_to_process)}")
        console.print(f"[gray]Files to skip:[/gray] {len(skipped_files)}\n")
        
        if not files_to_process:
            console.print("[green]✓ All files already processed! Nothing to do.[/green]\n")
            return 0
        
        # Display files to process
        table = Table(title="Files to Process")
        table.add_column("File", style="cyan")
        table.add_column("Reason", style="yellow")
        
        for file_path, reason in files_to_process:
            table.add_row(
                str(file_path.relative_to(DATA_DIR)),
                reason
            )
        
        console.print(table)
        console.print()
        
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
        
        # Process files
        processed_count = 0
        failed_files = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task(
                "Processing files...",
                total=len(files_to_process)
            )
            
            for file_path, reason in files_to_process:
                try:
                    progress.update(
                        task,
                        description=f"Processing {file_path.name}..."
                    )
                    
                    # Process file
                    pipeline.process_file(
                        file_path=str(file_path),
                        clean_text=True
                    )
                    
                    # Update tracker
                    file_key = str(file_path.relative_to(DATA_DIR))
                    tracker[file_key] = {
                        'file_path': str(file_path),
                        'file_hash': calculate_file_hash(file_path),
                        'processed_at': datetime.now().isoformat(),
                        'file_size': file_path.stat().st_size,
                        'reason': reason
                    }
                    
                    processed_count += 1
                    progress.advance(task)
                    
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
                    failed_files.append((file_path, str(e)))
                    progress.advance(task)
        
        # Save tracker
        save_tracker(tracker)
        console.print(f"\n[green]✓[/green] Tracker updated: {TRACKER_FILE}\n")
        
        # Display results
        stats = pipeline.get_stats()
        
        result_table = Table(title="Ingestion Results")
        result_table.add_column("Metric", style="cyan")
        result_table.add_column("Value", style="green")
        
        result_table.add_row("Files processed", str(processed_count))
        result_table.add_row("Files failed", str(len(failed_files)))
        result_table.add_row("Files skipped", str(len(skipped_files)))
        result_table.add_row("Total chunks in Qdrant", str(stats['total_chunks']))
        result_table.add_row("Collection name", stats['collection_name'])
        
        console.print(result_table)
        console.print()
        
        # Display failures if any
        if failed_files:
            console.print("[bold red]Failed Files:[/bold red]")
            for file_path, error in failed_files:
                console.print(f"  [red]✗[/red] {file_path.name}: {error}")
            console.print()
        
        console.print("[bold green]✓ Ingestion Complete![/bold green]\n")
        
        return 0 if not failed_files else 1
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}\n")
        logger.exception("Ingestion failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_ingestion())
