# automations/webde/report_not_spam/mobile/handlers.py
"""
State handlers for web.de Mobile Report Not Spam using StatefulFlow.
"""
import asyncio
from playwright.async_api import Page
from core.flow_engine.state_handler import StateHandler
from modules.core.flow_state import FlowResult
from core.humanization.actions import HumanAction
from core.utils.browser_utils import navigate_to
from core.models import Account

class UnknownPageHandler(StateHandler):
    """Handle unknown pages"""

    async def handle(self, page: Page) -> FlowResult:
        try:
            await navigate_to(page, "https://alligator.navigator.web.de/go/?targetURI=https://link.web.de/mail/showStartView&ref=link")
            return FlowResult.RETRY
        except Exception:
            return FlowResult.ABORT