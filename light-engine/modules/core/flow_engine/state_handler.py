# core/flow_engine/state_handler.py
from typing import Callable, Dict, Optional
from playwright.sync_api import Page
from core.utils.browser_utils import navigate_to
from modules.core.flow_state import FlowResult

class StateHandler:
    """
    Base class for handling unexpected page states.
    Subclass this to implement specific page handlers.
    """
    def __init__(self, automation=None, logger=None):
        self.automation = automation
        self.logger = logger
        self.account = automation.account if automation else None
    
    def handle(self, page: Page) -> FlowResult:
        """
        Handle unexpected pages.
        
        Returns:
            FlowResult.SUCCESS - Page handled successfully, continue with current step
            FlowResult.ABORT - Critical error, abort the entire flow
            FlowResult.RETRY - Request retry of current step after handling
        """
        raise NotImplementedError("Subclasses must implement handle()")


class StateHandlerRegistry:
    """
    Registry for page state handlers.
    Maps page identifiers to their handlers.
    """
    def __init__(
        self, 
        identifier_func: Callable[[Page, str, dict], str], 
        signatures: dict, 
        logger=None
    ):
        """
        Args:
            identifier_func: Function that identifies the current page
                            Signature: (page, url, signatures) -> page_id
            signatures: Dictionary of page signatures for identification
            logger: Optional logger instance
        """
        self.identifier_func = identifier_func
        self.signatures = signatures
        self._handlers: Dict[str, StateHandler] = {}
        self.logger = logger

    def register(self, page_id: str, handler: StateHandler):
        """Register a handler for a specific page ID."""
        self._handlers[page_id] = handler
        if self.logger:
            self.logger.debug(f"Registered handler for page: {page_id}")

    def unregister(self, page_id: str):
        """Remove a handler for a specific page ID."""
        if page_id in self._handlers:
            del self._handlers[page_id]
            if self.logger:
                self.logger.debug(f"Unregistered handler for page: {page_id}")

    def get_handler(self, page_id: str) -> Optional[StateHandler]:
        """Get the handler for a specific page ID."""
        return self._handlers.get(page_id)

    def identify(self, page: Page) -> str:
        """
        Identify the current page.
        
        Returns:
            Page identifier string, or "unknown" if identification fails
        """
        try:
            page_id = self.identifier_func(page, page.url, self.signatures)
            return page_id
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to identify page: {e}")
            return "unknown"
    
    def has_handler(self, page_id: str) -> bool:
        """Check if a handler exists for the given page ID."""
        return page_id in self._handlers
    
    def list_handlers(self) -> list[str]:
        """Get list of all registered page IDs."""
        return list(self._handlers.keys())


class RedirectStateHandler(StateHandler):
    """
    Convenience handler that redirects to a specific URL.
    Useful for common redirect scenarios.
    """
    def __init__(self, redirect_url: str, action: FlowResult = FlowResult.SUCCESS, logger=None):
        super().__init__(logger)
        self.redirect_url = redirect_url
        self.action = action
    
    def handle(self, page: Page) -> FlowResult:
        try:
            if self.logger:
                self.logger.info(f"Redirecting to: {self.redirect_url}")
            navigate_to(page, self.redirect_url)
            page.wait_for_load_state("domcontentloaded")
            return self.action
        except Exception as e:
            if self.logger:
                self.logger.error(f"Redirect failed: {e}")
            return FlowResult.ABORT