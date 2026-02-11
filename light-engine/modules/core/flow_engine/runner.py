# core/flow_engine/runner.py
from typing import Optional
from .step import Step, StepResult
from .state_handler import StateHandlerRegistry
from modules.core.flow_state import FlowResult

class StepRunner:
    def __init__(self, initial_step: Step, state_registry: Optional[StateHandlerRegistry] = None):
        """
        Accept a single initial step that may chain to others via payload.
        
        Args:
            initial_step: The first step to execute
            state_registry: Optional StateHandlerRegistry for handling unexpected pages
        """
        self.initial_step = initial_step
        self.state_registry = state_registry
        self.logger = initial_step.logger if hasattr(initial_step, 'logger') else None
        self.execution_trace = []  # Track all step executions for debugging

    def _check_page_state(self, page, current_step) -> Optional[StepResult]:
        """
        Check if we're on an unexpected page and handle it.
        Returns StepResult if page was handled, None if page is expected.
        """
        if not self.state_registry:
            return None
            
        try:
            page_id = self.state_registry.identify(page)
            
            # Log the current page state
            if self.logger:
                self.logger.debug(f"Current page identified as: {page_id}", extra={"account_id": self.account.id})
            
            # Check if there's a handler for this unexpected page
            handler = self.state_registry.get_handler(page_id)
            
            if handler:
                if self.logger:
                    self.logger.warning(f"Unexpected page detected: {page_id}. Running handler...", extra={"account_id": self.account.id})
                
                result = handler.handle(page)
                
                if result in (FlowResult.ABORT, FlowResult.FAILED, FlowResult.LOCKED,
                              FlowResult.WRONG_EMAIL, FlowResult.WRONG_PASSWORD,
                              FlowResult.SUSPENDED, FlowResult.PHONE_VERIFICATION, FlowResult.CAPTCHA):
                    return StepResult(
                        status=result,
                        message=f"Flow terminated by {page_id} handler"
                    )
                elif result == FlowResult.SUCCESS:
                    if self.logger:
                        self.logger.info(f"Handler for {page_id} completed. Continuing flow...", extra={"account_id": self.account.id})
                    return None  # Continue with current step
                elif result == FlowResult.RETRY:
                    if self.logger:
                        self.logger.info(f"Handler for {page_id} requests retry", extra={"account_id": self.account.id})
                    return StepResult(status=FlowResult.RETRY, message=f"Retry requested by {page_id} handler")
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during page state check: {e}", exc_info=True, extra={"account_id": self.account.id})
        
        return None

    def run(self, page):
        """Execute steps dynamically, following the chain via result.payload."""
        current_step = self.initial_step
        step_index = 0
        
        while current_step is not None:
            step_index += 1
            attempt = 0
            next_step = None
            
            # Check page state before executing step
            state_result = self._check_page_state(page, current_step)
            if state_result:
                if state_result.status != FlowResult.RETRY:
                    self._log_execution_trace()
                    return state_result
                elif state_result.status == FlowResult.RETRY:
                    # Handler wants us to retry - don't increment attempt counter
                    page.wait_for_timeout(1000)
                    continue
            
            while attempt < current_step.max_retries:
                attempt += 1
                
                # Record execution attempt
                trace_entry = {
                    "step_index": step_index,
                    "step_name": current_step.__class__.__name__,
                    "attempt": attempt,
                    "url": page.url if page else "unknown"
                }
                
                if self.logger:
                    self.logger.info(
                        f"[Step {step_index}] Executing {current_step.__class__.__name__} "
                        f"(Attempt {attempt}/{current_step.max_retries})",
                        extra={"account_id": self.account.id}
                    )

                try:
                    result: StepResult = current_step.run(page)
                    trace_entry["status"] = result.status.name
                    trace_entry["message"] = result.message
                    
                except Exception as e:
                    result = StepResult(status=FlowResult.FAILED, message=str(e))
                    trace_entry["status"] = "exception"
                    trace_entry["message"] = str(e)
                    trace_entry["exception_type"] = type(e).__name__
                    
                    if self.logger:
                        self.logger.exception(
                            f"[Step {step_index}] Exception in {current_step.__class__.__name__}: {e}",
                            extra={"account_id": self.account.id}
                        )
                
                self.execution_trace.append(trace_entry)

                # Handle StepResult
                if result.status == FlowResult.SUCCESS:
                    if self.logger:
                        self.logger.info(f"[Step {step_index}] ✓ SUCCESS: {result.message or ''}", extra={"account_id": self.account.id})
                    next_step = result.payload
                    break

                elif result.status == FlowResult.RETRY:
                    if self.logger:
                        self.logger.warning(
                            f"[Step {step_index}] ↻ RETRY ({attempt}/{current_step.max_retries}): "
                            f"{result.message or ''}",
                            extra={"account_id": self.account.id}
                        )
                    if attempt < current_step.max_retries:
                        page.wait_for_timeout(1000)  # Brief pause before retry
                    continue

                elif result.status == FlowResult.SKIP:
                    if self.logger:
                        self.logger.info(f"[Step {step_index}] ⊘ SKIP: {result.message or ''}", extra={"account_id": self.account.id})
                    next_step = result.payload
                    break

                elif result.status in (FlowResult.FAILED, FlowResult.ABORT, FlowResult.LOCKED,
                                     FlowResult.WRONG_EMAIL, FlowResult.WRONG_PASSWORD,
                                     FlowResult.SUSPENDED, FlowResult.PHONE_VERIFICATION, FlowResult.CAPTCHA):
                    if self.logger:
                        self.logger.error(f"[Step {step_index}] ✗ {result.status.name}: {result.message or ''}", extra={"account_id": self.account.id})
                    self._log_execution_trace()
                    return result
            
            else:
                # Max retries exceeded
                error_msg = f"Max retries ({current_step.max_retries}) exceeded for {current_step.__class__.__name__}"
                if self.logger:
                    self.logger.error(f"[Step {step_index}] {error_msg}", extra={"account_id": self.account.id})
                self._log_execution_trace()
                return StepResult(status=FlowResult.FAILED, message=error_msg)
            
            # Move to next step
            current_step = next_step

        # All steps completed successfully
        if self.logger:
            self.logger.info("✓ Flow completed successfully", extra={"account_id": self.account.id})
        return StepResult(status=FlowResult.SUCCESS, message="Flow completed successfully")
    
    def _log_execution_trace(self):
        """Log the complete execution trace for debugging."""
        if self.logger and self.execution_trace:
            for entry in self.execution_trace:
                self.logger.info(
                    f"Step {entry['step_index']}: {entry['step_name']} "
                    f"(Attempt {entry['attempt']}) -> {entry['status']}",
                    extra={"account_id": self.account.id}
                )
                if entry.get('message'):
                    self.logger.info(f"  Message: {entry['message']}", extra={"account_id": self.account.id})
                if entry.get('url'):
                    self.logger.info(f"  URL: {entry['url']}", extra={"account_id": self.account.id})