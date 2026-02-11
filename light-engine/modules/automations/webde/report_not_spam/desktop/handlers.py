# automations/webde/report_not_spam/desktop/handlers.py
"""
State handlers for web.de Desktop Report Not Spam using StatefulFlow.
"""
import logging
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
            navigate_to(page, "https://alligator.navigator.web.de/go/?targetURI=https://link.web.de/mail/showStartView&ref=link")
            return FlowResult.RETRY
        except Exception as e:
            return FlowResult.ABORT