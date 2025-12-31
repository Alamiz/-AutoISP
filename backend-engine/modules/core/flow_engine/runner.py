# core/flow_engine/runner.py
from typing import Optional
from .step import Step, StepResult, StepStatus
from .state_handler import StateHandlerRegistry

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
                self.logger.debug(f"Current page identified as: {page_id}")
            
            # Check if there's a handler for this unexpected page
            handler = self.state_registry.get_handler(page_id)
            
            if handler:
                if self.logger:
                    self.logger.warning(f"Unexpected page detected: {page_id}. Running handler...")
                
                action = handler.handle(page)
                
                if action == "abort":
                    return StepResult(
                        status=StepStatus.FAILURE,
                        message=f"Flow aborted by {page_id} handler"
                    )
                elif action == "continue":
                    if self.logger:
                        self.logger.info(f"Handler for {page_id} completed. Continuing flow...")
                    return None  # Continue with current step
                elif action == "retry":
                    if self.logger:
                        self.logger.info(f"Handler for {page_id} requests retry")
                    return StepResult(status=StepStatus.RETRY, message=f"Retry requested by {page_id} handler")
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during page state check: {e}", exc_info=True)
        
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
                if state_result.status == StepStatus.FAILURE:
                    self._log_execution_trace()
                    return state_result
                elif state_result.status == StepStatus.RETRY:
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
                        f"(Attempt {attempt}/{current_step.max_retries})"
                    )

                try:
                    result: StepResult = current_step.run(page)
                    trace_entry["status"] = result.status.value
                    trace_entry["message"] = result.message
                    
                except Exception as e:
                    result = StepResult(status=StepStatus.FAILURE, message=str(e))
                    trace_entry["status"] = "exception"
                    trace_entry["message"] = str(e)
                    trace_entry["exception_type"] = type(e).__name__
                    
                    if self.logger:
                        self.logger.exception(f"[Step {step_index}] Exception in {current_step.__class__.__name__}: {e}")
                
                self.execution_trace.append(trace_entry)

                # Handle StepResult
                if result.status == StepStatus.SUCCESS:
                    if self.logger:
                        self.logger.info(f"[Step {step_index}] ✓ SUCCESS: {result.message or ''}")
                    next_step = result.payload
                    break

                elif result.status == StepStatus.RETRY:
                    if self.logger:
                        self.logger.warning(
                            f"[Step {step_index}] ↻ RETRY ({attempt}/{current_step.max_retries}): "
                            f"{result.message or ''}"
                        )
                    if attempt < current_step.max_retries:
                        page.wait_for_timeout(1000)  # Brief pause before retry
                    continue

                elif result.status == StepStatus.SKIP:
                    if self.logger:
                        self.logger.info(f"[Step {step_index}] ⊘ SKIP: {result.message or ''}")
                    next_step = result.payload
                    break

                elif result.status == StepStatus.FAILURE:
                    if self.logger:
                        self.logger.error(f"[Step {step_index}] ✗ FAILURE: {result.message or ''}")
                    self._log_execution_trace()
                    return result
            
            else:
                # Max retries exceeded
                error_msg = f"Max retries ({current_step.max_retries}) exceeded for {current_step.__class__.__name__}"
                if self.logger:
                    self.logger.error(f"[Step {step_index}] {error_msg}")
                self._log_execution_trace()
                return StepResult(status=StepStatus.FAILURE, message=error_msg)
            
            # Move to next step
            current_step = next_step

        # All steps completed successfully
        if self.logger:
            self.logger.info("✓ Flow completed successfully")
        return StepResult(status=StepStatus.SUCCESS, message="Flow completed successfully")
    
    def _log_execution_trace(self):
        """Log the complete execution trace for debugging."""
        if self.logger and self.execution_trace:
            self.logger.info("=" * 60)
            self.logger.info("EXECUTION TRACE")
            self.logger.info("=" * 60)
            for entry in self.execution_trace:
                self.logger.info(
                    f"Step {entry['step_index']}: {entry['step_name']} "
                    f"(Attempt {entry['attempt']}) -> {entry['status']}"
                )
                if entry.get('message'):
                    self.logger.info(f"  Message: {entry['message']}")
                if entry.get('url'):
                    self.logger.info(f"  URL: {entry['url']}")
            self.logger.info("=" * 60)