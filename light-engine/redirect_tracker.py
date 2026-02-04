from playwright.sync_api import sync_playwright
import sys

def run():
    with sync_playwright() as p:
        print("Launching browser...")
        # Use chromium and show UI so user can interact
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("-" * 50)
        print("REDIRECT TRACKER ACTIVE")
        print("-" * 50)

        # Track navigation requests and redirects
        def handle_request(request):
            if request.is_navigation_request():
                redirected_from = request.redirected_from
                if redirected_from:
                    print(f"[REDIRECT] From: {redirected_from.url}")
                    print(f"           To:   {request.url}")
                else:
                    print(f"[NAV START] {request.url}")

        def handle_framenavigated(frame):
            if frame == page.main_frame:
                print(f"[FRAME NAV] URL: {frame.url}")

        page.on("request", handle_request)
        page.on("framenavigated", handle_framenavigated)

        try:
            print("Navigating to web.de...")
            page.goto("https://www.web.de/")
            
            print("\nMonitoring active. Perform actions in the browser window.")
            print("All navigation hops and redirects will be printed below.")
            print("Close the browser window or press Ctrl+C to exit.\n")
            
            # Keep the browser open
            page.wait_for_timeout(3600000) # 1 hour timeout
            
        except Exception as e:
            if "Target closed" in str(e) or "Browser closed" in str(e):
                print("\nBrowser closed. Exiting...")
            else:
                print(f"\nError: {e}")
        except KeyboardInterrupt:
            print("\nStopped by user.")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
