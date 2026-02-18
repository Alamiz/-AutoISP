from .retry_decorators import retry_action
from playwright.async_api import Page

@retry_action()
async def navigate_to(page: Page, url: str):
    await page.goto(url, timeout=90_000)