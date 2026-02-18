import time
import asyncio
from core.utils.retry_decorators import retry_action
from playwright.async_api import Page, Locator
from core.utils.element_finder import deep_find_elements
from core.flow_engine.step import Step, StepResult
from modules.core.flow_state import FlowResult
from core.utils.date_utils import parse_mail_date
from datetime import datetime

class NavigateToSpamStep(Step):
    async def run(self, page: Page) -> StepResult:
        try:
            start_time = time.perf_counter()
            await self.automation.human_click(
                page,
                selectors=['button.sidebar-folder-icon-spam'],
                deep_search=True
            )
            duration = time.perf_counter() - start_time
            self.logger.info(f"Navigated to Spam folder: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            await page.wait_for_timeout(2000)
            return StepResult(status=FlowResult.SUCCESS, message="Navigated to Spam folder")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to navigate to Spam: {e}")

class ReportSpamEmailsStep(Step):
    async def run(self, page: Page) -> StepResult:
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

            if not hasattr(self.automation, "reported_email_ids"):
                self.automation.reported_email_ids = []

            while True:
                self.logger.info(f"Processing page {current_page}", extra={"account_id": self.account.id})

                email_items = await deep_find_elements(
                    page, "list-mail-item.list-mail-item--root"
                )

                if not email_items:
                    self.logger.info("No emails found on this page", extra={"account_id": self.account.id})
                    break

                index = 0

                while index < len(email_items):
                    start_process = time.perf_counter()
                    item = email_items[index]

                    try:
                        # --- Extract date ---
                        date_el = item.locator("list-date-label.list-mail-item__date")
                        if await date_el.count() == 0:
                            self.logger.warning("No date found on this email", extra={"account_id": self.account.id})
                            index += 1
                            continue

                        ms = await date_el.get_attribute("date-in-ms")
                        if not ms:
                            self.logger.warning("date-in-ms missing", extra={"account_id": self.account.id})
                            index += 1
                            continue

                        mail_date = datetime.fromtimestamp(
                            int(ms) / 1000
                        ).date()

                        # --- Early stop: first email already older ---
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
                            return self._final_result()

                        # --- Keyword check ---
                        subject_el = item.locator("div.list-mail-item__subject")
                        if await subject_el.count() == 0:
                            index += 1
                            continue

                        subject_text = (await subject_el.inner_text() or "").lower()
                        if keyword not in subject_text:
                            index += 1
                            continue

                        self.logger.info(
                            f"Processing email subject='{subject_text[:15]}', date={mail_date}",
                            extra={"account_id": self.account.id}
                        )

                        # --- Open email ---
                        await self.click_email_item(item)

                        # --- Scroll content ---
                        await self.scroll_content(page)

                        # --- Report as not spam ---
                        await self.click_not_spam(page)

                        # DOM CHANGED → re-query + reset index
                        email_items = await deep_find_elements(
                            page, "list-mail-item.list-mail-item--root"
                        )
                        
                        duration = time.perf_counter() - start_process
                        self.logger.info(f"Email processed in {duration:.2f} seconds \n\n", extra={"account_id": self.account.id})

                        index = 0
                        continue

                    except Exception as e:
                        self.logger.warning(
                            f"Failed processing email: {e}",
                            extra={"account_id": self.account.id}
                        )
                        index += 1
                        continue

                # --- Next page ---
                try:
                    next_button = await self.automation._find_element_with_humanization(
                        page,
                        ["button.list-paging-footer__page-next"],
                        deep_search=True
                    )
                    
                    if next_button:
                        # Handle both Locator and ElementHandle
                        is_disabled = await next_button.is_disabled()
                        if not is_disabled:
                            await self.automation.human_behavior.click(next_button)
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
    async def click_email_item(self, item):
        try:
            start_time = time.perf_counter()
            await self.automation.human_behavior.click(item)
            duration = time.perf_counter() - start_time
            self.logger.info(f"Email item clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Failed to click email item: {e}",
                extra={"account_id": self.account.id}
            )

    @retry_action()
    async def scroll_content(self, page: Page):
        try:
            start_time = time.perf_counter()
            iframe = await self.automation._find_element_with_humanization(
                page,
                selectors=['iframe[name="detail-body-iframe"]'],
                deep_search=True
            )
            # iframe is a Locator, we need ElementHandle to call content_frame()
            if isinstance(iframe, Locator):
                element_handle = await iframe.element_handle()
                frame = await element_handle.content_frame()
            else:
                 frame = await iframe.content_frame()

            body = await self.automation._find_element_with_humanization(
                frame, ["body"]
            )
            await self.automation.human_behavior.scroll_into_view(body)
            duration = time.perf_counter() - start_time
            self.logger.info(f"Content scrolled: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Failed to scroll content: {e}",
                extra={"account_id": self.account.id}
            )
    
    @retry_action()
    async def click_not_spam(self, page: Page):
        try:
            start_time = time.perf_counter()
            await self.automation.human_click(
                page,
                selectors=[
                    'div.list-toolbar__scroll-item '
                    'section[data-overflow-id="no_spam"] button'
                ],
                deep_search=True
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
    async def run(self, page: Page) -> StepResult:
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
            await self._navigate_to_inbox(page)

            # Fill search input
            await self._fill_search_input(page, keyword)

            # Open search options
            await self.open_search_options(page)
 
            # Select inbox and submit search
            await self.select_inbox_and_submit(page)

            if not hasattr(self.automation, "pending_closures"):
                self.automation.pending_closures = []

            found_any = False
            current_page = 1

            while True:
                self.logger.info(f"Processing page {current_page}", extra={"account_id": self.account.id})

                email_items = await deep_find_elements(
                    page, "list-mail-item.list-mail-item--root"
                )

                if not email_items:
                    self.logger.warning("No emails found on this page", extra={"account_id": self.account.id})
                    break

                index = 0
                while index < len(email_items):
                    await self._cleanup_pending_pages()
                    start_process = time.perf_counter()
                    item = email_items[index]

                    try:
                        fav_button = item.locator("list-favorite-marker.list-mail-item__fav[selected]")
                        if await fav_button.count() > 0:
                            index += 1
                            continue

                        # --- Extract datetime from date-in-ms ---
                        date_el = item.locator("list-date-label.list-mail-item__date")
                        if await date_el.count() == 0:
                            self.logger.warning("No date found on this email", extra={"account_id": self.account.id})
                            index += 1
                            continue

                        ms = await date_el.get_attribute("date-in-ms")
                        if not ms:
                            self.logger.warning("No date-in-ms found on this email", extra={"account_id": self.account.id})
                            index += 1
                            continue

                        mail_dt = datetime.fromtimestamp(
                            int(ms) / 1000
                        ).date()

                        # --- Early stop: everything else is older ---
                        if index == 0 and mail_dt < start_dt:
                            self.logger.info("First email older than start_datetime. Stopping.", extra={"account_id": self.account.id})
                            return self._final(found_any)

                        # --- Range filter ---
                        if mail_dt > end_dt:
                            self.logger.warning(f"mail date: {mail_dt} is newer than end_datetime: {end_dt}, skipping", extra={"account_id": self.account.id})
                            index += 1
                            continue

                        if mail_dt < start_dt:
                            self.logger.warning(f"mail date: {mail_dt} is older than start_datetime: {start_dt}, stopping", extra={"account_id": self.account.id})
                            return self._final(found_any)

                        # --- Subject ---
                        subject_el = item.locator("div.list-mail-item__subject")
                        if await subject_el.count() == 0:
                            self.logger.warning("No subject found on this email", extra={"account_id": self.account.id})
                            index += 1
                            continue

                        subject_text = (await subject_el.get_attribute("title") or "").lower()

                        if keyword not in subject_text:
                            index += 1
                            continue

                        found_any = True

                        self.logger.info(f"Processing email {subject_text[:10]}... @ {mail_dt}", extra={"account_id": self.account.id})

                        # --- Actions ---
                        await self._click_email_item(item, page)

                        frame = await self._scroll_content(page)

                        await self._add_to_favorites(page)

                        await self._scroll_to_top(frame)

                        await self._click_link_or_image(frame, page)

                        duration = time.perf_counter() - start_process
                        self.logger.info(f"Email processed in {duration:.2f} seconds \n\n", extra={"account_id": self.account.id})

                        # Re-query for safety (DOM not reordered)
                        email_items = await deep_find_elements(
                            page, "list-mail-item.list-mail-item--root"
                        )

                        index += 1
                        continue

                    except Exception as e:
                        self.logger.warning(f"Failed processing email: {e}", extra={"account_id": self.account.id})
                        index += 1
                        continue

                # --- Pagination ---
                try:
                    next_button = await self.automation._find_element_with_humanization(
                        page,
                        ["button.list-paging-footer__page-next"],
                        deep_search=True
                    )
                    
                    if next_button:
                        is_disabled = await next_button.is_disabled()
                        if not is_disabled:
                            await self.automation.human_behavior.click(next_button)
                            await page.wait_for_timeout(2000)
                            current_page += 1
                            continue
                    break
                except Exception:
                    break

            # Final cleanup (gentle)
            await self._cleanup_pending_pages(force=False)

            return self._final(found_any)

        except Exception as e:
            return StepResult(
                status=FlowResult.RETRY,
                message=f"Failed to open reported emails: {e}"
            )

    @retry_action()
    async def _navigate_to_inbox(self, page):
        try:
            start_time = time.perf_counter()
            await self.automation.human_click(
                page,
                selectors=["button.sidebar-folder-icon-inbox"],
                deep_search=True
            )
            duration = time.perf_counter() - start_time
            self.logger.info(f"Navigated to inbox: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(f"Failed to navigate to inbox: {e}", extra={"account_id": self.account.id})

    @retry_action()
    async def _fill_search_input(self, page, keyword):
        try:
            start_time = time.perf_counter()
            search_input = await deep_find_elements(
                page,
                css_selector="input.webmailer-mail-list-search-input__input",
            )
            if search_input:
                await search_input[0].fill(keyword)
            duration = time.perf_counter() - start_time
            self.logger.info(f"Search input filled: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(f"Failed to fill search input: {e}", extra={"account_id": self.account.id})
    
    @retry_action()
    async def open_search_options(self, page):
        try:
            start_time = time.perf_counter()
            await self.automation.human_click(
                page,
                selectors=["button.webmailer-mail-list-search-options__button"],
                deep_search=True
            )
            duration = time.perf_counter() - start_time
            self.logger.info(f"Search options opened: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(f"Failed to open search options: {e}", extra={"account_id": self.account.id})
    
    @retry_action()
    async def select_inbox_and_submit(self, page):
        try:
            start_time = time.perf_counter()
            # Select inbox
            await self.automation.human_select(
                page,
                selectors=[
                    "div.webmailer-mail-list-search-options__container select#folderSelect"
                ],
                label="Posteingang",
                deep_search=True
            )

            # Submit search
            await self.automation.human_click(
                page,
                selectors=[
                    "div.webmailer-mail-list-search-options__container button[type='submit']"
                ],
                deep_search=True
            )
            duration = time.perf_counter() - start_time
            self.logger.info(f"Inbox selected and search submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})

            await page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.warning(f"Failed to select inbox and submit search: {e}", extra={"account_id": self.account.id})

    @retry_action()
    async def _click_email_item(self, item, page):
        try:
            start_time = time.perf_counter()
            await self.automation.human_behavior.click(item)
            duration = time.perf_counter() - start_time
            self.logger.info(f"Email item clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
            await page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.warning(f"Click inside email failed: {e}", extra={"account_id": self.account.id})

    @retry_action()
    async def _scroll_content(self, page):
        try:
            start_time = time.perf_counter()
            iframe = await self.automation._find_element_with_humanization(
                page,
                selectors=["iframe[name='detail-body-iframe']"],
                deep_search=True
            )
            
            # iframe is a Locator, we need ElementHandle to call content_frame()
            if isinstance(iframe, Locator):
                element_handle = await iframe.element_handle()
                frame = await element_handle.content_frame()
            else:
                 frame = await iframe.content_frame()

            body = await self.automation._find_element_with_humanization(
                frame, ["body"]
            )
            await self.automation.human_behavior.scroll_into_view(body)
            duration = time.perf_counter() - start_time
            self.logger.info(f"Content scrolled: {duration:.2f} seconds", extra={"account_id": self.account.id})

            return frame
        except Exception as e:
            self.logger.warning(f"Scroll content failed: {e}", extra={"account_id": self.account.id})
    
    async def _scroll_to_top(self, frame):
        try:
            start_time = time.perf_counter()
            body = await self.automation._find_element_with_humanization(
                frame, ["body"]
            )
            # Scroll the body to top
            await body.evaluate("element => element.scrollTop = 0")
            duration = time.perf_counter() - start_time
            self.logger.info(f"Scrolled to top: {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(f"Scroll to top failed: {e}", extra={"account_id": self.account.id})
    
    @retry_action()
    async def _add_to_favorites(self, page):
        try:
            start_time = time.perf_counter()
            # Find and click the button
            button = await self.automation._find_element_with_humanization(
                page,
                selectors=["button.detail-favorite-marker__unselected"],
                deep_search=True,
                timeout=2000
            )
            await button.click()
            
            # Wait a moment for the DOM to update
            await page.wait_for_timeout(500)
            
            # Verify the button now has the selected class
            selected_button = await self.automation._find_element_with_humanization(
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
    
    async def _find_first_clickable(self, container):
        """Find the first visible and clickable link or image inside a container."""
        if not container:
            return None
        
        # Search for all links and images
        targets = await container.query_selector_all("a, img")
        for target in targets:
            try:
                if await target.is_visible():
                    box = await target.bounding_box()
                    if box and box['width'] > 0 and box['height'] > 0:
                        return target
            except:
                continue
        return None

    async def _cleanup_pending_pages(self, force=False):
        """Close pending pages that have been open for >30 seconds, or all if force=True."""
        if not hasattr(self.automation, "pending_closures"):
            return
            
        now = time.time()
        remaining = []
        for p, close_time in self.automation.pending_closures:
            if force or now >= close_time:
                try:
                    await p.close()
                    self.logger.info("Pending tab closed successfully (Thread-safe)", extra={"account_id": self.account.id})
                except Exception as e:
                    self.logger.warning(f"Failed to close pending tab: {e}", extra={"account_id": self.account.id})
            else:
                remaining.append((p, close_time))
        self.automation.pending_closures = remaining

    @retry_action()
    async def _click_link_or_image(self, frame, page):
        try:
            start_time = time.perf_counter()
            if frame:
                target = await self._find_first_clickable(frame)

                if target:
                    try:
                        async with page.context.expect_page(timeout=5000) as new_page_info:
                            # Use a shorter timeout for the click itself to avoid 30s hangs
                            await self.automation.human_behavior.click(target, timeout=5000)
                        
                        new_page = await new_page_info.value
                        self.logger.info("New tab opened, will close in 30s (Queue-based)", extra={"account_id": self.account.id})
                        
                        if not hasattr(self.automation, "pending_closures"):
                            self.automation.pending_closures = []
                        self.automation.pending_closures.append((new_page, time.time() + 30))
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to open new page from click: {e}", extra={"account_id": self.account.id})
                        # Fallback if no new page is opened (e.g. click failed or same tab navigation)
                        try:
                            await self.automation.human_behavior.click(target, timeout=5000)
                            await page.wait_for_timeout(3000)
                        except:
                            pass

            duration = time.perf_counter() - start_time
            self.logger.info(f"Link or image clicked (and started async close if tab): {duration:.2f} seconds", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(f"Click inside email failed: {e}", extra={"account_id": self.account.id})

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