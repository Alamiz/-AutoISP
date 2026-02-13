import time
from playwright.sync_api import Page
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements
from core.flow_engine.step import Step, StepResult
from modules.core.flow_state import FlowResult
from core.utils.retry_decorators import retry_action
from core.utils.date_utils import parse_german_mail_date


class NavigateToSpamStep(Step):
    """Navigate from folder list to spam folder."""

    @retry_action(max_attempts=3, delay=0.5)
    def _click_spam_folder(self, page):
        start_time = time.perf_counter()
        self.automation.human_click(
            page,
            selectors=['ul.sidebar__folder-list > li a[data-webdriver*="SPAM"]'],
            deep_search=True
        )
        duration = time.perf_counter() - start_time
        self.logger.info(f"Navigated to Spam folder: {duration:.2f} seconds", extra={"account_id": self.account.id})
    
    def run(self, page: Page) -> StepResult:
        try:
            self._click_spam_folder(page)
            page.wait_for_timeout(2000)
            return StepResult(status=FlowResult.SUCCESS)
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to navigate to Spam: {e}")

class ReportSpamEmailsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            keyword = (getattr(self.automation, "search_text", "") or "").lower()
            start_date = getattr(self.automation, "start_date") 
            end_date = getattr(self.automation, "end_date")     

            current_page = 1
            self.logger.info(
                f"Processing emails with keyword='{keyword}' "
                f"between {start_date} and {end_date}", 
                extra={"account_id": self.account.id}
            )


            while True:
                page.wait_for_selector("div.message-list-panel__content")
                page.wait_for_timeout(1000)
                email_items = page.query_selector_all("li.message-list__item")

                if not email_items:
                    self.logger.info("No emails found on this page", extra={"account_id": self.account.id})
                    break
                
                index = 0
                while index < len(email_items):
                    start_process = time.perf_counter()
                    try:
                        item = email_items[index]
                        
                        # --- Extract date from <list-date-label> ---
                        date_el = item.query_selector("dd.mail-header__date")
                        if not date_el:
                            self.logger.warning("Date element not found", extra={"account_id": self.account.id})
                            index += 1
                            continue
                        
                        date_title = date_el.get_attribute("title")
                        if not date_title:
                            self.logger.warning("Date title not found", extra={"account_id": self.account.id})
                            index += 1
                            continue

                        mail_date = parse_german_mail_date(date_title)

                        # --- Early stop: all next emails are older ---
                        if index == 0 and mail_date < start_date:
                            self.logger.info(
                                "First email older than start_date. Stopping pagination.",
                                extra={"account_id": self.account.id}
                            )
                            return self._final_result()

                        # --- Skip out-of-range ---
                        if mail_date > end_date:
                            index += 1
                            continue

                        if mail_date < start_date:
                            self.logger.warning(
                                f"mail date: {mail_date} is older than start_datetime: {start_date}, aborting",
                                extra={"account_id": self.account.id}
                            )
                            return self._final_result()

                        # --- Keyword check ---
                        subject_el = item.query_selector("dd.mail-header__subject")
                        if not subject_el:
                            self.logger.warning("Subject element not found", extra={"account_id": self.account.id})
                            index += 1
                            continue
                        
                        subject_text = (subject_el.inner_text() or "").lower()

                        if keyword not in subject_text:
                            index += 1
                            continue
                        
                        self.logger.info(
                            f"Processing email '{subject_text}' @ {mail_date}",
                            extra={"account_id": self.account.id}
                        )

                        # --- Open email ---
                        self.click_email_item(item)
                        # --- Scroll content ---
                        self.scroll_content(page)

                        # --- Report as not spam ---
                        self.click_not_spam(page)

                        # Re-query after DOM change
                        page.wait_for_selector("div.message-list-panel__content")
                        page.wait_for_timeout(1000)
                        email_items = page.query_selector_all("li.message-list__item")
                        self.logger.info(
                            f"Re-queried email items: {len(email_items)}",
                            extra={"account_id": self.account.id}
                        )
                        
                        duration = time.perf_counter() - start_process
                        self.logger.info(f"Email processed in {duration:.2f} seconds \n\n", extra={"account_id": self.account.id})

                        # DON'T increment index - reprocess same position with new list
                        # continue without index += 1

                    except Exception as e:
                        self.logger.warning(
                            f"Failed processing email: {e}",
                            extra={"account_id": self.account.id}
                        )
                        index += 1
                        continue

                # --- Next page ---
                try:
                    next_button = self.automation._find_element_with_humanization(
                        page,
                        ["ul.paging-toolbar li[data-position='right'] > a[href*='messagelist']"]
                    )
                    if next_button:
                        self.automation.human_behavior.click(next_button)
                        current_page += 1
                        continue
                    break
                except Exception as e:
                    self.logger.warning(
                        f"Pagination failed: {e}",
                        extra={"account_id": self.account.id}
                    )
                    break

            return self._final_result()

        except Exception as e:
            return StepResult(
                status=FlowResult.RETRY,
                message=f"Failed to report emails: {e}"
            )
    
    @retry_action()
    def click_email_item(self, item):
        try:
            start_time = time.perf_counter()
            self.automation.human_behavior.click(item)
            duration = time.perf_counter() - start_time
            self.logger.info(f"Email item clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Failed to click email item: {e}",
                extra={"account_id": self.account.id}
            )

    @retry_action()
    def mark_email_unread(self, item, page):
        try:
            start_time = time.perf_counter()
            self.automation.human_behavior.hover(item)
            self.automation.human_click(
                page,
                selectors=["button.list-mail-item__read"],
                deep_search=True
            )
            duration = time.perf_counter() - start_time
            self.logger.info(f"Email marked unread: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Failed to mark email unread: {e}",
                extra={"account_id": self.account.id}
            )
    
    @retry_action()
    def scroll_content(self, page: Page):
        try:
            start_time = time.perf_counter()
            iframe = self.automation._find_element_with_humanization(
                page,
                selectors=['iframe#bodyIFrame']
            )
            # iframe is an ElementHandle, call content_frame() directly
            frame = iframe.content_frame()
            body = self.automation._find_element_with_humanization(
                frame, ["body"]
            )
            self.automation.human_behavior.scroll_into_view(body)
            duration = time.perf_counter() - start_time
            self.logger.info(f"Content scrolled: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Failed to scroll content: {e}",
                extra={"account_id": self.account.id}
            )
    
    @retry_action()
    def click_not_spam(self, page: Page):
        try:
            start_time = time.perf_counter()
            self.automation.human_click(
                page,
                selectors=[
                    'a[href*="mailactions"]'
                ]
            )
            page.wait_for_timeout(750)

            self.automation.human_click(
                page,
                selectors=[
                    'a[href*="noSpam"]'
                ]
            )
            duration = time.perf_counter() - start_time
            self.logger.info(f"Not spam clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Failed to click not spam: {e}",
                extra={"account_id": self.account.id}
            )
    
    def _final_result(self) -> StepResult:
        if getattr(self.automation, "reported_email_ids", []):
            return StepResult(
                status=FlowResult.SUCCESS,
                message="Emails reported within date range"
            )

        return StepResult(
            status=FlowResult.SKIP,
            message="No emails found within date range"
        )


class OpenReportedEmailsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            keyword = (getattr(self.automation, "search_text", "") or "").lower()
            start_dt = getattr(self.automation, "start_date")
            end_dt = getattr(self.automation, "end_date")

            self.logger.info(
                f"Opening emails with keyword='{keyword}' "
                f"between {start_dt} and {end_dt}",
                extra={"account_id": self.account.id}
            )

            # Navigate to inbox
            self._navigate_to_inbox(page)

            if not hasattr(self.automation, "pending_closures"):
                self.automation.pending_closures = []

            found_any = False
            current_page = 1

            while True:
                page.wait_for_selector("div.message-list-panel__content")

                email_items = page.query_selector_all("li.message-list__item")

                if not email_items:
                    self.logger.warning(
                        "No emails found on this page",
                        extra={"account_id": self.account.id}
                    )
                    break
                
                index = 0
                while index < len(email_items):
                    self._cleanup_pending_pages()
                    start_process = time.perf_counter()
                    try:
                        item = email_items[index]

                        index += 1
                        
                        email_subject_el = item.query_selector("dd.mail-header__subject")
                        if not email_subject_el:
                            continue
                        email_subject = email_subject_el.text_content().strip().lower()

                        # --- Extract date from date element title ---
                        date_el = item.query_selector("dd.mail-header__date")
                        if not date_el:
                            continue

                        date_title = date_el.get_attribute("title")
                        if not date_title:
                            continue

                        mail_date = parse_german_mail_date(date_title)
                        if not mail_date:
                            continue

                        # --- Early stop: everything else is older ---
                        if index == 0 and mail_date < start_dt:
                            self.logger.info(
                                "First email older than start_datetime. Stopping.",
                                extra={"account_id": self.account.id}
                            )
                            return self._final(found_any)

                        # --- Range filter ---
                        if mail_date > end_dt:
                            continue

                        if mail_date < start_dt:
                            self.logger.warning(f"mail date: {mail_date} is older than start_datetime: {start_dt}, aborting")
                            return self._final(found_any)

                        if keyword not in email_subject:
                            continue

                        found_any = True
                        self.logger.info(
                            f"Processing email '{email_subject[:10]}' @ {mail_date}",
                            extra={"account_id": self.account.id}
                        )

                        # Open email
                        self._click_email_item(item, page)

                        # Scroll content
                        frame = self._scroll_content(page)

                        # Click link or image
                        self._click_link_or_image(frame, page)

                        # Click back button
                        self._click_back_button(page)

                        duration = time.perf_counter() - start_process
                        self.logger.info(f"Email processed in {duration:.2f} seconds \n\n", extra={"account_id": self.account.id})

                        # Re-query after DOM change
                        page.wait_for_selector("div.message-list-panel__content")
                        page.wait_for_timeout(1000)
                        email_items = page.query_selector_all("li.message-list__item")
                        self.logger.info(
                            f"Re-queried {len(email_items)} emails",
                            extra={"account_id": self.account.id}
                        )

                    except Exception as e:
                        self.logger.warning(
                            f"Failed processing email: {e}",
                            extra={"account_id": self.account.id}
                        )
                        index += 1
                        continue


                # --- Pagination ---
                try:
                    next_button = self.automation._find_element_with_humanization(
                        page,
                        ["ul.paging-toolbar li[data-position='right'] > a[href*='messagelist']"]
                    )
                    if next_button:
                        self.automation.human_behavior.click(next_button)
                        current_page += 1
                        continue
                    break
                except Exception as e:
                    self.logger.warning(
                        f"Pagination failed: {e}",
                        extra={"account_id": self.account.id}
                    )
                    break

            # Final cleanup (gentle)
            self._cleanup_pending_pages(force=False)

            return self._final(found_any)

        except Exception as e:
            return StepResult(
                status=FlowResult.RETRY,
                message=f"Failed to open reported emails: {e}"
            )

    @retry_action()
    def _navigate_to_inbox(self, page):
        try:
            start_time = time.perf_counter()
            self.automation.human_click(
                page,
                selectors=["a[href*='folderlist']"],
            )
            page.wait_for_timeout(2000)

            self.automation.human_click(
                page,
                selectors=["ul.sidebar__folder-list li.sidebar__folder-list-item:nth-of-type(1)"],
            )
            duration = time.perf_counter() - start_time
            self.logger.info(f"Navigated to inbox: {duration:.2f} seconds", extra={"account_id": self.account.id})
            page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.warning(
                f"Failed to navigate to inbox: {e}",
                extra={"account_id": self.account.id}
            )

    @retry_action()
    def _click_email_item(self, item, page):
        try:
            start_time = time.perf_counter()
            self.automation.human_behavior.click(item)
            duration = time.perf_counter() - start_time
            self.logger.info(f"Email item clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
            page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.warning(
                f"Click inside email failed: {e}",
                extra={"account_id": self.account.id}
            )

    @retry_action()
    def _scroll_content(self, page):
        try:
            start_time = time.perf_counter()
            iframe = self.automation._find_element_with_humanization(
                page,
                selectors=["iframe#bodyIFrame"]
            )
            # iframe is an ElementHandle, call content_frame() directly
            frame = iframe.content_frame()
            body = self.automation._find_element_with_humanization(
                frame, ["body"]
            )
            self.automation.human_behavior.scroll_into_view(body)
            duration = time.perf_counter() - start_time
            self.logger.info(f"Content scrolled: {duration:.2f} seconds", extra={"account_id": self.account.id})

            return frame
        except Exception as e:
            self.logger.warning(
                f"Scroll content failed: {e}",
                extra={"account_id": self.account.id}
            )
    
    @retry_action()
    def _add_to_favorites(self, page):
        try:
            start_time = time.perf_counter()
            # Find and click the button
            button = self.automation._find_element_with_humanization(
                page,
                selectors=["button.detail-favorite-marker__unselected"],
                deep_search=True,
                timeout=2000
            )
            button.click()
            
            # Wait a moment for the DOM to update
            page.wait_for_timeout(500)
            
            # Verify the button now has the selected class
            selected_button = self.automation._find_element_with_humanization(
                page,
                selectors=["button.detail-favorite-marker__selected"],
                deep_search=True,
                timeout=2000
            )
            
            if not selected_button:
                raise Exception("Failed to verify favorite was added - selected class not found")
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Added to favorites: {duration:.2f} seconds", extra={"account_id": self.account.id})
                
        except Exception as e:
            self.logger.warning(f"Failed to add to favorites: {e}", extra={"account_id": self.account.id})
            raise  # Re-raise to trigger retry

    def _find_first_clickable(self, container):
        """Find the first visible and clickable link or image inside a container."""
        if not container:
            return None
        
        # Search for all links and images
        targets = container.query_selector_all("a, img")
        for target in targets:
            try:
                if target.is_visible():
                    box = target.bounding_box()
                    if box and box['width'] > 0 and box['height'] > 0:
                        return target
            except:
                continue
        return None

    def _cleanup_pending_pages(self, force=False):
        """Close pending pages that have been open for >30 seconds, or all if force=True."""
        if not hasattr(self.automation, "pending_closures"):
            return
            
        now = time.time()
        remaining = []
        for p, close_time in self.automation.pending_closures:
            if force or now >= close_time:
                try:
                    p.close()
                    self.logger.info("Pending tab closed successfully (Thread-safe)", extra={"account_id": self.account.id})
                except Exception as e:
                    self.logger.warning(f"Failed to close pending tab: {e}", extra={"account_id": self.account.id})
            else:
                remaining.append((p, close_time))
        self.automation.pending_closures = remaining

    @retry_action()
    def _click_link_or_image(self, frame, page):
        try:
            start_time = time.perf_counter()
            if frame:
                target = self._find_first_clickable(frame)

                if target:
                    try:
                        with page.context.expect_page(timeout=5000) as new_page_info:
                            # Use a shorter timeout for the click itself to avoid 30s hangs
                            self.automation.human_behavior.click(target, timeout=5000)
                        
                        new_page = new_page_info.value
                        self.logger.info("New tab opened, will close in 30s (Queue-based)", extra={"account_id": self.account.id})
                        
                        if not hasattr(self.automation, "pending_closures"):
                            self.automation.pending_closures = []
                        self.automation.pending_closures.append((new_page, time.time() + 30))
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to open new page from click: {e}", extra={"account_id": self.account.id})
                        # Fallback if no new page is opened (e.g. click failed or same tab navigation)
                        try:
                            self.automation.human_behavior.click(target, timeout=5000)
                            page.wait_for_timeout(3000)
                        except:
                            pass

            duration = time.perf_counter() - start_time
            self.logger.info(f"Link or image clicked (and started async close if tab): {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Click inside email failed: {e}",
                extra={"account_id": self.account.id}
            )
    
    @retry_action()
    def _click_back_button(self, page):
        try:
            start_time = time.perf_counter()
            self.automation.human_click(
                page,
                selectors=[
                    "a[href*='messagelist']"
                ]
            )
            duration = time.perf_counter() - start_time
            self.logger.info(f"Back button clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Click back button failed: {e}",
                extra={"account_id": self.account.id}
            )

    def _final(self, found: bool) -> StepResult:
        if found:
            return StepResult(
                status=FlowResult.SUCCESS,
                message="All matching emails in datetime range processed."
            )
        return StepResult(
            status=FlowResult.SKIP,
            message="No matching emails found in datetime range."
        )
