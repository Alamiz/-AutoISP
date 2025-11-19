PAGE_SIGNATURES = {
    "gmail_inbox": {
        "description": "Gmail Inbox page.",
        "required_sublink": "mail.google.com/mail",
        "checks": [
            {
                "name": "Check div role=navigation",
                "css_selector": "div[role=\"navigation\"]",
                "contains_text": "",
                "min_count": 1,
                "require_english": False,
                "description": "div with role navigation",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Anchor inbox",
                "css_selector": "a[href=\"#inbox\"]",
                "contains_text": "",
                "min_count": 1,
                "require_english": False,
                "description": "Inbox sidebar link",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Emails grid table",
                "css_selector": "table[role=\"grid\"]",
                "contains_text": "",
                "min_count": 1,
                "require_english": False,
                "description": "Main email list table",
                "weight": 1.0,
                "should_exist": True
            }
        ]
    },
    "gmx_login_page": {
        "description": "GMX Login page.",
        "required_sublink": "www.gmx.net",
        "checks": [
            {
                "name": "Check login iframe",
                "css_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "contains_text": "",
                "min_count": 1,
                "require_english": False,
                "description": "Login iframe exists",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Email input inside iframe",
                "css_selector": "form#login input#username",
                "iframe_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "contains_text": "",
                "min_count": 1,
                "require_english": False,
                "description": "Email input field inside login iframe",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Create account button",
                "css_selector": 'a[data-component="button"][href^="https://www.gmx.net/mail/tarifvergleich"]',
                "contains_text": "",
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
        ]
    },
    "gmx_logged_in_page": {
        "description": "GMX Confirm user page.",
        "required_sublink": "www.gmx.net",
        "checks": [
            {
                "name": "Check login iframe",
                "css_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "contains_text": "",
                "min_count": 1,
                "require_english": False,
                "description": "Login iframe",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'account-avatar-homepage[role="button"]',
                "contains_text": "",
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Continue button",
                "css_selector": "button[data-component-path='openInbox.continue-button']",
                "iframe_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "contains_text": "",
                "min_count": 1,
                "require_english": False,
                "description": "Button to confirm already authenticated user inside iframe.",
                "weight": 3.0,
                "should_exist": True
            },
            {
                "name": "Greeting user",
                "css_selector": "div.oi_customer span.oi_customer_greeting",
                "iframe_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "contains_text": "",
                "min_count": 1,
                "require_english": False,
                "description": "Logged in user greeting text.",
                "weight": 3.0,
                "should_exist": True
            },
            {
                "name": "Email input",
                "css_selector": "input#username",
                "iframe_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "contains_text": "",
                "require_english": False,
                "description": "Email input field inside login iframe",
                "weight": 2.0,
                "should_exist": False
            }
        ]
    }
}