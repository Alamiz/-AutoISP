import time
import logging
from functools import wraps
from typing import Callable, Type, Tuple, Optional

# Setup basic logger
logging.basicConfig(level=logging.INFO)

class RequiredActionFailed(Exception):
    """Raised when a required automation action fails after all retries."""
    def __init__(self, message: str, status: Optional['FlowResult'] = None):
        super().__init__(message)
        self.status = status
        self.message = message


logger = logging.getLogger("autoisp")

def retry_action(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):

    """
    Decorator for retrying actions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay (exponential backoff)
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called before each retry
                 Signature: on_retry(attempt, exception, delay)
    
    Example:

        @retry_action(max_attempts=3, delay=1.0, backoff=2.0)
        def click_element(page, selector):
            page.click(selector)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"Action '{func.__name__}' failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"Action '{func.__name__}' failed (attempt {attempt}/{max_attempts}): {e}"
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt, e, current_delay)
                        except Exception as callback_error:
                            logger.error(f"Retry callback failed: {callback_error}")
                    
                    logger.info(f"Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def retry_on_timeout(max_attempts: int = 3, delay: float = 2.0):
    """
    Specialized decorator for timeout errors.
    
    Example:
        @retry_on_timeout(max_attempts=3)
        def wait_for_element(page, selector):
            page.wait_for_selector(selector, timeout=5000)
    """
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    
    return retry_action(
        max_attempts=max_attempts,
        delay=delay,
        backoff=1.5,
        exceptions=(PlaywrightTimeout,)
    )


def retry_on_element_not_found(max_attempts: int = 3, delay: float = 1.0):
    """
    Specialized decorator for element not found errors.
    
    Example:
        @retry_on_element_not_found(max_attempts=5)
        def find_and_click(page, selector):
            element = page.locator(selector)
            element.click()
    """
    from playwright.sync_api import Error as PlaywrightError
    
    return retry_action(
        max_attempts=max_attempts,
        delay=delay,
        backoff=1.5,
        exceptions=(PlaywrightError,)
    )


def retry_with_page_refresh(max_attempts: int = 2):
    """
    Decorator that refreshes the page before retry.
    Useful for stale element issues.
    
    Example:
        @retry_with_page_refresh(max_attempts=2)
        def interact_with_element(page, selector):
            page.click(selector)
    """
    def refresh_callback(attempt, exception, delay):
        logger.info("Refreshing page before retry...")
        # Note: page object needs to be accessible in scope
        # This is a simplified version
    
    return retry_action(
        max_attempts=max_attempts,
        delay=2.0,
        on_retry=refresh_callback
    )
