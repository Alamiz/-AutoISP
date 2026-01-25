from typing import Dict, Optional
import threading
from playwright.sync_api import BrowserContext, Playwright

class BrowserRegistry:
    """
    Singleton registry to track active browser instances by job_id.
    Allows for forceful termination of browsers when a job is cancelled.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.active_browsers = {}  # Map job_id -> (playwright, context)
        return cls._instance

    def register(self, job_id: str, playwright: Playwright, context: BrowserContext):
        """Register a browser context for a job."""
        if not job_id:
            return
            
        with self._lock:
            self.active_browsers[job_id] = (playwright, context)
            print(f"✅ Registered browser for job {job_id}")

    def unregister(self, job_id: str):
        """Unregister a browser context."""
        if not job_id:
            return
            
        with self._lock:
            if job_id in self.active_browsers:
                del self.active_browsers[job_id]
                print(f"✅ Unregistered browser for job {job_id}")

    def force_close(self, job_id: str):
        """Force close the browser context for a job."""
        if not job_id:
            return
            
        with self._lock:
            if job_id in self.active_browsers:
                print(f"⚠️ Force closing browser for job {job_id}...")
                pw, context = self.active_browsers[job_id]
                try:
                    context.close()
                except Exception as e:
                    print(f"Error closing context: {e}")
                
                try:
                    pw.stop()
                except Exception as e:
                    print(f"Error stopping playwright: {e}")
                
                del self.active_browsers[job_id]
                print(f"✅ Force closed browser for job {job_id}")

browser_registry = BrowserRegistry()