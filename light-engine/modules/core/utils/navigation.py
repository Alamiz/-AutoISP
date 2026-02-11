# core/flow_engine/navigation.py
"""Reliable navigation utilities with retry logic."""

import time
import logging
from playwright.sync_api import Page
from core.utils.browser_utils import navigate_to
from core.models import Account

def navigate_with_retry(
    page: Page,
    url: str,
    account: Account,
    max_retries: int = 4,
    retry_delay: float = 3.0,
    timeout: int = 30000,
    logger: logging.Logger = None
) -> bool:
    """
    Navigate to a URL with automatic retry on network errors.
    
    Args:
        page: Playwright page object
        url: URL to navigate to
        max_retries: Maximum number of retry attempts
        retry_delay: Seconds to wait between retries
        timeout: Navigation timeout in milliseconds
        logger: Optional logger for status messages
        
    Returns:
        True if navigation succeeded, False if all retries failed
        
    Raises:
        Exception: Re-raises the last exception if all retries fail
    """
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            if logger:
                logger.info(f"Navigating to {url} (attempt {attempt}/{max_retries})", extra={"account_id": account.id})
            
            navigate_to(page, url)
            return True
            
        except Exception as e:
            last_error = e
            error_msg = str(e)
            
            # Check if it's a network error worth retrying
            is_retryable = any(err in error_msg for err in [
                "ERR_INTERNET_DISCONNECTED",
                "ERR_NAME_NOT_RESOLVED", 
                "ERR_CONNECTION_REFUSED",
                "ERR_CONNECTION_RESET",
                "ERR_TIMED_OUT",
                "ERR_CONNECTION_TIMED_OUT",
                "ERR_NETWORK_CHANGED",
                "net::",
                "Timeout"
            ])
            
            if logger:
                logger.warning(f"Navigation failed (attempt {attempt}/{max_retries}): {error_msg}", extra={"account_id": account.id})
            
            if attempt < max_retries:
                if is_retryable:
                    if logger:
                        logger.info(f"Retryable error detected. Waiting {retry_delay}s before retry...", extra={"account_id": account.id})
                    time.sleep(retry_delay)
                else:
                    # Non-retryable error, fail immediately
                    if logger:
                        logger.error(f"Non-retryable error: {error_msg}", extra={"account_id": account.id})
                    raise
            else:
                if logger:
                    logger.error(f"Max retries ({max_retries}) exceeded. Last error: {error_msg}", extra={"account_id": account.id})
                raise
    
    # Should not reach here, but just in case
    if last_error:
        raise last_error
    return False