import random
import time
from typing import Optional, List
from playwright.sync_api import Page, ElementHandle, Locator

class HumanBehavior:
    """Simulates human-like interactions with browser elements"""
    
    def __init__(self, 
                 job_id: Optional[str] = None,
                 typing_speed_range=(50, 150),  # ms per character
                 mouse_move_duration_range=(100, 300),  # ms
                 action_delay_range=(500, 1500),  # ms between actions
                 reading_delay_range=(3000, 5000)):  # ms for "reading"
        
        self.job_id = job_id
        self.typing_speed_range = typing_speed_range
        self.mouse_move_duration_range = mouse_move_duration_range
        self.action_delay_range = action_delay_range
        self.reading_delay_range = reading_delay_range
    
    def _random_delay(self, min_ms: int, max_ms: int):
        """Generate random delay in milliseconds"""
        if self.job_id:
            pass
            # from modules.core.job_manager import job_manager
            # job_manager.check_cancellation(self.job_id)
            
        time.sleep(random.uniform(min_ms, max_ms) / 1000)
    
    def _human_typing_delay(self):
        """Simulate human typing speed variation"""
        return random.uniform(*self.typing_speed_range)
    
    def type_text(self, element: Locator, text: str, clear_first: bool = False):
        """Type text with human-like delays between keystrokes"""
        if clear_first:
            element.clear()
            self._random_delay(200, 500)
        
        # Sometimes type in bursts, sometimes character by character
        if random.random() > 0.3:  # 70% chance of burst typing
            burst_size = random.randint(2, 5)
            for i in range(0, len(text), burst_size):
                chunk = text[i:i+burst_size]
                element.type(chunk, delay=self._human_typing_delay())
                if random.random() > 0.8:  # 20% chance of pause between bursts
                    self._random_delay(300, 800)
        else:
            element.type(text, delay=self._human_typing_delay())
    
    def click(self, element: ElementHandle, page: Optional[Page] = None, force: bool = False, timeout: Optional[float] = None):
        """
        Perform a human-like mouse movement and click.
        If page is not provided, fall back to element.click().
        """

        # If no page, we cannot move the mouse → fallback
        if page is None:
            element.click(force=force, timeout=timeout)
            return

        box = element.bounding_box()
        if not box:
            element.click(force=force, timeout=timeout)
            return

        # Target point with slight randomness
        target_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
        target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)

        # Current mouse position (fallback if unknown)
        start_x = random.randint(0, 100)
        start_y = random.randint(0, 100)

        steps = random.randint(18, 30)

        for i in range(steps):
            t = i / steps
            eased = t * t * (3 - 2 * t)

            x = start_x + (target_x - start_x) * eased
            y = start_y + (target_y - start_y) * eased

            page.mouse.move(x, y)
            time.sleep(random.uniform(0.008, 0.02))

        time.sleep(random.uniform(0.1, 0.25))

        page.mouse.down()
        time.sleep(random.uniform(0.05, 0.12))
        page.mouse.up()
    
    def hover(self, element: Locator):
        """Hover over an element with human-like behavior"""
        # Small delay before hovering
        self._random_delay(*self.mouse_move_duration_range)
        
        element.hover()
        self._random_delay(200, 500)
    
    def select(self, element: Locator, value: Optional[str] = None, label: Optional[str] = None):
        """Select option in dropdown with human-like behavior"""
        # Small delay before interacting with the dropdown
        self._random_delay(*self.mouse_move_duration_range)

        # Occasionally hover before selecting
        if random.random() > 0.7:  # 30% chance
            element.hover()
            self._random_delay(200, 500)

        if label:
            element.select_option(label=label)
        else:
            element.select_option(value)

        # Small delay after selection
        self._random_delay(100, 300)
    
    def wait_before_action(self):
        """Random delay between actions (simulating human decision-making)"""
        self._random_delay(*self.action_delay_range)
    
    def read_delay(self):
        """Simulate reading/processing information"""
        self._random_delay(*self.reading_delay_range)
    
    def scroll_into_view(self, element: Optional[Locator] = None, page: Optional[Page] = None, y_amount: Optional[int] = None, smooth: bool = True):
        """
        Scrolls to an element with human-like behavior, or scrolls the page by a defined amount.

        If `element` is provided, it scrolls the element into view.
        If `element` is None, and `page` and `y_amount` are provided, it scrolls the page by `y_amount`.
        """
        if element:
            self._random_delay(80, 260)  # Delay before scrolling to element
            if smooth and random.random() > 0.5:
                # Sometimes scroll past and then back
                element.evaluate("el => el.scrollIntoView({behavior: 'smooth', block: 'center'})")
                self._random_delay(170, 420)
            else:
                element.scroll_into_view_if_needed()
                self._random_delay(150, 300)
            self._random_delay(80, 260) # Delay after scrolling to element
        elif page and y_amount is not None:
            self.scroll_page_by(page, y_amount)
        else:
            # If neither element nor scroll amount is provided, just a small human-like delay
            self._random_delay(50, 150)
    
    def scroll_page_by(self, page: Page, y_amount: int):
        """Scrolls the page by a given amount with human-like behavior."""
        self._random_delay(200, 500)  # Delay before starting scroll

        # Simulate scrolling in smaller, random steps
        current_scroll_y = page.evaluate("() => window.scrollY")
        target_scroll_y = current_scroll_y + y_amount

        direction = 1 if y_amount > 0 else -1
        remaining_scroll = abs(y_amount)

        while remaining_scroll > 0:
            step_size = random.randint(50, 200)  # Scroll in chunks of 50-200 pixels
            if step_size > remaining_scroll:
                step_size = remaining_scroll

            scroll_by = step_size * direction
            page.evaluate(f"window.scrollBy(0, {scroll_by})")
            remaining_scroll -= step_size

            # Random delay between scroll steps
            self._random_delay(50, 150)  # Short delay between steps

        self._random_delay(200, 500)  # Delay after finishing scroll