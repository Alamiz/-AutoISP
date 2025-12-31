PAGE_SIGNATURES = {
    "gmx_login_page": {
        "description": "GMX Login page.",
        "required_sublink": "www.gmx.net",
        "checks": [
            {
                "name": "Check login iframe",
                "css_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Login iframe exists",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Email input inside iframe",
                "css_selector": "form#login input#username",
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Email input field inside login iframe",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Create account button",
                "css_selector": 'a[data-component="button"][href^="https://www.gmx.net/mail/tarifvergleich"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
        ]
    },
    "gmx_login_captcha_page": {
        "description": "GMX Login captcha page.",
        "required_sublink": "www.gmx.net",
        "checks": [
            {
                "name": "Captcha",
                "css_selector": "div[data-testid='captcha']",
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Captcha exists",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_login_wrong_username": {
        "description": "GMX Login wrong username page.",
        "required_sublink": "www.gmx.net",
        "checks": [
            {
                "name": "Check login iframe",
                "css_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Login iframe exists",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Email input inside iframe",
                "css_selector": "form#login input#username",
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Email input field inside login iframe",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Create account button",
                "css_selector": 'a[data-component="button"][href^="https://www.gmx.net/mail/tarifvergleich"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Error message",
                "css_selector": 'p[data-testid="error-email"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Wrong username error message",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_login_wrong_password": {
        "description": "GMX Login wrong password page.",
        "required_sublink": "www.gmx.net/logoutlounge/?status=login-failed",
        "checks": [
            {
                "name": "Error message",
                "css_selector": 'div[data-component="notification"][data-notification-type="error-light"][position="beforeLogin"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Wrong password error message",
                "weight": 4.0,
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
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Login iframe",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'account-avatar-homepage[role="button"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Continue button",
                "css_selector": "button[data-component-path='openInbox.continue-button']",
                # "iframe_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Button to confirm already authenticated user inside iframe.",
                "weight": 3.0,
                "should_exist": True
            },
            {
                "name": "Greeting user",
                "css_selector": "div.oi_customer span.oi_customer_greeting",
                # "iframe_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Logged in user greeting text.",
                "weight": 3.0,
                "should_exist": True
            },
            {
                "name": "Email input",
                "css_selector": "input#username",
                # "iframe_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "deep_search": True,
                "contains_text": None,
                "require_english": False,
                "description": "Email input field inside login iframe",
                "weight": 2.0,
                "should_exist": False
            }
        ]
    },
    "gmx_inbox_ads_preferences_popup_1_core": {
        "description": "GMX email ads preferences popup (core).",
        "required_sublink": "www.gmx.net",
        "checks": [
            # {
            #     "name": "Check inbox iframe",
            #     "css_selector": 'iframe[src*="gmx.net/mail/client"]',
            #     "contains_text": None,
            #     "min_count": 1,
            #     "require_english": False,
            #     "description": "Inbox iframe",
            #     "weight": 1.0,
            #     "should_exist": True
            # },
            # {
            #     "name": "Emails sidebar",
            #     "css_selector": 'webmailer-mail-sidebar#sidebar',
            #     "deep_search": True,
            #     "contains_text": None,
            #     "min_count": 1,
            #     "require_english": False,
            #     "description": "",
            #     "weight": 1.0,
            #     "should_exist": True
            # },
            # {
            #     "name": "User avatar",
            #     "css_selector": 'div.nav-header__icons > account-avatar-navigator',
            #     "contains_text": None,
            #     "min_count": 1,
            #     "require_english": False,
            #     "description": "",
            #     "weight": 1.0,
            #     "should_exist": True
            # },
            {
                "name": "Advertising core pop-up",
                "css_selector": 'iframe.permission-core-iframe',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_inbox_ads_preferences_popup_1": {
        "description": "GMX email ads preferences popup.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Advertising pop-up",
                "css_selector": 'iframe#thirdPartyFrame_permission_dialog',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_inbox_ads_preferences_popup_2": {
        "description": "GMX email ads preferences popup.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Advertising pop-up",
                "css_selector": 'iframe#thirdPartyFrame_upp_dialog[src*="navigator.gmx.net/upp-dialog"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Advertising popup deny button",
                "css_selector": 'button#deny',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Advertising popup accept button",
                "css_selector": 'button#cta',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
        ]
    },
    "gmx_inbox_smart_features_popup": {
        "description": "GMX email smart features popup.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Smart features pop-up",
                "css_selector": 'iframe#thirdPartyFrame_upp_dialog',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Smart features container iframe",
                "css_selector": 'iframe[src*="spl.gmx.net/smart-inbox/twoinone"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "gmx_security_suspension": {
        "description": "GMX security suspension page.",
        "required_sublink": "assistent.gmx.net",
        "checks": [
            {
                "name": "Check security suspension iframe",
                "css_selector": 'div[type="error"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Security error message.",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "gmx_inbox": {
        "description": "GMX email inbox page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active inbox button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-inbox',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Advertising pop-up",
                "css_selector": 'iframe#thirdPartyFrame_permission_dialog',
                "contains_text": None,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": False
            },
            {
                "name": "Smart features pop-up",
                "css_selector": 'iframe#thirdPartyFrame_upp_dialog',
                "contains_text": None,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": False
            },
        ]
    },
    "gmx_favorites": {
        "description": "GMX email favorites page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active favorites button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-favorite',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_general": {
        "description": "GMX email general page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active general button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-general',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_newsletter": {
        "description": "GMX email newsletter page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active newsletter button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-newsletter',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_orders": {
        "description": "GMX email orders page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active orders button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-shopping',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_contracts-and-subscriptions": {
        "description": "GMX email contracts and subscriptions page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active contracts and subscriptions button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-contracts',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_socialmedia": {
        "description": "GMX email socialmedia page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active socialmedia button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-socialmedia',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_trash": {
        "description": "GMX email trash page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active trash button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-trash',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_spam": {
        "description": "GMX email spam page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active spam button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-spam',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_sent": {
        "description": "GMX email sent page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active sent button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-sent',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_drafts": {
        "description": "GMX email drafts page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active drafts button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-drafts',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_outbox": {
        "description": "GMX email outbox page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active outbox button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-outbox',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
}