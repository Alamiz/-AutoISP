import time
import asyncio
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
    Supports both sync and async functions.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(f"Action '{func.__name__}' failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(f"Action '{func.__name__}' failed (attempt {attempt}/{max_attempts}): {e}")
                    
                    if on_retry:
                        try:
                            if asyncio.iscoroutinefunction(on_retry):
                                await on_retry(attempt, e, current_delay)
                            else:
                                on_retry(attempt, e, current_delay)
                        except Exception as callback_error:
                            logger.error(f"Retry callback failed: {callback_error}")
                    
                    logger.info(f"Retrying in {current_delay}s...")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(f"Action '{func.__name__}' failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(f"Action '{func.__name__}' failed (attempt {attempt}/{max_attempts}): {e}")
                    
                    if on_retry:
                        try:
                            on_retry(attempt, e, current_delay)
                        except Exception as callback_error:
                            logger.error(f"Retry callback failed: {callback_error}")
                    
                    logger.info(f"Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def retry_on_timeout(max_attempts: int = 3, delay: float = 2.0):
    from playwright.async_api import TimeoutError as AsyncTimeout
    from playwright.sync_api import TimeoutError as SyncTimeout
    
    return retry_action(
        max_attempts=max_attempts,
        delay=delay,
        backoff=1.5,
        exceptions=(AsyncTimeout, SyncTimeout)
    )


def retry_on_element_not_found(max_attempts: int = 3, delay: float = 1.0):
    from playwright.async_api import Error as AsyncError
    from playwright.sync_api import Error as SyncError
    
    return retry_action(
        max_attempts=max_attempts,
        delay=delay,
        backoff=1.5,
        exceptions=(AsyncError, SyncError)
    )


def retry_with_page_refresh(max_attempts: int = 2):
    def refresh_callback(attempt, exception, delay):
        logger.info("Refreshing page before retry...")
        # Note: Logic to refresh page would depend on context (args[0] if it's page)
    
    return retry_action(
        max_attempts=max_attempts,
        delay=2.0,
        on_retry=refresh_callback
    )
