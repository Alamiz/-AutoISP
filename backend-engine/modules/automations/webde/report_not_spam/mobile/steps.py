# automations/webde/report_not_spam/mobile/steps.py
import logging
from playwright.sync_api import Page
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements
from core.flow_engine.step import Step, StepResult, StepStatus
from core.utils.retry_decorators import retry_action


class NavigateToSpamStep(Step):
    """Navigate from folder list to spam folder."""
    max_retries = 3
    
    @retry_action(max_attempts=3, delay=0.5)
    def _click_spam_folder(self, page):
        self.human.human_click(
            page,
            selectors=['ul.sidebar__folder-list > li a[data-webdriver*="SPAM"]'],
            deep_search=True
        )
    
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Navigating to Spam folder")
            self._click_spam_folder(page)
            page.wait_for_timeout(2000)
            return StepResult(status=StepStatus.SUCCESS)
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to navigate to Spam: {e}")


class ReportSpamEmailsStep(Step):
    """Reports spam emails and stores their IDs."""
    max_retries = 2
    
    @retry_action(max_attempts=3, delay=1.0)
    def _wait_for_message_list(self, page):
        return self.human._find_element_with_humanization(
            page, ["div.message-list-panel__content"], deep_search=True
        )
    
    @retry_action(max_attempts=3, delay=0.5)
    def _click_email_link(self, page, email_link):
        self.human.human_behavior.click(email_link)
    
    @retry_action(max_attempts=3, delay=1.0)
    def _click_mail_actions_button(self, page):
        self.human.human_click(
            page,
            selectors=['ul.toolbar__icon[data-position="left"] > li > a[href*="mailactions"]'],
            deep_search=True
        )
    
    @retry_action(max_attempts=4, delay=1.0, backoff=1.5)
    def _click_not_spam_button(self, page):
        self.human.human_click(
            page,
            selectors=['div.base-page__content div.action-list:nth-child(3) ul li > a[href*="noSpam"]'],
            deep_search=True
        )
    
    def run(self, page: Page) -> StepResult:
        try:
            keyword = getattr(self.human, "search_text", "")
            self.logger.info(f"Reporting emails with keyword: {keyword}")
            
            if not hasattr(self.human, "reported_email_ids"):
                self.human.reported_email_ids = []
            
            while True:
                try:
                    self._wait_for_message_list(page)
                except Exception:
                    self.logger.warning("Message list not found, might be empty")
                    break
                
                email_items = deep_find_elements(page, "div.message-list-panel__content > li")
                
                if not email_items:
                    self.logger.info("No more emails found in list")
                    break
                
                found_match = False
                
                for item in email_items:
                    try:
                        subject_span = item.query_selector("a > span")
                        if not subject_span:
                            continue
                        
                        text = subject_span.inner_text()
                        
                        if keyword.lower() in text.lower():
                            self.logger.info(f"Found matching email: {text}")
                            found_match = True
                            
                            email_link = item.query_selector("a.message-list__link")
                            if email_link:
                                email_link_src = email_link.get_attribute("href")
                                if email_link_src and "mailId" in email_link_src:
                                    email_id_number = email_link_src.split("mailId=")[1]
                                    self.human.reported_email_ids.append(email_id_number)
                                    self.logger.info(f"Stored email ID: {email_id_number}")
                            
                            self._click_email_link(page, email_link)
                            page.wait_for_timeout(1500)
                            
                            self.human.human_behavior.scroll_page_by(page, 300)
                            
                            self._click_mail_actions_button(page)
                            page.wait_for_timeout(1000)
                            
                            self._click_not_spam_button(page)
                            
                            self.logger.info("Reported as not spam")
                            page.wait_for_timeout(2000)
                            break
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to process email item: {e}")
                        continue
                
                if not found_match:
                    self.logger.info("No more matching emails found")
                    break
            
            total_reported = len(self.human.reported_email_ids)
            self.logger.info(f"Completed: {total_reported} emails reported as not spam")
            
            if total_reported > 0:
                return StepResult(status=StepStatus.SUCCESS, message=f"Reported {total_reported} emails")
            
            return StepResult(status=StepStatus.SKIP, message="No matching emails found")
            
        except Exception as e:
            self.logger.error(f"Critical error in report step: {e}", exc_info=True)
            return StepResult(status=StepStatus.FAILURE, message=f"Critical failure: {e}")


class OpenReportedEmailsStep(Step):
    """Opens previously reported emails in inbox."""
    max_retries = 2
    
    @retry_action(max_attempts=3, delay=0.5)
    def _click_back_button(self, page):
        self.human.human_click(
            page, selectors=['div.message-list-panel__navigation-bar > ul > li[data-position="left"] > a']
        )
    
    @retry_action(max_attempts=3, delay=1.0)
    def _search_emails(self, page, keyword):
        self.human.human_fill(page, selectors=['form.search-form input'], text=keyword)
        self.human.human_click(page, selectors=['form.search-form button[type="submit"]'])
    
    @retry_action(max_attempts=3, delay=0.5)
    def _click_email_by_id(self, page, email_id_number):
        email_items = deep_find_elements(page, "div.message-list-panel__content > li")
        
        target_item = None
        for item in email_items:
            item_link = item.query_selector("a.message-list__link")
            if item_link:
                item_src = item_link.get_attribute("href")
                if email_id_number in item_src:
                    target_item = item
                    break
        
        if not target_item:
            raise Exception(f"Email with ID {email_id_number} not found")
        
        self.human.human_behavior.click(target_item)
    
    @retry_action(max_attempts=3, delay=0.5)
    def _click_back_to_list(self, page):
        self.human.human_click(
            page, selectors=['ul.toolbar__icon[data-position="left"] > li:nth-of-type(1) > a']
        )
    
    def run(self, page: Page) -> StepResult:
        try:
            email_ids = getattr(self.human, "reported_email_ids", [])
            
            if not email_ids:
                self.logger.warning("No email IDs to open")
                return StepResult(status=StepStatus.SKIP, message="No emails to open")
            
            self.logger.info(f"Opening {len(email_ids)} reported emails in inbox")
            
            self._click_back_button(page)
            page.wait_for_timeout(500)
            
            keyword = getattr(self.human, "search_text", "")
            self._search_emails(page, keyword)
            page.wait_for_timeout(2000)
            
            opened_count = 0
            
            for email_id_number in email_ids:
                try:
                    self.logger.info(f"Looking for email with ID: {email_id_number}")
                    
                    self._click_email_by_id(page, email_id_number)
                    self.logger.info("Opened email in inbox")
                    page.wait_for_timeout(2000)
                    
                    self.human.human_behavior.scroll_into_view(page=page, y_amount=300)
                    
                    # Click link or image inside the email body iframe (mobile)
                    try:
                        iframes = deep_find_elements(page, 'iframe#bodyIFrame')
                        if iframes:
                            content_frame = iframes[0].content_frame()
                            if content_frame:
                                links = content_frame.query_selector_all("a")
                                if links:
                                    self.human.human_behavior.click(links[0])
                                    self.logger.info("Clicked link inside email")
                                    page.wait_for_timeout(3000)
                                else:
                                    imgs = content_frame.query_selector_all("img")
                                    if imgs:
                                        self.human.human_behavior.click(imgs[0])
                                        self.logger.info("Clicked image inside email")
                                        page.wait_for_timeout(3000)
                    except Exception as e:
                        self.logger.warning(f"Could not click link/img in email: {e}")
                    
                    self._click_back_to_list(page)
                    page.wait_for_timeout(2000)
                    
                    opened_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to open email {email_id_number}: {e}")
                    continue
            
            self.logger.info(f"Opened {opened_count}/{len(email_ids)} emails")
            
            return StepResult(status=StepStatus.SUCCESS, message=f"Opened {opened_count} emails in inbox")
            
        except Exception as e:
            self.logger.error(f"Error opening reported emails: {e}")
            return StepResult(status=StepStatus.RETRY, message=f"Failed to open emails: {e}")
