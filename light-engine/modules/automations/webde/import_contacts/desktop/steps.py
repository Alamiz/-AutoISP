from playwright.sync_api import Page
from core.flow_engine.step import Step, StepResult
from modules.core.flow_state import FlowResult
import random
import os

class OpenAddressBookStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Navigating to Address Book", extra={"account_id": self.account.id})
            self.automation.human_click(
                page,
                selectors=['nav#top-nav button[aria-controls="menu-services"]'],
                deep_search=False
            )
            page.wait_for_timeout(1000)

            self.automation.human_click(
                page,
                selectors=['button[data-item-name="addressbook"]'],
                deep_search=False
            )
            page.wait_for_timeout(3000)
            return StepResult(status=FlowResult.SUCCESS, message="Navigated to Address Book")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to navigate to Address Book: {e}")

class OpenImportPanelStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Opening Import Panel", extra={"account_id": self.account.id})

            page.wait_for_load_state("load")
            self.automation.human_click(
                page,
                selectors=['button[data-action="import"]'],
                deep_search=True
            )
            page.wait_for_timeout(2000)
            return StepResult(status=FlowResult.SUCCESS, message="Opened Import Panel")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to open Import Panel: {e}")

class SelectSourceStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Selecting Import Source", extra={"account_id": self.account.id})
            
            sources = ["file", "webde"]
            chosen_source = random.choice(sources)
            self.logger.info(f"Chosen source: {chosen_source}", extra={"account_id": self.account.id})
            
            # Save chosen source to automation instance for next step
            self.automation.chosen_source = chosen_source
            
            selector = f'div[data-action="select"][data-source="{chosen_source}"]'
            
            self.automation.human_click(
                page,
                selectors=[selector],
                deep_search=True
            )
            page.wait_for_timeout(1000)
            
            return StepResult(status=FlowResult.SUCCESS, message=f"Selected source: {chosen_source}")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to select source: {e}")

class UploadFileStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            vcf_path = getattr(self.automation, "vcf_file_path", None)
            if not vcf_path or not os.path.exists(vcf_path):
                return StepResult(status=FlowResult.FAILED, message=f"VCF file not found at: {vcf_path}")
            
            self.logger.info(f"Uploading file: {vcf_path}", extra={"account_id": self.account.id})
            
            chosen_source = getattr(self.automation, "chosen_source", "file")
            
            input_selector = 'input#fileimport-webde' if chosen_source == 'webde' else 'input#fileimport-file'
            
            # Find the input element
            file_input = self.automation._find_element_with_humanization(
                page,
                selectors=[input_selector],
                deep_search=True
            )
            
            if not file_input:
                return StepResult(status=FlowResult.RETRY, message=f"File input not found: {input_selector}")
                
            file_input.set_input_files(vcf_path)
            page.wait_for_timeout(2000)
            
            return StepResult(status=FlowResult.SUCCESS, message="File uploaded")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to upload file: {e}")

class UploadContactsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Clicking Upload Button", extra={"account_id": self.account.id})
            self.automation.human_click(
                page,
                selectors=['button[data-action="upload"]'],
                deep_search=True
            )
            page.wait_for_timeout(3000) # Wait for upload to process
            return StepResult(status=FlowResult.SUCCESS, message="Clicked Upload")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to click upload: {e}")

class ImportContactsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Confirming Import", extra={"account_id": self.account.id})
            self.automation.human_click(
                page,
                selectors=['button[data-action="select"]'],
                deep_search=True
            )
            page.wait_for_timeout(3000)
            return StepResult(status=FlowResult.SUCCESS, message="Confirmed Import")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to confirm import: {e}")

class VerifyImportStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Verifying Import Completion", extra={"account_id": self.account.id})
            
            success_element = self.automation._find_element_with_humanization(
                page,
                selectors=['div.status.complete div.content.box.ok'],
                deep_search=True,
                timeout=10000
            )
            
            if success_element:
                return StepResult(status=FlowResult.SUCCESS, message="Import verified successfully")
            
            # Fallback check if the exact selector provided by user works
            user_selector = 'div[class="status hide complete"] > div[class="content box ok"]'
            success_element_exact = self.automation._find_element_with_humanization(
                page,
                selectors=[user_selector],
                deep_search=True,
                timeout=5000
            )
            
            if success_element_exact:
                return StepResult(status=FlowResult.SUCCESS, message="Import verified successfully (exact selector)")

            return StepResult(status=FlowResult.FAILED, message="Success message not found")
            
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Verification failed: {e}")
