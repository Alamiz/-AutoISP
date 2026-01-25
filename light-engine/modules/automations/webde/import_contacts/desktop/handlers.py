# automations/webde/report_not_spam/desktop/handlers.py
"""
State handlers for web.de Desktop Import Contacts using StatefulFlow.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.humanization.actions import HumanAction
from core.utils.browser_utils import navigate_to
from core.models import Account

class UnknownPageHandler(StateHandler):
    """Handle unknown pages"""
    def handle(self, page: Page) -> HandlerAction:
        try:
            navigate_to(page, "https://web.de/")
            return "retry"
        except Exception as e:
            return "abort"