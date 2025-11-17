from playwright.sync_api import sync_playwright, BrowserContext, Page
from core.chrome_profiles_manager import ChromeProfileManager
import os
from typing import Optional, List

STEALTH_INIT_SCRIPT = """
// Minimal evasions for navigator properties commonly checked
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });

// Provide minimal chrome object shape expected by some sites
window.chrome = window.chrome || { runtime: {} };

// Overwrite permissions query to avoid "denied" anomalies
const originalQuery = navigator.permissions && navigator.permissions.query;
if (originalQuery) {
  navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
      Promise.resolve({ state: Notification.permission }) :
      originalQuery(parameters)
  );
}
"""

class PlaywrightBrowserFactory:
    """
    Helper to create a Playwright persistent Chrome context with
    common stealth patches and human-like helpers.

    Notes:
      - Pass a path to a real Chrome profile (a profile you used manually) to reduce detection.
      - This reduces some detectable signals but does NOT guarantee undetectability.
      - Prefer official APIs (e.g., Gmail API) for account automation.
    """

    def __init__(
        self,
        profile_dir: str,
        channel: str = "chrome",
        headless: bool = False,
        executable_path: Optional[str] = None,
        additional_args: Optional[List[str]] = None,
        use_stealth: bool = True,
        start_maximized: bool = True,
        slow_mo: Optional[int] = None,
    ):
        self.profile_path = os.path.join(ChromeProfileManager().chrome_data_path, profile_dir)
        self.profile_dir = profile_dir
        self.channel = channel
        self.headless = headless
        self.executable_path = executable_path
        self.additional_args = additional_args or []
        self.use_stealth = use_stealth
        self.start_maximized = start_maximized
        self.slow_mo = slow_mo

        self._pw = None
        self._context: Optional[BrowserContext] = None
        self._opened = False

    def start(self):
        """Start Playwright and launch persistent context."""
        if self._opened:
            return
        # ensure profile path exists
        os.makedirs(self.profile_path, exist_ok=True)
        self._pw = sync_playwright().start()
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-default-browser-check",
            "--disable-dev-shm-usage"
        ]
        if self.start_maximized:
            args.append("--start-maximized")
        args.extend(self.additional_args)
        
        launch_kwargs = dict(
            user_data_dir=self.profile_path,
            channel=self.channel,
            headless=self.headless,
            args=args,
            slow_mo=self.slow_mo,
            ignore_default_args=["--enable-automation"],
        )
        
        # optionally set executable path (useful if you want the same Chrome binary you use manually)
        if self.executable_path:
            launch_kwargs["executable_path"] = self.executable_path
        
        # launch persistent context (this will reuse the real profile)
        self._context = self._pw.chromium.launch_persistent_context(**launch_kwargs)
        
        # Add init script to every page in the context (before any page scripts run)
        if self.use_stealth and self._context:
            self._context.add_init_script(STEALTH_INIT_SCRIPT)
        
        self._opened = True

    def get_page(self) -> Page:
        """Return the first existing page (reuse profile tab) or create a new one."""
        if not self._opened:
            self.start()

        pages = self._context.pages
        # Prefer an existing non-empty page (the profile's active tab)
        if pages:
            return pages[0]
        return self._context.new_page()

    def new_page(self) -> Page:
        """Open a fresh new page in the context."""
        if not self._opened:
            self.start()
        return self._context.new_page()

    def close(self):
        """Close context and stop Playwright."""
        if self._context:
            try:
                self._context.close()
            except Exception:
                pass
            self._context = None
        if self._pw:
            try:
                self._pw.stop()
            except Exception:
                pass
            self._pw = None
        self._opened = False