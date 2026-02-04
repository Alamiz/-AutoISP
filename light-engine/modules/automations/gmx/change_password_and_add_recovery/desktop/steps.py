import string
import secrets
from playwright.sync_api import Page
from core.utils.element_finder import deep_find_elements
from core.flow_engine.step import Step, StepResult
from modules.core.flow_state import FlowResult
from core.utils.retry_decorators import retry_action
from modules.core.utils.credential_manager import update_credentials_file, update_processed_log

# Temp email service
TEMP_MAIL_URL = "https://temp-mail.io/"


def generate_secure_password(length=16) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits
    # Ensure at least one of each required type
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
    ]
    # Fill the rest
    password += [secrets.choice(alphabet) for _ in range(length - 3)]
    # Shuffle
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)


class OpenAccountMenuStep(Step):
    """Click on the account avatar to open the account menu."""
    
    def run(self, page: Page) -> StepResult:
        try:
            self.automation.human_click(
                page,
                selectors=['appa-account-avatar div.appa-user-icon'],
                deep_search=True
            )
            self.logger.info("Opened account menu", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(1500)
            return StepResult(status=FlowResult.SUCCESS, message="Opened account menu")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to open account menu: {e}")


class NavigateToAccountSettingsStep(Step):
    """Click on the first navigation link to go to account settings."""
    
    def run(self, page: Page) -> StepResult:
        try:
            self.automation.human_click(
                page,
                selectors=['section.appa-account-avatar__navigation > a:nth-child(1)'],
                deep_search=True
            )
            self.logger.info("Navigated to account settings", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(2000)
            return StepResult(status=FlowResult.SUCCESS, message="Navigated to account settings")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to navigate to account settings: {e}")

class ChangePasswordStep(Step):
    """Fill in the password fields and submit the password change."""
    
    def run(self, page: Page) -> StepResult:
        try:
            # Click Security menu item first
            self.logger.info("Clicking Security menu item...", extra={"account_id": self.account.id})
            self.automation.human_click(
                page,
                selectors=['li[data-icon="security"]'],
                deep_search=True
            )
            page.wait_for_timeout(2000)

            # Click change password link
            self.logger.info("Clicking change password menu item...", extra={"account_id": self.account.id})
            self.automation.human_click(
                page,
                selectors=['a[href*="changePassword"]'],
                deep_search=True
            )
            page.wait_for_timeout(2000)

            # Generate new password
            new_password = generate_secure_password()
            self.automation.new_password = new_password
            self.logger.info(f"Generated new password: {new_password}", extra={"account_id": self.account.id})
            
            current_password = self.account.password
            
            # Fill current password
            self._fill_current_password(page, current_password)
            
            # Fill new password
            self._fill_new_password(page, new_password)
            
            # Confirm new password
            self._fill_confirm_password(page, new_password)
            
            # Submit
            self._submit_password_change(page)
            
            # Verify password change success by checking for confirmation message
            page.wait_for_timeout(3000)
            confirm_elements = deep_find_elements(page, '.hint-confirm#feedback', timeout_ms=5000)
            
            if not confirm_elements:
                self.logger.error("Password change confirmation not found", extra={"account_id": self.account.id})
                return StepResult(status=FlowResult.RETRY, message="Password change failed: confirmation not found")
            
            # Save new password immediately to output/changed_passwords.txt
            try:
                self.logger.info("Saving new password to output/changed_passwords.txt...", extra={"account_id": self.account.id})
                update_credentials_file("output/changed_passwords.txt", self.account.email, new_password)
                
                # Also update the processed log file with the NEW password
                log_path = getattr(self.automation, 'recovery_log_path', None)
                if log_path:
                    self.logger.info(f"Updating processed log: {log_path}", extra={"account_id": self.account.id})
                    update_processed_log(log_path, self.account.email, new_password)
            except Exception as e:
                self.logger.error(f"Failed to update logs: {e}", extra={"account_id": self.account.id})
            
            self.logger.info("Password changed successfully", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(2000)
            return StepResult(status=FlowResult.SUCCESS, message="Password changed successfully")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to change password: {e}")
    
    @retry_action()
    def _fill_current_password(self, page: Page, password: str):
        elements = deep_find_elements(
            page,
            css_selector='div[id*="currentPasswordPanel"] input[type="password"]'
        )
        if not elements:
            raise Exception("Current password input not found")
        elements[0].fill(password)
        self.logger.info("Filled current password", extra={"account_id": self.account.id})
    
    @retry_action()
    def _fill_new_password(self, page: Page, password: str):
        elements = deep_find_elements(
            page,
            css_selector='div[id*="newPasswordFieldPanel"] input[type="password"]'
        )
        if not elements:
            raise Exception("New password input not found")
        elements[0].fill(password)
        self.logger.info("Filled new password", extra={"account_id": self.account.id})
    
    @retry_action()
    def _fill_confirm_password(self, page: Page, password: str):
        elements = deep_find_elements(
            page,
            css_selector='div[id*="retypeNewPasswordFieldPanel"] input[type="password"]'
        )
        if not elements:
            raise Exception("Confirm password input not found")
        elements[0].fill(password)
        self.logger.info("Filled confirm password", extra={"account_id": self.account.id})
    
    @retry_action()
    def _submit_password_change(self, page: Page):
        self.automation.human_click(
            page,
            selectors=['button.pos-button--cta'],
            deep_search=True
        )
        self.logger.info("Submitted password change", extra={"account_id": self.account.id})
        page.wait_for_timeout(3000)

class AddRecoveryEmailStep(Step):
    """
    Set up temp-mail.io inbox, fill recovery email on web.de,
    wait for verification code, and complete the verification.
    """
    
    def run(self, page: Page) -> StepResult:
        temp_mail_page = None
        try:
            # Click Security menu item first
            self.logger.info("Clicking Security menu item...", extra={"account_id": self.account.id})
            self.automation.human_click(
                page,
                selectors=['li[data-icon="security"]'],
                deep_search=True
            )
            page.wait_for_timeout(2000)

            # Get the email username (before @)
            email_username = self.account.email.split('@')[0]
            
            # Use CURRENT account password (old password) for recovery flow
            current_password = self.account.password
            
            # Step 1: Open temp-mail.io in a new page
            self.logger.info("Opening temp-mail.io...", extra={"account_id": self.account.id})
            temp_mail_page = page.context.new_page()
            temp_mail_page.goto(TEMP_MAIL_URL)
            temp_mail_page.wait_for_timeout(3000)
            
            # Step 2: Click change button on temp-mail
            self.logger.info("Clicking change button on temp-mail...", extra={"account_id": self.account.id})
            temp_mail_page.click('button[data-qa="change-button"]')
            temp_mail_page.wait_for_timeout(1500)
            
            # Step 3: Insert email username
            self.logger.info(f"Inserting email username: {email_username}", extra={"account_id": self.account.id})
            temp_mail_page.fill('form input', email_username)
            temp_mail_page.wait_for_timeout(1000)
            
            # Step 4: Click domain dropdown to open it
            self.logger.info("Opening domain dropdown...", extra={"account_id": self.account.id})
            temp_mail_page.click('select[data-qa="selected-domain"]')
            temp_mail_page.wait_for_timeout(1000)
            
            # Step 5: Select the first domain option
            self.logger.info("Selecting first domain option...", extra={"account_id": self.account.id})
            temp_mail_page.click('section.flex-col > button:nth-of-type(1)')
            temp_mail_page.wait_for_timeout(1000)
            
            # Step 6: Click submit button
            self.logger.info("Clicking submit button...", extra={"account_id": self.account.id})
            temp_mail_page.click('button[data-qa="submit-button"]')
            temp_mail_page.wait_for_timeout(3000)
            
            # Step 7: Get the full temp email address
            temp_email_input = temp_mail_page.query_selector('div.items-center.relative > input#email')
            if temp_email_input:
                recovery_email = temp_email_input.input_value()
            else:
                # Fallback: construct email manually
                recovery_email = f"{email_username}@bltiwd.com"
            
            self.logger.info(f"Generated temp email: {recovery_email}", extra={"account_id": self.account.id})
            self.automation.recovery_email = recovery_email
            
            if not recovery_email:
                self.logger.error("Failed to get temp email address", extra={"account_id": self.account.id})
                return StepResult(status=FlowResult.FAILED, message="Failed to get temp email address")
            
            # Step 8: Navigate to recovery email page (Click the link)
            self.navigate_to_recovery_email_page(page)
            
            # Step 9: Check for existing recovery email
            email_field = deep_find_elements(page, 'input#contactEmail', timeout_ms=5000)
            if not email_field:
                raise Exception("Recovery email input field not found")
            
            existing_email = email_field[0].input_value().strip()
            
            if existing_email:
                self.logger.info(f"Existing recovery email found: {existing_email}. Starting deletion flow...", extra={"account_id": self.account.id})
                
                # 1. Fill current password
                self._fill_password(page, current_password)
                
                # 2. Click submit
                self._submit_recovery_email(page)
                
                # 3. Click delete link a[target="_self"]
                page.wait_for_timeout(3000)
                delete_links = deep_find_elements(page, 'a[target="_self"]', timeout_ms=5000)
                if not delete_links:
                    raise Exception("Delete link a[target='_self'] not found")
                
                delete_links[0].click()
                page.wait_for_timeout(2000)
                
                # REDO add steps with verification (uses retry decorator)
                self._add_recovery_email_with_verification(page, recovery_email, current_password)
                
            else:
                self.logger.info("No existing recovery email found. Adding direct...", extra={"account_id": self.account.id})
                # No existing email flow:
                # Step 9-10: Fill recovery email, password, submit (first attempt)
                self._add_recovery_email_with_verification(page, recovery_email, current_password)
            
            # Step 11: Wait for verification email on temp-mail.io
            code = self._wait_for_verification_code(temp_mail_page)
            
            if not code:
                self.logger.error("Failed to get verification code", extra={"account_id": self.account.id})
                return StepResult(status=FlowResult.FAILED, message="Failed to get verification code")
            
            self.logger.info(f"Got verification code: {code}", extra={"account_id": self.account.id})
            
            # Step 12: Fill the verification code (6 separate inputs)
            self._fill_verification_code(page, code)
            
            # Step 13: Submit the verification code
            self._submit_verification_code(page)
            
            # Step 14: Wait for confirmation icon
            self._check_confirmation(page)
            
            self.logger.info(f"Recovery email {recovery_email} verified successfully", extra={"account_id": self.account.id})
            
            # Save to processed log: account_email|password|recovery_email
            # Use current_password (old one)
            log_path = getattr(self.automation, 'recovery_log_path', None)
            if log_path:
                self.logger.info(f"Saving to processed log: {log_path}", extra={"account_id": self.account.id})
                update_processed_log(log_path, self.account.email, current_password, recovery_email)
            
            return StepResult(status=FlowResult.SUCCESS, message="Recovery email added and verified successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to add recovery email: {e}", extra={"account_id": self.account.id})
            return StepResult(status=FlowResult.RESTART, message=f"Failed to add recovery email: {e}")
        finally:
            # Clean up temp mail page
            if temp_mail_page:
                try:
                    # Delete the temp mail account
                    self.automation.human_click(
                        temp_mail_page,
                        selectors=['button[data-qa="delete-button"]'],
                        deep_search=False
                    )
                    temp_mail_page.close()
                except:
                    pass
    
    @retry_action()
    def navigate_to_recovery_email_page(self, page: Page):
        self.logger.info("Navigating to recovery email page...", extra={"account_id": self.account.id})
        self.automation.human_click(
            page,
            selectors=['a[href*="changeContactEmail"]'],
            deep_search=True
        )
        
        # Verify navigation happened by checking for an element on the next page
        # Retry check for 5 seconds
        navigation_success = False
        for _ in range(5):
            if deep_find_elements(page, 'input#contactEmail', timeout_ms=3000):
                navigation_success = True
                break
            page.wait_for_timeout(1000)
            
        if not navigation_success:
            raise Exception("Failed to navigate to recovery email page: input#contactEmail not found")
            
        page.wait_for_timeout(2000)

    @retry_action()
    def _fill_recovery_email(self, page: Page, email: str):
        elements = deep_find_elements(
            page,
            css_selector='input#contactEmail'
        )
        if not elements:
            raise Exception("Recovery email input not found")
        elements[0].fill(email)
        self.logger.info("Filled recovery email", extra={"account_id": self.account.id})
    
    @retry_action()
    def _fill_password(self, page: Page, password: str):
        elements = deep_find_elements(
            page,
            css_selector='input#password'
        )
        if not elements:
            raise Exception("Password input not found")
        elements[0].fill(password)
        self.logger.info("Filled password for recovery email", extra={"account_id": self.account.id})
    
    @retry_action()
    def _add_recovery_email_with_verification(self, page: Page, recovery_email: str, password: str):
        """
        Combined method to fill recovery email, password, submit, and verify.
        Raises exception if verification fails (triggers retry).
        """
        self.logger.info("Adding recovery email...", extra={"account_id": self.account.id})
        
        # Fill recovery email
        email_elements = deep_find_elements(page, 'input#contactEmail', timeout_ms=5000)
        if not email_elements:
            raise Exception("Recovery email input not found")
        email_elements[0].fill(recovery_email)
        
        # Fill password
        password_elements = deep_find_elements(page, 'input#password', timeout_ms=5000)
        if not password_elements:
            raise Exception("Password input not found")
        password_elements[0].fill(password)
        
        # Submit
        self.automation.human_click(
            page,
            selectors=['button[type="submit"]'],
            deep_search=True
        )
        page.wait_for_timeout(5000)
        
        # Verify by checking for code input field
        code_input = deep_find_elements(page, 'input#code-field-0', timeout_ms=10000)
        if not code_input:
            raise Exception("Recovery email submission failed: code input not found")
        
        self.logger.info("Recovery email submitted successfully, code input visible", extra={"account_id": self.account.id})

    @retry_action()
    def _submit_recovery_email(self, page: Page):
        self.automation.human_click(
            page,
            selectors=['button[type="submit"]'],
            deep_search=True
        )
        self.logger.info("Submitted recovery email form", extra={"account_id": self.account.id})
        page.wait_for_timeout(5000)  # Wait for code to be sent
    
    
    def _wait_for_verification_code(self, temp_mail_page: Page, max_attempts: int = 10) -> str:
        """
        Wait for verification email on temp-mail.io and extract the code.
        Polls for up to max_attempts * 10 seconds.
        Filters for email with subject containing "E-Mail-Kontaktadresse bestätigen".
        """
        code = None
        email_found = False
        target_subject = "E-Mail-Kontaktadresse bestätigen"
        
        for attempt in range(max_attempts):
            self.logger.info(f"Waiting for email... attempt {attempt + 1}/{max_attempts}", extra={"account_id": self.account.id})
            
            # Reload the page
            temp_mail_page.reload()
            temp_mail_page.wait_for_timeout(10000)
            
            # Check for emails with matching subject
            email_items = temp_mail_page.query_selector_all('ul.email-list > li')
            for item in email_items:
                try:
                    subject_el = item.query_selector('span.message__subject')
                    if subject_el:
                        subject_text = subject_el.inner_text()
                        if target_subject in subject_text:
                            self.logger.info(f"Verification email found: {subject_text}", extra={"account_id": self.account.id})
                            item.click()
                            temp_mail_page.wait_for_timeout(2000)
                            email_found = True
                            break
                except:
                    continue
            
            if email_found:
                break
        
        if not email_found:
            self.logger.error("Verification email not received within timeout", extra={"account_id": self.account.id})
            return None
        
        # Extract the verification code
        self.logger.info("Extracting verification code...", extra={"account_id": self.account.id})
        
        for _ in range(5):
            temp_mail_page.wait_for_timeout(3000)
            
            # Find the verification code element
            code_element = temp_mail_page.query_selector('span#verification-code')
            if code_element:
                code = code_element.inner_text().strip()
                if code:
                    break
        
        if not code:
            self.logger.error("Failed to extract verification code from email", extra={"account_id": self.account.id})
            return None
        
        return code
    
    def _fill_verification_code(self, page: Page, code: str):
        """Fill the 6-digit verification code into separate input fields."""
        self.logger.info("Filling verification code...", extra={"account_id": self.account.id})
        
        for i, digit in enumerate(code[:6]):
            try:
                input_selector = f'input#code-field-{i}'
                
                # Use deep_find_elements instead of wait_for_selector
                elements = []
                for attempt in range(10):  # Retry up to 10 times (10 seconds)
                    elements = deep_find_elements(page, css_selector=input_selector)
                    if elements:
                        break
                    page.wait_for_timeout(1000)
                
                if elements:
                    elements[0].fill(digit)
                    page.wait_for_timeout(100)
                else:
                    self.logger.warning(f"Code field {input_selector} not found after retries", extra={"account_id": self.account.id})
            except Exception as e:
                self.logger.warning(f"Failed to fill code field {i}: {e}", extra={"account_id": self.account.id})
        
        self.logger.info("Verification code filled", extra={"account_id": self.account.id})
    
    @retry_action()
    def _submit_verification_code(self, page: Page):
        """Click the submit button for the verification code."""
        self.automation.human_click(
            page,
            selectors=['button[data-testid="code"]'],
            deep_search=True
        )
        self.logger.info("Submitted verification code", extra={"account_id": self.account.id})
        page.wait_for_timeout(3000)
    
    def _check_confirmation(self, page: Page, timeout: int = 5000):
        """Wait for the confirmation icon to appear."""
        self.logger.info("Waiting for confirmation...", extra={"account_id": self.account.id})
        try:
            # Wait for the SVG path that indicates success
            confirmation_path = 'path[d="M10 .25A9.75 9.75 0 1 0 19.75 10 9.75 9.75 0 0 0 10 .25zM8.14 15l-4.6-4.6 1.78-1.73 2.82 2.83L14.68 5l1.77 1.77z"]'
            page.wait_for_selector(confirmation_path, timeout=timeout)
            self.logger.info("Confirmation icon appeared", extra={"account_id": self.account.id})

            self.automation.human_click(
                page,
                selectors=['button[data-testid="redirect"]'],
                deep_search=True,
                timeout=timeout
            )
            self.logger.info("Clicked redirect button", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(f"Failed to check for confirmation", extra={"account_id": self.account.id})

class SaveSecuredAccountStep(Step):
    """Save the secured account details to the output file."""
    
    def run(self, page: Page) -> StepResult:
        try:
            import os
            
            email = self.account.email
            new_password = getattr(self.automation, 'new_password', self.account.password)
            recovery_email = getattr(self.automation, 'recovery_email', '')
            
            # Get output directory from automation
            output_dir = getattr(self.automation, 'output_dir', None)
            if not output_dir:
                # Use log_dir parent as fallback
                log_dir = getattr(self.automation, 'log_dir', None)
                if log_dir:
                    output_dir = os.path.dirname(os.path.dirname(log_dir))
                else:
                    # Ultimate fallback
                    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'output')
            
            # Full path to the secured accounts file
            secured_file = os.path.join(output_dir, 'secured_accounts.txt')
            
            # Append account details
            with open(secured_file, 'a', encoding='utf-8') as f:
                f.write(f"{email}|{new_password}|{recovery_email}\n")
            
            self.logger.info(f"Saved secured account to {secured_file}", extra={"account_id": self.account.id})
            
            return StepResult(status=FlowResult.COMPLETED, message="Saved secured account details")
        except Exception as e:
            self.logger.error(f"Failed to save secured account: {e}", extra={"account_id": self.account.id})
            # Don't fail the whole automation just because we couldn't save
            return StepResult(status=FlowResult.SUCCESS, message=f"Warning: Failed to save account details: {e}")