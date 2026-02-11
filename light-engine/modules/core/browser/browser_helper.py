from playwright.sync_api import sync_playwright, BrowserContext, Page
from core.browser.chrome_profiles_manager import ChromeProfileManager
import os
import sys
import logging
from typing import Optional, List, Dict
import psutil
from core.models import Account

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
          pass
      originalQuery(parameters)
  );
}
"""

def get_chrome_executable() -> Optional[str]:
    """
    Find the Chrome executable in this order:
        pass
    1. Bundled Chrome in resources folder (relative to this file or frozen app)
    2. ProgramData location (C:\\ProgramData\\AutoISP\\chrome-win64\\chrome.exe)
    3. None (let Playwright use its default)
    """
    # Check for bundled Chrome
    if getattr(sys, 'frozen', False):
        # Running as packaged app
        base_path = sys._MEIPASS
    else:
        # Running as script - look relative to this file
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.abspath(os.path.join(base_path, "..", "..", ".."))  # Go up to backend-engine
    
    bundled_chrome = os.path.join(base_path, "resources", "chrome-win64", "chrome.exe")
    if os.path.exists(bundled_chrome):
        return bundled_chrome
    
    # Check ProgramData location
    programdata_chrome = r"C:\ProgramData\AutoISP\chrome-win64\chrome.exe"
    if os.path.exists(programdata_chrome):
        return programdata_chrome
    
    # Return None to let Playwright use default
    return None


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
        account: Account,
        channel: str = "chrome",
        headless: bool = False,
        executable_path: Optional[str] = None,
        additional_args: Optional[List[str]] = None,
        use_stealth: bool = True,
        start_maximized: bool = True,
        slow_mo: Optional[int] = None,
        user_agent_type: str = "desktop",  # "desktop" or "mobile"
        job_id: Optional[str] = None,
    ):
        self.profile_path = os.path.join(ChromeProfileManager().chrome_data_path, profile_dir)
        self.profile_dir = profile_dir
        self.channel = channel
        self.headless = headless
        # Auto-detect Chrome executable if not provided
        self.executable_path = executable_path or get_chrome_executable()
        self.additional_args = additional_args or []
        self.use_stealth = use_stealth
        self.start_maximized = start_maximized
        self.slow_mo = slow_mo
        self.proxy_config = account.proxy_settings
        self.account = account
        self.user_agent_type = user_agent_type
        self.job_id = job_id

        self._pw = None
        self._context: Optional[BrowserContext] = None
        self._opened = False

        self.logger = logging.getLogger("autoisp")

    def start(self):
        """Start browser with extension"""
        if self._opened:
            return
            
        print(f"🚀 Starting browser with {self.user_agent_type} user agent...")
        if self.executable_path:
            print(f"📂 Using Chrome: {self.executable_path}")

        os.makedirs(self.profile_path, exist_ok=True)
        self._pw = sync_playwright().start()
        
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-default-browser-check",
            "--disable-dev-shm-usage",

            # Memory critical
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            # "--disable-extensions", # Enabling extensions for MailCheck
            "--disable-sync",
            "--disable-default-apps",
            "--disable-component-update",
            "--disable-client-side-phishing-detection",
            "--disable-hang-monitor",
            "--disable-popup-blocking",

            # Reduce process count
            "--process-per-site",
            "--renderer-process-limit=4",

            # GPU on RDP = useless
            "--disable-gpu",
            "--disable-software-rasterizer",

            # Kill Chrome background mode
            "--disable-features=Translate,BackForwardCache,AcceptCHFrame,MediaRouter"
        ]

        # Configure extensions based on provider
        extensions_to_load = []
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            modules_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))

            # if self.account.provider == 'libero':
            # Note: 'extentions' (with 't') for rektCaptcha
            # extensions_to_load.append(os.path.join(modules_dir, "extensions", "rektCaptcha"))
            # elif self.account.provider in ['gmx', 'webde', None]: 
            #     # Note: 'extensions' (with 's') for MailCheck
            #     # Defaulting to MailCheck for gmx/webde or if provider is None
            #     extensions_to_load.append(os.path.join(modules_dir, "extensions", "MailCheck"))

            # Always load popupBlocker
            # extensions_to_load.append(os.path.join(modules_dir, "extensions", "popupBlocker"))

            if extensions_to_load:
                print(f"🧩 Configuring {len(extensions_to_load)} extensions...")
                extensions_arg = ",".join(extensions_to_load)
                args.extend([
                    f"--disable-extensions-except={extensions_arg}",
                    f"--load-extension={extensions_arg}",
                ])
                
                for ext_path in extensions_to_load:
                    if os.path.exists(ext_path):
                         print(f"  + Loaded: {ext_path}")
                    else:
                         print(f"  ⚠️ Extension path not found: {ext_path}")

        except Exception as e:
            print(f"⚠️ Failed to configure extensions: {e}")

        # Only start maximized for desktop
        if self.user_agent_type == "desktop":
            args.append("--start-maximized")
        
        launch_kwargs = dict(
            user_data_dir=self.profile_path,
            headless=self.headless,
            args=args,
            ignore_default_args=["--enable-automation"],
            user_agent=self._get_user_agent()
        )
        
        # Use custom executable if available, otherwise use channel
        if self.executable_path:
            launch_kwargs['executable_path'] = self.executable_path
        else:
            launch_kwargs['channel'] = self.channel
        
        # Proxy configuration
        if self.proxy_config:
            proxy_settings = {
                'server': f"{self.proxy_config['protocol']}://{self.proxy_config['host']}:{self.proxy_config['port']}"
            }
            
            if 'username' in self.proxy_config and 'password' in self.proxy_config:
                proxy_settings['username'] = self.proxy_config['username']
                proxy_settings['password'] = self.proxy_config['password']
            
            launch_kwargs['proxy'] = proxy_settings
        
        try:
            self._context = self._pw.chromium.launch_persistent_context(**launch_kwargs)
            print("✅ Browser started successfully")

            self._opened = True
            
            # Register with registry if job_id is present
            if self.job_id:
                pass # removed
                # removed
            
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            raise
        
    def _get_user_agent(self):
        """Get user agent string based on type"""
        user_agents = {
            "desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
            "mobile": "Mozilla/5.0 (Linux; Android 12; Redmi Note 11 Build/SKQ1.211019.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/99.0.4844.88 Mobile Safari/537.36"
        }
        return user_agents.get(self.user_agent_type, user_agents["desktop"])

    def _get_mobile_viewport(self):
        """Get mobile viewport dimensions"""
        mobile_viewports = {
            "iphone_12": {"width": 390, "height": 844},
            "samsung_galaxy": {"width": 412, "height": 915},
            "pixel_5": {"width": 393, "height": 851},
        }
        # Using samsung galaxy dimensions as default
        return mobile_viewports["samsung_galaxy"]

    def get_page(self) -> Page:
        if not self._opened:
            self.start()
        pages = self._context.pages
        page = pages[0] if pages else self._context.new_page()
        
        # Set viewport for mobile after page is created
        if self.user_agent_type == "mobile":
            mobile_viewport = self._get_mobile_viewport()
            page.set_viewport_size(mobile_viewport)
            print(f"✅ Mobile viewport set: {mobile_viewport['width']}x{mobile_viewport['height']}")
        
        return page

    def new_page(self) -> Page:
        if not self._opened:
            self.start()
        page = self._context.new_page()
        
        # Set viewport for mobile after page is created
        if self.user_agent_type == "mobile":
            mobile_viewport = self._get_mobile_viewport()
            page.set_viewport_size(mobile_viewport)
            print(f"✅ Mobile viewport set: {mobile_viewport['width']}x{mobile_viewport['height']}")
        
        return page

    @staticmethod
    def kill_chrome_for_profile(profile_path: str):
        profile_path = os.path.abspath(profile_path).lower()

        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if proc.info["name"] != "chrome.exe":
                    continue

                cmdline = " ".join(proc.info.get("cmdline") or []).lower()
                if profile_path in cmdline:
                    proc.kill()

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def close(self):
        """Close context and stop Playwright."""
        self._opened = False
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
        
        self.kill_chrome_for_profile(self.profile_path)
        self.logger.info("Chrome processes killed for profile", extra={"account_id": self.account.id, "is_global":True})

    def force_close(self):
        """Forcefully close browser - kills all pages and browser."""
        self._opened = False
        self.logger.info("Force closing browser...", extra={"account_id": self.account.id, "is_global":True})
        
        # Close all pages first to interrupt any running operations
        if self._context:
            try:
                pages = self._context.pages
                self.logger.info(f"Closing {len(pages)} pages...", extra={"account_id": self.account.id, "is_global":True})
                for page in pages:
                    try:
                        page.close()
                    except Exception as e:
                        pass
            except Exception as e:
                self.logger.warning(f"Error accessing pages: {e}", extra={"account_id": self.account.id, "is_global":True})
            
            try:
                self._context.close()
                self.logger.info("Browser context closed", extra={"account_id": self.account.id, "is_global":True})
            except Exception as e:
                pass
            self._context = None
        
        # Force stop Playwright
        if self._pw:
            try:
                self._pw.stop()
                self.logger.info("Playwright stopped", extra={"account_id": self.account.id, "is_global":True})
            except Exception as e:
                pass
            self._pw = None
        
        self.kill_chrome_for_profile(self.profile_path)
        self.logger.info("Chrome processes killed for profile", extra={"account_id": self.account.id, "is_global":True})