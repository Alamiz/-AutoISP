from enum import Enum, auto

class FlowResult(Enum):
    """Enum representing the result of a flow handler action."""
    COMPLETED = auto()  # Automation is done successfully
    SUCCESS = auto()    # Handler succeeded, move to next page/step
    RESTART = auto()    # Restart the whole automation from the start
    RETRY = auto()      # Retry the current handler
    ABORT = auto()      # Terminate the automation (failure)
    SKIP = auto()       # Skip current handler and continue
    FAILED = auto()     # Generic failure (treat as ABORT or RETRY depending on context)
    
    # Specific failure states (terminal)
    LOCKED = auto()
    WRONG_EMAIL = auto()
    WRONG_PASSWORD = auto()
    ADD_PROTECTION = auto()
    SUSPENDED = auto()
    PHONE_VERIFICATION = auto()
    CAPTCHA = auto()

