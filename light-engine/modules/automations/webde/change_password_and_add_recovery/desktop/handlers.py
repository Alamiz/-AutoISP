# automations/webde/change_password_and_add_recovery/desktop/handlers.py
"""
State handlers for web.de Desktop Change Password and Add Recovery.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler
from modules.core.flow_state import FlowResult
from core.utils.browser_utils import navigate_to

class UnknownPageHandler(StateHandler):
    """Handle unknown pages by redirecting to web.de homepage."""

    def handle(self, page: Page) -> FlowResult:
        try:
            navigate_to(page, "https://web.de/")
            return FlowResult.RETRY
        except Exception as e:
            return FlowResult.ABORT