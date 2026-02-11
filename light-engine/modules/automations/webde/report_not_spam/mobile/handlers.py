# automations/webde/report_not_spam/mobile/handlers.py
"""
State handlers for web.de Mobile Report Not Spam using StatefulFlow.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler
from modules.core.flow_state import FlowResult
from core.humanization.actions import HumanAction
from core.utils.browser_utils import navigate_to
from core.models import Account

class UnknownPageHandler(StateHandler):
    """Handle unknown pages"""

    def handle(self, page: Page) -> FlowResult:
        try:
            navigate_to(page, "https://lightmailer-bs.web.de/")
            return FlowResult.RETRY
        except Exception:
            return FlowResult.ABORT