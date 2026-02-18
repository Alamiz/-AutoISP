import random
import asyncio
from typing import Optional, List
from playwright.async_api import Page, ElementHandle, Locator

class HumanBehavior:
    """Simulates human-like interactions with browser elements"""
    
    def __init__(self, 
                 job_id: Optional[str] = None,
                 typing_speed_range=(0.05, 0.15),  # s per character (adjusted for async sleep)
                 mouse_move_duration_range=(0.1, 0.3),  # s
                 action_delay_range=(0.5, 1.5),  # s between actions
                 reading_delay_range=(3.0, 5.0)):  # s for "reading"
        
        self.job_id = job_id
        self.typing_speed_range = typing_speed_range
        self.mouse_move_duration_range = mouse_move_duration_range
        self.action_delay_range = action_delay_range
        self.reading_delay_range = reading_delay_range
    
    async def _random_delay(self, min_s: float, max_s: float):
        """Generate random delay in seconds"""
        if self.job_id:
             pass
             # Cancellation check logic here if needed
        await asyncio.sleep(random.uniform(min_s, max_s))
    
    def _human_typing_delay(self):
        """Simulate human typing speed variation (returns milliseconds for type method)"""
        # Playwright type delay is in ms
        return random.uniform(self.typing_speed_range[0] * 1000, self.typing_speed_range[1] * 1000)
    
    async def type_text(self, element: Locator, text: str, clear_first: bool = False):
        """Type text with human-like delays between keystrokes"""
        if clear_first:
            await element.clear()
            await self._random_delay(0.2, 0.5)
        
        # Sometimes type in bursts, sometimes character by character
        if random.random() > 0.3:  # 70% chance of burst typing
            burst_size = random.randint(2, 5)
            for i in range(0, len(text), burst_size):
                chunk = text[i:i+burst_size]
                # Playwright's type method delay is in milliseconds
                await element.type(chunk, delay=self._human_typing_delay())
                if random.random() > 0.8:  # 20% chance of pause between bursts
                    await self._random_delay(0.3, 0.8)
        else:
            await element.type(text, delay=self._human_typing_delay())
    
    async def click(self, element: ElementHandle, page: Optional[Page] = None, force: bool = False, timeout: Optional[float] = None):
        """
        Perform a human-like mouse movement and click.
        If page is not provided, fall back to element.click().
        """

        # If no page, we cannot move the mouse → fallback
        if page is None:
            await element.click(force=force, timeout=timeout)
            return

        box = await element.bounding_box()
        if not box:
            await element.click(force=force, timeout=timeout)
            return

        # Target point with slight randomness
        target_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
        target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)

        # Current mouse position (fallback if unknown) - Playwright doesn't expose current mouse pos easily
        start_x = random.randint(0, 100)
        start_y = random.randint(0, 100)

        steps = random.randint(18, 30)

        for i in range(steps):
            t = i / steps
            eased = t * t * (3 - 2 * t)

            x = start_x + (target_x - start_x) * eased
            y = start_y + (target_y - start_y) * eased

            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.008, 0.02))

        await asyncio.sleep(random.uniform(0.1, 0.25))

        await page.mouse.down()
        await asyncio.sleep(random.uniform(0.05, 0.12))
        await page.mouse.up()
    
    async def hover(self, element: Locator):
        """Hover over an element with human-like behavior"""
        # Small delay before hovering
        await self._random_delay(*self.mouse_move_duration_range)
        
        await element.hover()
        await self._random_delay(0.2, 0.5)
    
    async def select(self, element: Locator, value: Optional[str] = None, label: Optional[str] = None):
        """Select option in dropdown with human-like behavior"""
        # Small delay before interacting with the dropdown
        await self._random_delay(*self.mouse_move_duration_range)

        # Occasionally hover before selecting
        if random.random() > 0.7:  # 30% chance
            await element.hover()
            await self._random_delay(0.2, 0.5)

        if label:
            await element.select_option(label=label)
        else:
            await element.select_option(value)

        # Small delay after selection
        await self._random_delay(0.1, 0.3)
    
    async def wait_before_action(self):
        """Random delay between actions (simulating human decision-making)"""
        await self._random_delay(*self.action_delay_range)
    
    async def read_delay(self):
        """Simulate reading/processing information"""
        await self._random_delay(*self.reading_delay_range)
    
    async def scroll_into_view(self, element: Optional[Locator] = None, page: Optional[Page] = None, y_amount: Optional[int] = None, smooth: bool = True):
        """
        Scrolls to an element with human-like behavior, or scrolls the page by a defined amount.
        """
        if element:
            await self._random_delay(0.08, 0.26)  # Delay before scrolling to element
            if smooth and random.random() > 0.5:
                # Sometimes scroll past and then back
                await element.evaluate("el => el.scrollIntoView({behavior: 'smooth', block: 'center'})")
                await self._random_delay(0.17, 0.42)
            else:
                await element.scroll_into_view_if_needed()
                await self._random_delay(0.15, 0.3)
            await self._random_delay(0.08, 0.26)
        elif page and y_amount is not None:
            await self.scroll_page_by(page, y_amount)
        else:
            await self._random_delay(0.05, 0.15)
    
    async def scroll_page_by(self, page: Page, y_amount: int):
        """Scrolls the page by a given amount with human-like behavior."""
        await self._random_delay(0.2, 0.5)  # Delay before starting scroll

        # Simulate scrolling in smaller, random steps
        current_scroll_y = await page.evaluate("() => window.scrollY")
        # target_scroll_y = current_scroll_y + y_amount # Unused variable

        direction = 1 if y_amount > 0 else -1
        remaining_scroll = abs(y_amount)

        while remaining_scroll > 0:
            step_size = random.randint(50, 200)
            if step_size > remaining_scroll:
                step_size = remaining_scroll

            scroll_by = step_size * direction
            await page.evaluate(f"window.scrollBy(0, {scroll_by})")
            remaining_scroll -= step_size

            # Random delay between scroll steps
            await self._random_delay(0.05, 0.15)

        await self._random_delay(0.2, 0.5)
