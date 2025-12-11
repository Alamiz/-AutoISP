# automations/gmx/report_not_spam/mobile/steps.py
"""
Sequential steps for GMX Mobile Report Not Spam using SequentialFlow.
"""
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
        self.automation.human_click(
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
        return self.automation._find_element_with_humanization(
            page, ["div.message-list-panel__content"], deep_search=True
        )
    
    # Click to open email
    @retry_action(max_attempts=3, delay=0.5)
    def _click_email_link(self, page, email_link):
        self.automation.human_behavior.click(email_link)
    
    # Click back
    @retry_action(max_attempts=3, delay=1.0)
    def _click_back_button(self, page):
        self.automation.human_click(
            page,
            selectors=['div.toolbar > ul.toolbar__icon[data-position="left"] > li:nth-of-type(1)'],
        )
    
    # Click checkbox
    @retry_action(max_attempts=3, delay=1.0)
    def _click_checkbox(self, page, email_id):
        self.automation.human_click(
            page,
            selectors=[f'div.message-list-panel__content > li:has(a[href*="{email_id}"]) input[type="checkbox"]'],
        )
    
    # Click more actions button
    @retry_action(max_attempts=3, delay=1.0)
    def _click_more_actions(self, page):
        self.automation.human_click(
            page,
            selectors=['div.toolbar[aria-controls="mail-list"] > ul > li:nth-of-type(4)'],
        )
        
    # Click mark as unread
    @retry_action(max_attempts=3, delay=1.0)
    def _click_mark_as_unread(self, page):
        self.automation.human_click(
            page,
            selectors=['div.action-list > ul > li > a[href*="unread"]'],
        )

    # Click no spam button
    @retry_action(max_attempts=3, delay=1.0)
    def _click_no_spam(self, page):
        self.automation.human_click(
            page,
            selectors=['button[name="actions:noSpam"]'],
        )

    @retry_action(max_attempts=3, delay=1.0)
    def _click_mail_actions_button(self, page):
        self.automation.human_click(
            page,
            selectors=['ul.toolbar__icon[data-position="left"] > li > a[href*="mailactions"]'],
        )
    
    @retry_action(max_attempts=4, delay=1.0, backoff=1.5)
    def _click_not_spam_button(self, page):
        self.automation.human_click(
            page,
            selectors=['div.base-page__content div.action-list:nth-child(3) ul li > a[href*="noSpam"]'],
        )
    
    def run(self, page: Page) -> StepResult:
        try:
            keyword = getattr(self.automation, "search_text", "")
            self.logger.info(f"Reporting emails with keyword: {keyword}")
            
            if not hasattr(self.automation, "reported_email_ids"):
                self.automation.reported_email_ids = []
            
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
                                    self.automation.reported_email_ids.append(email_id_number)
                                    self.logger.info(f"Stored email ID: {email_id_number}")
                            
                            self._click_email_link(page, email_link)
                            page.wait_for_timeout(1500)
                            
                            self.automation.human_behavior.scroll_page_by(page, 600)
                            
                            self._click_back_button(page)
                            page.wait_for_timeout(1000)
                            
                            self._click_checkbox(page, email_id_number)
                            page.wait_for_timeout(1000)
                            
                            self._click_more_actions(page)
                            page.wait_for_timeout(1000)
                            
                            self._click_mark_as_unread(page)
                            page.wait_for_timeout(1000)
                            
                            self._click_checkbox(page, email_id_number)
                            page.wait_for_timeout(1000)

                            self._click_no_spam(page)
                            page.wait_for_timeout(1000)
                            
                            self.logger.info("Reported as not spam")
                            page.wait_for_timeout(2000)
                            break
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to process email item: {e}")
                        continue
                
                if not found_match:
                    self.logger.info("No more matching emails found")
                    break
            
            total_reported = len(self.automation.reported_email_ids)
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
        self.automation.human_click(
            page, selectors=['div.message-list-panel__navigation-bar > ul > li[data-position="left"] > a']
        )
    
    @retry_action(max_attempts=3, delay=1.0)
    def _search_emails(self, page, keyword):
        self.automation.human_fill(page, selectors=['form.search-form input'], text=keyword)
        self.automation.human_click(page, selectors=['form.search-form button[type="submit"]'])
    
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
        
        self.automation.human_behavior.click(target_item)

        # Click link or image inside the email body iframe
        try:
            iframes = deep_find_elements(page, 'iframe#bodyIFrame')
            if iframes:
                iframe_element = iframes[0]
                content_frame = iframe_element.content_frame()
                if content_frame:
                    links = content_frame.query_selector_all("a")
                    if links:
                        self.automation.human_behavior.click(links[0])
                        self.logger.info(f"Clicked link inside email '{subject_text}'")
                        page.wait_for_timeout(3000)
                    else:
                        imgs = content_frame.query_selector_all("img")
                        if imgs:
                            self.automation.human_behavior.click(imgs[0])
                            self.logger.info(f"Clicked image inside email '{subject_text}'")
                            page.wait_for_timeout(3000)
                        else:
                            self.logger.info(f"No links or images found in iframe for email '{subject_text}'")
                else:
                    self.logger.warning(f"Could not get content frame for email '{subject_text}'")
            else:
                self.logger.warning(f"Iframe 'detail-body-iframe' not found for email '{subject_text}'")
        except Exception as click_iframe_e:
            self.logger.warning(f"Could not click link/img in email '{subject_text}': {click_iframe_e}")

    
    @retry_action(max_attempts=3, delay=0.5)
    def _click_back_to_list(self, page):
        self.automation.human_click(
            page, selectors=['ul.toolbar__icon[data-position="left"] > li:nth-of-type(1) > a']
        )
    
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Opening unread reported emails in inbox")
            
            self._click_back_button(page)
            page.wait_for_timeout(500)
            
            keyword = getattr(self.automation, "search_text", "")
            self._search_emails(page, keyword)
            page.wait_for_timeout(2000)
            
            opened_count = 0
            
            while True:
                # Find all email items in the list
                email_items = deep_find_elements(page, "div.message-list-panel__content > li")
                
                if not email_items:
                    self.logger.info("No emails found in list")
                    break
                
                found_unread_match = False
                
                for item in email_items:
                    try:
                        # Check if email is unread
                        class_attr = item.get_attribute("class") or ""
                        if "is-unread" not in class_attr:
                            continue

                        # Check subject match
                        subject_span = item.query_selector("a > span")
                        if not subject_span:
                            continue
                        
                        text = subject_span.inner_text()
                        if keyword.lower() not in text.lower():
                            continue
                            
                        self.logger.info(f"Found unread matching email: {text}")
                        found_unread_match = True
                        
                        # Click to open
                        email_link = item.query_selector("a.message-list__link")
                        if email_link:
                            self.automation.human_behavior.click(email_link)
                            self.logger.info("Opened email in inbox")
                            page.wait_for_timeout(2000)
                            
                            self.automation.human_behavior.scroll_into_view(page=page, y_amount=300)
                            
                            # Click link or image inside the email body iframe (mobile)
                            try:
                                iframes = deep_find_elements(page, 'iframe#bodyIFrame')
                                if iframes:
                                    content_frame = iframes[0].content_frame()
                                    if content_frame:
                                        links = content_frame.query_selector_all("a")
                                        if links:
                                            self.automation.human_behavior.click(links[0])
                                            self.logger.info("Clicked link inside email")
                                            page.wait_for_timeout(3000)
                                        else:
                                            imgs = content_frame.query_selector_all("img")
                                            if imgs:
                                                self.automation.human_behavior.click(imgs[0])
                                                self.logger.info("Clicked image inside email")
                                                page.wait_for_timeout(3000)
                            except Exception as e:
                                self.logger.warning(f"Could not click link/img in email: {e}")
                            
                            self._click_back_to_list(page)
                            self.logger.info("Clicked back button")
                            page.wait_for_timeout(2000)
                            
                            opened_count += 1
                            break # Break inner loop to refresh list
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to process email item: {e}")
                        continue
                
                if not found_unread_match:
                    self.logger.info("No more unread matching emails found")
                    break
            
            self.logger.info(f"Opened {opened_count} unread matching emails")
            
            if opened_count > 0:
                return StepResult(status=StepStatus.SUCCESS, message=f"Opened {opened_count} emails in inbox")
            
            return StepResult(status=StepStatus.SKIP, message="No unread matching emails found")
            
        except Exception as e:
            self.logger.error(f"Error opening reported emails: {e}")
            return StepResult(status=StepStatus.RETRY, message=f"Failed to open emails: {e}")