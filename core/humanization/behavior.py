import random
import time
from typing import Optional, List
from playwright.sync_api import Page, ElementHandle, Locator

class HumanBehavior:
    """Simulates human-like interactions with browser elements"""
    
    def __init__(self, 
                 typing_speed_range=(50, 150),  # ms per character
                 mouse_move_duration_range=(100, 300),  # ms
                 action_delay_range=(500, 1500),  # ms between actions
                 reading_delay_range=(1000, 3000)):  # ms for "reading"
        
        self.typing_speed_range = typing_speed_range
        self.mouse_move_duration_range = mouse_move_duration_range
        self.action_delay_range = action_delay_range
        self.reading_delay_range = reading_delay_range
    
    def _random_delay(self, min_ms: int, max_ms: int):
        """Generate random delay in milliseconds"""
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
    
    def click(self, element: Locator, force: bool = False):
        """Click with human-like mouse movement"""
        # Small delay before clicking (simulating mouse movement)
        self._random_delay(*self.mouse_move_duration_range)
        
        # Occasionally double-check by hovering first
        if random.random() > 0.7:  # 30% chance
            element.hover()
            self._random_delay(200, 500)
        
        element.click(force=force)
    
    def wait_before_action(self):
        """Random delay between actions (simulating human decision-making)"""
        self._random_delay(*self.action_delay_range)
    
    def read_delay(self):
        """Simulate reading/processing information"""
        self._random_delay(*self.reading_delay_range)
    
    def scroll_into_view(self, element: Locator, smooth: bool = True):
        """Scroll to element with human-like behavior"""
        if smooth and random.random() > 0.5:
            # Sometimes scroll past and then back
            element.evaluate("el => el.scrollIntoView({behavior: 'smooth', block: 'center'})")
            self._random_delay(500, 1000)
        else:
            element.scroll_into_view_if_needed()
            self._random_delay(300, 600)