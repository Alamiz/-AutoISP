from .retry_decorators import retry_action
from playwright.sync_api import Page

@retry_action()
def navigate_to(page: Page, url: str):
    page.goto(url, timeout=90_000)