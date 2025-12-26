from playwright.sync_api import Page
from core.utils.element_finder import deep_find_elements
from core.flow_engine.step import Step, StepResult, StepStatus
from core.utils.date_utils import parse_mail_date

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
            keyword = getattr(self.automation, "search_text", "").lower()
            start_date = getattr(self.automation, "start_date")  # datetime.date
            end_date = getattr(self.automation, "end_date")      # datetime.date

            current_page = 1
            self.logger.info(
                f"Processing emails with keyword='{keyword}' "
                f"between {start_date} and {end_date}"
            )

            if not hasattr(self.automation, "reported_email_ids"):
                self.automation.reported_email_ids = []

            while True:
                self.logger.info(f"Processing page {current_page}")

                email_items = deep_find_elements(
                    page, "list-mail-item.list-mail-item--root"
                )

                if not email_items:
                    self.logger.info("No emails found on this page")
                    break

                stop_processing = False

                for index, item in enumerate(email_items):
                    try:
                        # --- Extract date ---
                        date_el = self.automation._find_element_with_humanization(
                            item,
                            ["span.list-date-label.list-mail-item__date"],
                            deep_search=True
                        )
                        mail_date = parse_mail_date(date_el.get_attribute("title"))

                        # --- Early exit optimization ---
                        if index == 0 and mail_date < start_date:
                            self.logger.info(
                                "First email is older than start_date. "
                                "No emails left in date range."
                            )
                            stop_processing = True
                            break

                        # --- Skip out-of-range ---
                        if mail_date > end_date:
                            continue

                        if mail_date < start_date:
                            stop_processing = True
                            break

                        # --- Keyword check ---
                        subject_el = self.automation._find_element_with_humanization(
                            item, ["div.list-mail-item__subject"]
                        )
                        subject_text = subject_el.inner_text().lower()

                        if keyword not in subject_text:
                            continue

                        # --- Store email ID ---
                        email_id_attr = item.get_attribute("id")
                        if email_id_attr and email_id_attr.startswith("id"):
                            email_id_number = email_id_attr[2:]
                            self.automation.reported_email_ids.append(email_id_number)
                            self.logger.info(
                                f"Processing email ID={email_id_number}, date={mail_date}"
                            )

                        # --- Open email ---
                        self.automation.human_behavior.click(item)

                        # --- Mark unread ---
                        self.automation.human_behavior.hover(item)
                        self.automation.human_click(
                            page,
                            selectors=['button.list-mail-item__read'],
                            deep_search=True
                        )

                        # --- Scroll content ---
                        iframe = self.automation._find_element_with_humanization(
                            page,
                            selectors=['iframe[name="detail-body-iframe"]'],
                            deep_search=True
                        )
                        frame = iframe.content_frame()
                        body = self.automation._find_element_with_humanization(
                            frame, ["body"]
                        )
                        self.automation.human_behavior.scroll_into_view(body)

                        # --- Report not spam ---
                        self.automation.human_click(
                            page,
                            selectors=[
                                'div.list-toolbar__scroll-item '
                                'section[data-overflow-id="no_spam"] button'
                            ],
                            deep_search=True
                        )

                    except Exception as e:
                        self.logger.warning(f"Failed processing email: {e}")
                        continue

                if stop_processing:
                    break

                # --- Pagination ---
                try:
                    next_button = self.automation._find_element_with_humanization(
                        page,
                        ["button.list-paging-footer__page-next"],
                        deep_search=True
                    )
                    if next_button and not next_button.is_disabled():
                        self.automation.human_behavior.click(next_button)
                        current_page += 1
                        continue
                    break
                except Exception as e:
                    self.logger.warning(f"Pagination failed: {e}")
                    break

            if self.automation.reported_email_ids:
                return StepResult(
                    status=StepStatus.SUCCESS,
                    message="Emails reported within date range"
                )

            return StepResult(
                status=StepStatus.SKIP,
                message="No emails found within date range"
            )

        except Exception as e:
            return StepResult(
                status=StepStatus.RETRY,
                message=f"Failed to report emails: {e}"
            )

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
                label='Posteingang',
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
            current_page = 1

            while True:
                self.logger.info(f"Processing page {current_page}")
                
                # Process emails one by one, re-querying each time
                processed_on_this_page = 0
                
                while True:
                    # Re-query email items each time to avoid stale references
                    email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
                    if not email_items:
                        self.logger.info("No email items found on this page.")
                        break

                    # Find first unprocessed matching email
                    found_match = False
                    for item in email_items:
                        try:
                            subject_element = self.automation._find_element_with_humanization(item, ["div.list-mail-item__subject"])
                            subject_text = subject_element.inner_text().lower()

                            # Check if the subject contains the keyword and is unread
                            is_unread = "list-mail-item--unread" in item.get_attribute("class")

                            if keyword.lower() in subject_text and is_unread:
                                found_emails_to_process = True
                                found_match = True
                                self.logger.info(f"Processing unread email: {subject_text}")

                                # Open email
                                self.automation.human_behavior.click(item)
                                page.wait_for_timeout(1000)
                                
                                # Scroll email content
                                email_content_body_iframe = self.automation._find_element_with_humanization(
                                    page,
                                    selectors=['iframe[name="detail-body-iframe"]'],
                                    deep_search=True
                                )
                                email_content_body_frame = email_content_body_iframe.content_frame()
                                email_content_body = self.automation._find_element_with_humanization(email_content_body_frame, ["body"])
                                self.automation.human_behavior.scroll_into_view(email_content_body)

                                # Add to favorites
                                try:
                                    self.automation.human_click(
                                        page,
                                        selectors=['button.detail-favorite-marker__unselected'],
                                        deep_search=True,
                                        timeout=5000
                                    )
                                except Exception as click_fav_e:
                                    self.logger.warning(f"Could not click 'add to favorites' for email '{subject_text}': {click_fav_e}")

                                # Click link or image inside iframe
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

                                processed_on_this_page += 1
                                # Break to re-query the list since clicking changed the DOM
                                break

                        except Exception as e:
                            self.logger.warning(f"Error processing email item: {e}")
                            continue
                    
                    # If no matching email found, we're done with this page
                    if not found_match:
                        self.logger.info(f"Processed {processed_on_this_page} emails on page {current_page}")
                        break

                # Check if next page button exists and is enabled
                try:
                    next_button = self.automation._find_element_with_humanization(page, ["button.list-paging-footer__page-next"], deep_search=True)
                    if next_button and not next_button.is_disabled():
                        self.logger.info("Going to next page of emails")
                        
                        # Get reference to first item on current page to detect when it's gone
                        old_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
                        first_old_item = old_items[0] if old_items else None
                        
                        self.automation.human_behavior.click(next_button)
                        
                        # Wait for the old items to be detached from DOM
                        if first_old_item:
                            try:
                                page.wait_for_function(
                                    "(element) => !document.body.contains(element)",
                                    first_old_item,
                                    timeout=5000
                                )
                            except Exception:
                                self.logger.warning("Timeout waiting for old items to detach")
                        
                        # Wait for new items to load
                        page.wait_for_timeout(2000)
                        current_page += 1
                        continue
                    else:
                        self.logger.info("No more pages or next button disabled")
                        break
                except Exception as e:
                    self.logger.warning(f"Failed to navigate to next page: {e}")
                    break

            if found_emails_to_process:
                return StepResult(status=StepStatus.SUCCESS, message="All matching unread emails processed.")
            else:
                return StepResult(status=StepStatus.SKIP, message="No matching unread emails found to process.")

        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to open reported emails: {e}")
