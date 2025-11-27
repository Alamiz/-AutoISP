import time
import functools
import logging

# Setup basic logger
logging.basicConfig(level=logging.INFO)

class RequiredActionFailed(Exception):
    """Raised when a required automation action fails after all retries."""
    pass

def retry(max_retries=3, required=True, delay=1):
    """
    Decorator to retry a function multiple times.
    
    :param max_retries: number of retries
    :param required: if True, failure stops the flow
    :param delay: seconds to wait between retries
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logging.warning(f"[{func.__name__}] Attempt {attempts}/{max_retries} failed: {e}")
                    if attempts >= max_retries:
                        if required:
                            logging.error(f"[{func.__name__}] Required action failed after {max_retries} retries. Stopping automation.")
                            raise RequiredActionFailed(f"{func.__name__} failed after {max_retries} retries.") from e
                        else:
                            logging.warning(f"[{func.__name__}] Optional action failed after {max_retries} retries. Continuing automation.")
                            return None
                    time.sleep(delay)
        return wrapper
    return decorator
