"""
Automation run metadata tracking.
Tracks run-level statistics like counts, timing, and generates summary report.
"""
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import os

# Define default output directory relative to this file or project root
# Assuming light-engine/modules/core/automation_metadata.py
# We want light-engine/output
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir))) # Adjust as needed
OUTPUT_DIR = Path(os.path.join(os.getcwd(), "output"))

class AutomationMetadata:
    """
    Tracks metadata for an automation run including status counts and timing.
    Thread/process-safe using multiprocessing Manager for shared state.
    """
    
    # Default statuses to track
    DEFAULT_STATUSES = ["SUCCESS", "FAILED", "LOCKED", "WRONG_EMAIL", "WRONG_PASSWORD", 
                        "ADD_PROTECTION", "RECOVERY_EMAIL_REACHED", "COMPLETED", "ERROR"]
    
    @staticmethod
    def create_shared_state(manager) -> tuple:
        """
        Create shared state objects using the provided multiprocessing Manager.
        Call this in the main process before starting workers.
        
        Returns:
            tuple: (status_counts dict, lock)
        """
        status_counts = manager.dict()
        lock = manager.Lock()
        
        # Initialize common statuses
        for status in AutomationMetadata.DEFAULT_STATUSES:
            status_counts[status] = 0
        
        return status_counts, lock
    
    def __init__(self, automation_name: str, total_accounts: int, 
                 status_counts: Dict = None, lock = None, output_dir: Path = OUTPUT_DIR):
        """
        Initialize metadata tracker.
        
        Args:
            automation_name: Name of the automation being run
            total_accounts: Total number of accounts to process
            status_counts: Shared dict from multiprocessing Manager (optional)
            lock: Shared lock from multiprocessing Manager (optional)
            output_dir: Directory to save the metadata file
        """
        self.automation_name = automation_name
        self.total_accounts = total_accounts
        self.output_dir = output_dir
        
        # Use provided shared state or create local (for non-multiprocess use)
        self._status_counts = status_counts if status_counts is not None else {}
        self._lock = lock
        
        # Initialize if not already initialized
        if status_counts is None:
            for status in self.DEFAULT_STATUSES:
                self._status_counts[status] = 0
        
        # Timing
        self.start_time = time.time()
        self.start_datetime = datetime.now()
        self.end_time: float = None
        self.end_datetime: datetime = None
    
    def increment_status(self, status: str) -> None:
        """
        Increment the count for a status (thread/process-safe).
        
        Args:
            status: The status to increment (e.g., "SUCCESS", "FAILED")
        """
        if self._lock:
            with self._lock:
                current = self._status_counts.get(status, 0)
                self._status_counts[status] = current + 1
        else:
            current = self._status_counts.get(status, 0)
            self._status_counts[status] = current + 1
    
    def get_counts(self) -> Dict[str, int]:
        """Get a copy of current status counts."""
        if self._lock:
            with self._lock:
                return dict(self._status_counts)
        return dict(self._status_counts)
    
    def finalize(self) -> Path:
        """
        Finalize the run and write metadata to file.
        
        Returns:
            Path to the metadata file
        """
        self.end_time = time.time()
        self.end_datetime = datetime.now()
        
        duration_seconds = self.end_time - self.start_time
        duration_str = self._format_duration(duration_seconds)
        
        # Filename is always metadata.txt in the run directory
        filename = "metadata.txt"
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        filepath = self.output_dir / filename
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write metadata
        counts = self.get_counts()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"AUTOMATION RUN REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Automation: {self.automation_name}\n")
            f.write(f"Start Time: {self.start_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"End Time:   {self.end_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration:   {duration_str}\n\n")
            
            f.write("-" * 40 + "\n")
            f.write("ACCOUNT STATISTICS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Accounts: {self.total_accounts}\n\n")
            
            f.write("Status Counts:\n")
            for status, count in sorted(counts.items()):
                if count > 0:  # Only show statuses with counts
                    f.write(f"  {status}: {count}\n")
            
            # Calculate processed
            processed = sum(counts.values())
            f.write(f"\nProcessed: {processed}/{self.total_accounts}\n")
            
            f.write("\n" + "=" * 60 + "\n")
        
        return filepath
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration as HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
