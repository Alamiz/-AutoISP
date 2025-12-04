# core/flow_engine/state_handler.py
from typing import Callable, Dict, Optional
from playwright.sync_api import Page

class StateHandler:
    def handle(self, page: Page) -> str:
        """
        Handle unexpected pages.
        Return "continue" to let flow proceed, "abort" to stop.
        """
        raise NotImplementedError()

class StateHandlerRegistry:
    def __init__(self, identifier_func: Callable[[Page, str, dict], str], signatures: dict, logger=None):
        self.identifier_func = identifier_func
        self.signatures = signatures
        self._handlers = {}
        self.logger = logger

    def register(self, page_id: str, handler: StateHandler):
        self._handlers[page_id] = handler

    def get_handler(self, page_id: str) -> Optional[StateHandler]:
        return self._handlers.get(page_id)

    def identify(self, page) -> str:
        try:
            return self.identifier_func(page, page.url, self.signatures)
        except Exception:
            return "unknown"
