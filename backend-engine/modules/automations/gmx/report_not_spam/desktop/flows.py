import logging
import re
from playwright.sync_api import Page
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements

class ReportNotSpamFlowHandler():
    """Handles different GMX page flows for Report Not Spam"""
    
    def __init__(self, automation, email: str, password: str, search_text: str):
        self.automation = automation
        self.email = email
        self.password = password
        self.search_text = search_text
        self.logger = logging.getLogger("autoisp")
        # Use automation's human_action/behavior if available, or create new
        self.human_action = automation if isinstance(automation, HumanAction) else HumanAction()
        # Track email IDs of emails reported as not spam
        self.reported_email_ids = []

    def handle_inbox_page(self, page: Page) -> str:
        """
        Handle inbox page - navigate to spam folder
        """
        self.logger.info("Detected inbox page - navigating to Spam folder")
        
        self.human_action.human_click(
            page,
            selectors=['button.sidebar-folder-icon-spam'],
            deep_search=True
        )
        
        self.logger.info("Clicked Spam folder")
        page.wait_for_timeout(2000)
        
        return "gmx_spam"

    def handle_spam_page(self, page: Page) -> str:
        """
        Handle spam page - search for email and report not spam
        """
        self.logger.info(f"Detected spam page - searching for email with text: {self.search_text}")
        
        # Keep processing emails until no more matches are found
        while True:
            # Wait for list to load
            try:
                self.human_action._find_element_with_humanization(page, ["div.list-mail-list"], deep_search=True)
            except:
                self.logger.warning("Mail list not found, might be empty or loading issue")
            
            # Find all email items using deep search (fresh scan each time)
            email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
            
            found_match = False
            
            for item in email_items:
                # Check text in subject/preview
                # Selector: div.list-mail-item__lines-container > div.list-mail-item__second-line > div
                try:
                    subject_div = item.query_selector("div.list-mail-item__lines-container > div.list-mail-item__second-line > div")
                    
                    if subject_div:
                        text = subject_div.inner_text()
                        if self.search_text.lower() in text.lower():
                            self.logger.info(f"Found matching email: {text}")
                            
                            # Extract email ID (e.g., from id="id1764755051039737362")
                            email_id_attr = item.get_attribute("id")
                            if email_id_attr and email_id_attr.startswith("id"):
                                # Extract numeric part (e.g., "1764755051039737362")
                                email_id_number = email_id_attr[2:]  # Remove "id" prefix
                                self.reported_email_ids.append(email_id_number)
                                self.logger.info(f"Stored email ID: {email_id_number}")
                            
                            # Click to open (simulate human behavior)
                            self.human_action.human_behavior.click(item)
                            
                            # Simulate reading
                            self.logger.info("Simulating reading...")
                            self.human_action.human_behavior.scroll_into_view(item)
                            
                            # Click "Not Spam" button
                            self.logger.info("Clicking 'Not Spam' button")
                            self.human_action.human_click(
                                page,
                                selectors=['div.list-toolbar__scroll-item section[data-overflow-id="no_spam"] button'],
                                deep_search=True
                            )
                            
                            self.logger.info("Reported as not spam")
                            found_match = True
                            
                            # Wait for action to complete/list to update
                            page.wait_for_timeout(2000)
                            break  # Exit inner loop to re-scan
                except Exception as e:
                    self.logger.warning(f"Error processing item (likely detached): {e}")
                    continue  # Skip to next item
            
            # If no match found in this scan, check pagination or finish
            if not found_match:
                # Check pagination
                next_buttons = deep_find_elements(page, "div.list-paging-footer__right > button.list-paging-footer__page-next")
                
                if next_buttons:
                    next_btn = next_buttons[0]
                    # Check if disabled
                    is_disabled = next_btn.get_attribute("disabled") is not None or "disabled" in next_btn.get_attribute("class")
                    
                    if not is_disabled:
                        self.logger.info("Clicking next page")
                        self.human_action.human_behavior.click(next_btn)
                        page.wait_for_timeout(2000)
                        continue  # Continue outer loop to scan next page
                
                # No match and no next page (or disabled)
                self.logger.info("No more matching emails found")
                break  # Exit while loop
        
        # After all spam processing is done, open reported emails
        if len(self.reported_email_ids) > 0:
            self.logger.info(f"Opening {len(self.reported_email_ids)} reported emails in inbox")
            
            # Navigate to inbox
            self.human_action.human_click(page, selectors=['button.sidebar-folder-icon-inbox'], deep_search=True)
            page.wait_for_timeout(2000)
            
            # Open each reported email directly
            for email_id_number in self.reported_email_ids:
                self.logger.info(f"Processing email ID: {email_id_number}")
                
                # Click the first email to load the iframe
                self.human_action.human_click(page, selectors=[f'div.list-mail-item__lines-container > div.list-mail-item__second-line > div:has-text("{email_id_number}")'], deep_search=True)
                page.wait_for_timeout(2000)

                try:
                    # Use deep_find_elements to find iframe inside shadow DOM
                    iframe_elements = deep_find_elements(page, 'iframe[name="detail-body-iframe"]')
                    
                    if not iframe_elements:
                        self.logger.warning("Iframe not found in shadow DOM")
                        continue
                    
                    iframe_element = iframe_elements[0]
                    
                    # Get current iframe src
                    current_src = iframe_element.get_attribute("src")
                    self.logger.info(f"Current iframe src: {current_src}")
                    
                    # Replace the email ID in the src
                    new_src = re.sub(r'tmai\d+', f'tmai{email_id_number}', current_src)
                    self.logger.info(f"New iframe src: {new_src}")
                    
                    # Set the new src to load the email
                    iframe_element.evaluate(f'element => element.src = "{new_src}"')
                    
                    # Wait for iframe to load
                    page.wait_for_timeout(3000)
                    
                    # Access iframe content
                    iframe = page.frame(name="detail-body-iframe")
                    if iframe:
                        # Dummy example: Click first link in the email
                        links = iframe.locator("a")
                        if links.count() > 0:
                            first_link = links.first
                            link_text = first_link.inner_text()
                            self.logger.info(f"Clicking link: {link_text}")
                            first_link.click()
                            page.wait_for_timeout(2000)
                        else:
                            self.logger.warning("No links found in email")
                    else:
                        self.logger.warning("Could not access iframe content")
                        
                except Exception as e:
                    self.logger.error(f"Error opening email {email_id_number}: {e}")
            
            self.logger.info("Finished opening all reported emails")
        
        # Mark as completed
        self.automation.action_completed = True
        return "task_completed"

    def handle_unknown_page(self, page: Page) -> str:
        """
        Handle unknown page - try to go to inbox or login
        """
        self.logger.warning("Unknown page detected")
        # Maybe try to go to inbox?
        page.goto("https://www.gmx.net/mail/client/inbox")
        return "gmx_inbox"