# automations/webde/report_not_spam/steps.py
from playwright.sync_api import Page
from core.utils.element_finder import deep_find_elements
from core.flow_engine.step import Step, StepResult, StepStatus

class NavigateToSpamStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Navigating to Spam folder")
            self.automation.human_click(
                page,
                selectors=['button.sidebar-folder-icon-spam'],
                deep_search=True
            )
            page.wait_for_timeout(2000)
            return StepResult(status=StepStatus.SUCCESS, message="Navigated to Spam folder")
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to navigate to Spam: {e}")


class ReportSpamEmailsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            keyword = getattr(self.automation, "search_text", "")
            self.logger.info(f"Reporting emails with keyword: {keyword}")

            # Track reported emails
            if not hasattr(self.automation, "reported_email_ids"):
                self.automation.reported_email_ids = []

            while True:
                try:
                    self.automation._find_element_with_humanization(page, ["div.list-mail-list"], deep_search=True)
                except:
                    self.logger.warning("Mail list not found, might be empty")

                email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
                if not email_items:
                    break

                found_match = False
                for item in email_items:
                    try:
                        subject = self.automation._find_element_with_humanization(item, ["div.list-mail-item__subject"])
                        if keyword.lower() in subject.inner_text().lower():
                            found_match = True
                            email_id_attr = item.get_attribute("id")
                            if email_id_attr and email_id_attr.startswith("id"):
                                email_id_number = email_id_attr[2:]
                                self.automation.reported_email_ids.append(email_id_number)
                                self.logger.info(f"Stored email ID: {email_id_number}")

                            # Click to open and report as not spam
                            self.automation.human_behavior.click(item)

                            # Mark as unread after opening
                            self.automation.human_behavior.hover(item)  
                            self.automation.human_click(
                                page,
                                selectors=['button.list-mail-item__read'],
                                deep_search=True
                            )

                            # Scroll to the bottom of the email content
                            email_content_body_iframe = self.automation._find_element_with_humanization(
                                page,
                                selectors=['iframe[name="detail-body-iframe"]'],
                                deep_search=True
                            )
                            email_content_body_frame = email_content_body_iframe.content_frame()
                            email_content_body = self.automation._find_element_with_humanization(email_content_body_frame, ["body"])
                            self.automation.human_behavior.scroll_into_view(email_content_body)

                            # Click on the report as not spam button
                            self.automation.human_click(
                                page,
                                selectors=['div.list-toolbar__scroll-item section[data-overflow-id="no_spam"] button'],
                                deep_search=True
                            )
                            page.wait_for_timeout(2000)
                            break
                    except Exception as e:
                        self.logger.warning(f"Error processing item: {e}")
                        continue

                if not found_match:
                    break

            if getattr(self.automation, "reported_email_ids", []):
                return StepResult(status=StepStatus.SUCCESS, message="Emails reported")

            return StepResult(status=StepStatus.SKIP, message="No emails reported")

        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to report emails: {e}")


class OpenReportedEmailsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            email_ids = getattr(self.automation, "reported_email_ids", [])
            self.logger.info(f"Opening {len(email_ids)} reported emails in inbox")

            # Navigate to inbox
            self.automation.human_click(page, selectors=['button.sidebar-folder-icon-inbox'], deep_search=True)
            page.wait_for_timeout(2000)

            # Search for emails
            keyword = getattr(self.automation, "search_text", "")

            # Fill search input
            self.automation.human_fill(
                page,
                selectors=['input.webmailer-mail-list-search-input__input'],
                text=keyword,
                deep_search=True
            )

            # Click search options button
            self.automation.human_click(
                page,
                selectors=['button.webmailer-mail-list-search-options__button'],
                deep_search=True
            )

            # Select inbox folder
            self.automation.human_select(
                page,
                selectors=['div.webmailer-mail-list-search-options__container select#folderSelect'],
                value='1709885902296757396',
                deep_search=True
            )

            # Click submit button
            self.automation.human_click(
                page,
                selectors=['div.webmailer-mail-list-search-options__container  button[type="submit"]'],
                deep_search=True
            )
            
            page.wait_for_timeout(2000)

            found_emails_to_process = False

            # Get all email items after search
            email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
            if not email_items:
                self.logger.info("No email items found after search.")
                return StepResult(status=StepStatus.SKIP, message="No emails found to open.")

            for item in email_items:
                try:
                    subject_element = self.automation._find_element_with_humanization(item, ["div.list-mail-item__subject"])
                    subject_text = subject_element.inner_text().lower()

                    # Check if the subject text contains the keyword and is visually "bold" (unread)
                    is_unread = "list-mail-item--unread" in item.get_attribute("class")

                    if keyword.lower() in subject_text and is_unread:
                        found_emails_to_process = True
                        self.logger.info(f"Processing unread email: {subject_text}")

                        # Click to open the email
                        self.automation.human_behavior.click(item)
                        page.wait_for_timeout(2000)
                        self.automation.human_behavior.scroll_into_view(item)
                        self.logger.info(f"Opened email with subject: {subject_text}")

                        # Click add to favorites
                        try:
                            self.automation.human_click(
                                page,
                                selectors=['button.detail-favorite-marker__unselected'],
                                deep_search=True,
                                timeout=5000
                            )
                            page.wait_for_timeout(2000)
                        except Exception as click_fav_e:
                            self.logger.warning(f"Could not click 'add to favorites' for email '{subject_text}': {click_fav_e}")

                        # Click link or image inside the email body iframe
                        try:
                            iframes = deep_find_elements(page, 'iframe[name="detail-body-iframe"]')
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

                except Exception as e:
                    self.logger.warning(f"Error processing email item: {e}")
                    continue

            if found_emails_to_process:
                return StepResult(status=StepStatus.SUCCESS, message="All matching unread emails processed.")
            else:
                return StepResult(status=StepStatus.SKIP, message="No matching unread emails found to process.")

        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to open reported emails: {e}")