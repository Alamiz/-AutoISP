# core/flow_engine/runner.py
from typing import Optional
from .step import Step, StepResult, StepStatus

class StepRunner:
    def __init__(self, initial_step: Step):
        """Accept a single initial step that may chain to others via payload."""
        self.initial_step = initial_step
        self.logger = initial_step.logger if hasattr(initial_step, 'logger') else None

    def run(self, page):
        """Execute steps dynamically, following the chain via result.payload."""
        current_step = self.initial_step
        step_index = 0
        
        while current_step is not None:
            step_index += 1
            attempt = 0
            next_step = None
            
            while attempt < current_step.max_retries:
                attempt += 1
                if self.logger:
                    self.logger.info(f"[Step {step_index}] Executing {current_step.__class__.__name__} (Attempt {attempt})")

                try:
                    result: StepResult = current_step.run(page)
                except Exception as e:
                    result = StepResult(status=StepStatus.FAILURE, message=str(e))
                    if self.logger:
                        self.logger.exception(f"[Step {step_index}] Exception: {e}")

                # Handle StepResult
                if result.status == StepStatus.SUCCESS:
                    if self.logger:
                        self.logger.info(f"[Step {step_index}] SUCCESS: {result.message or ''}")
                    next_step = result.payload  # Get next step from payload
                    break  # Exit retry loop

                elif result.status == StepStatus.RETRY:
                    if self.logger:
                        self.logger.warning(f"[Step {step_index}] RETRY: {result.message or ''}")
                    continue  # Retry current step

                elif result.status == StepStatus.SKIP:
                    if self.logger:
                        self.logger.info(f"[Step {step_index}] SKIP: {result.message or ''}")
                    next_step = result.payload  # Allow skipped steps to chain
                    break  # Exit retry loop

                elif result.status == StepStatus.FAILURE:
                    if self.logger:
                        self.logger.error(f"[Step {step_index}] FAILURE: {result.message or ''}")
                    return result  # Abort entire flow
            
            else:
                # Max retries exceeded (for loop completed without break)
                if self.logger:
                    self.logger.error(f"[Step {step_index}] Max retries exceeded for {current_step.__class__.__name__}")
                return StepResult(
                    status=StepStatus.FAILURE, 
                    message=f"Max retries exceeded for {current_step.__class__.__name__}"
                )
            
            # Move to next step
            current_step = next_step

        # All steps completed successfully
        return StepResult(status=StepStatus.SUCCESS, message="Flow completed successfully")