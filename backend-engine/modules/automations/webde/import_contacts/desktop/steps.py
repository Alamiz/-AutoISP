from core.utils.retry_decorators import retry_action
from playwright.sync_api import Page
from core.flow_engine.step import Step, StepResult, StepStatus
import random
import os

class OpenAddressBookStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Navigating to Address Book")
            self.automation.human_click(
                page,
                selectors=['div#actions-menu-primary a[data-item-name="addressbook"]'],
                deep_search=False
            )
            page.wait_for_timeout(3000)
            return StepResult(status=StepStatus.SUCCESS, message="Navigated to Address Book")
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to navigate to Address Book: {e}")

class OpenImportPanelStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Opening Import Panel")

            page.wait_for_load_state("load")
            self.automation.human_click(
                page,
                selectors=['button[data-action="import"]'],
                deep_search=True
            )
            page.wait_for_timeout(2000)
            return StepResult(status=StepStatus.SUCCESS, message="Opened Import Panel")
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to open Import Panel: {e}")

class SelectSourceStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Selecting Import Source")
            
            # Randomly choose between file or webde source as requested
            # "randomly click either one of this two: div[data-action="select"][data-source="file"], div[data-action="select"][data-source="webde"]"
            # However, the user request says: "click input#fileimport-file or input#fileimport-webde if choosed webde in the previouse step"
            # This implies if we choose "webde", we use input#fileimport-webde. If "file", input#fileimport-file.
            
            sources = ["file", "webde"]
            chosen_source = random.choice(sources)
            self.logger.info(f"Chosen source: {chosen_source}")
            
            # Save chosen source to automation instance for next step
            self.automation.chosen_source = chosen_source
            
            selector = f'div[data-action="select"][data-source="{chosen_source}"]'
            
            self.automation.human_click(
                page,
                selectors=[selector],
                deep_search=True
            )
            page.wait_for_timeout(1000)
            
            return StepResult(status=StepStatus.SUCCESS, message=f"Selected source: {chosen_source}")
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to select source: {e}")

class UploadFileStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            vcf_path = getattr(self.automation, "vcf_file_path", None)
            if not vcf_path or not os.path.exists(vcf_path):
                return StepResult(status=StepStatus.FAILURE, message=f"VCF file not found at: {vcf_path}")
            
            self.logger.info(f"Uploading file: {vcf_path}")
            
            chosen_source = getattr(self.automation, "chosen_source", "file")
            
            # "click input#fileimport-file or input#fileimport-webde if choosed webde in the previouse step and import the file"
            # Actually we need to set the input file, not just click.
            
            input_selector = 'input#fileimport-webde' if chosen_source == 'webde' else 'input#fileimport-file'
            
            # Find the input element
            file_input = self.automation._find_element_with_humanization(
                page,
                selectors=[input_selector],
                deep_search=True
            )
            
            if not file_input:
                return StepResult(status=StepStatus.RETRY, message=f"File input not found: {input_selector}")
                
            file_input.set_input_files(vcf_path)
            page.wait_for_timeout(2000)
            
            return StepResult(status=StepStatus.SUCCESS, message="File uploaded")
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to upload file: {e}")

class UploadContactsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Clicking Upload Button")
            self.automation.human_click(
                page,
                selectors=['button[data-action="upload"]'],
                deep_search=True
            )
            page.wait_for_timeout(3000) # Wait for upload to process
            return StepResult(status=StepStatus.SUCCESS, message="Clicked Upload")
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to click upload: {e}")

class ImportContactsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Confirming Import")
            self.automation.human_click(
                page,
                selectors=['button[data-action="select"]'],
                deep_search=True
            )
            page.wait_for_timeout(3000)
            return StepResult(status=StepStatus.SUCCESS, message="Confirmed Import")
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to confirm import: {e}")

class VerifyImportStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Verifying Import Completion")
            
            # "check this: div[class="status hide complete"] > div[class="content box ok"] to verify if completed successfully"
            # Note: "hide" class usually means hidden. If it's "status hide complete", maybe it becomes visible or class changes?
            # Or maybe the user meant `div.status.complete` (without hide)?
            # Assuming the user provided selector is what we should look for, but "hide" is suspicious.
            # Usually success messages appear.
            # Let's try to find it. If deep_search=True, we look everywhere.
            
            success_element = self.automation._find_element_with_humanization(
                page,
                selectors=['div.status.complete div.content.box.ok'], # Adjusted slightly to be more robust CSS selector
                deep_search=True,
                timeout=10000
            )
            
            if success_element:
                return StepResult(status=StepStatus.SUCCESS, message="Import verified successfully")
            
            # Fallback check if the exact selector provided by user works
            user_selector = 'div[class="status hide complete"] > div[class="content box ok"]'
            success_element_exact = self.automation._find_element_with_humanization(
                page,
                selectors=[user_selector],
                deep_search=True,
                timeout=5000
            )
            
            if success_element_exact:
                 return StepResult(status=StepStatus.SUCCESS, message="Import verified successfully (exact selector)")

            return StepResult(status=StepStatus.FAILURE, message="Success message not found")
            
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Verification failed: {e}")
