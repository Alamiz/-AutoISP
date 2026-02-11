PAGE_SIGNATURES = {
    "mailcheck_options_page": {
        "description": "MailCheck extension options page.",
        "required_sublink": "chrome-extension://",
        "checks": [
            {
                "name": "Add account button",
                "css_selector": "button#email-add",
                "contains_text": None,
                "min_count": 1,
                "description": "Add account button exists",
                "weight": 3.0,
                "should_exist": True
            },
        ]
    },
    "webde_login_page": {
        "description": "Webde Login page.",
        "required_sublink": "web.de",
        "checks": [
            {
                "name": "Check login iframe",
                "css_selector": 'iframe[src^="https://alligator.navigator.web.de"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "Email input field inside login iframe",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Create account button",
                "css_selector": 'a[data-component="button"][href^="https://web.de/email/tarifvergleich"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Error message",
                "css_selector": 'p[data-testid="error-email"]',
                "contains_text": None,
                "description": "Wrong username error message",
                "weight": 4.0,
                "should_exist": False
            },
        ]
    },
    "webde_login_page_v2": {
        "description": "Webde Login page v2 (split).",
        "required_sublink": "auth.web.de",
        "checks": [
            {
                "name": "Check login form",
                "css_selector": 'form#login',
                "contains_text": None,
                "min_count": 1,
                "description": "Login form exists",
                "weight": 5.0,
                "should_exist": True
            },
            {
                "name": "Captcha Container",
                "css_selector": 'div[data-testid="captcha-container"]',
                "contains_text": None,
                "description": "Captcha container don't exists",
                "weight": 5.0,
                "should_exist": False
            },
        ]
    },
    "webde_login_captcha_page": {
        "description": "Webde Login captcha page.",
        "required_sublink": "web.de",
        "checks": [
            {
                "name": "Captcha",
                "css_selector": "div[data-testid='captcha']",
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "Captcha exists",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_login_wrong_username": {
        "description": "Webde Login wrong username page.",
        "required_sublink": "web.de",
        "checks": [
            {
                "name": "Check login iframe",
                "css_selector": 'iframe[src^="https://alligator.navigator.web.de"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "Email input field inside login iframe",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Create account button",
                "css_selector": 'a[data-component="button"][href^="https://web.de/email/tarifvergleich"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Error message",
                "css_selector": 'p[data-testid="error-email"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Wrong username error message",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_login_wrong_password": {
        "description": "Webde Login wrong password page.",
        "required_sublink": "web.de/logoutlounge/?status=login-failed",
        "checks": [
            {
                "name": "Error message",
                "css_selector": 'div[data-component="notification"][data-notification-type="error-light"][position="beforeLogin"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "Wrong password error message",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_phone_verification": {
        "description": "Webde Login phone verification page.",
        "required_sublink": "interception.web.de",
        "checks": [
            {
                "name": "Phone text",
                "css_selector": 'div.mtan-code-input__panel',
                "contains_text": None,
                "min_count": 1,
                "description": "Phone number text",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_logged_in_page": {
        "description": "Webde Confirm user page.",
        "required_sublink": "web.de",
        "checks": [
            {
                "name": "Check login iframe",
                "css_selector": 'iframe[src^="https://alligator.navigator.web.de"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Login iframe",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'account-avatar[role="button"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Continue button",
                "css_selector": "button[data-component-path='openInbox.continue-button']",
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "Button to confirm already authenticated user inside iframe.",
                "weight": 3.0,
                "should_exist": True
            },
            {
                "name": "Greeting user",
                "css_selector": "div.oi_customer span.oi_customer_greeting",
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "Logged in user greeting text.",
                "weight": 3.0,
                "should_exist": True
            },
            {
                "name": "Email input",
                "css_selector": "input#username",
                "deep_search": True,
                "contains_text": None,
                "description": "Email input field inside login iframe",
                "weight": 2.0,
                "should_exist": False
            }
        ]
    },
    "webde_inbox_ads_preferences_popup_1_core": {
        "description": "Webde email ads preferences popup (core).",
        "required_sublink": "web.de/consent-management",
        "checks": [
            {
                "name": "Advertising core pop-up",
                "css_selector": 'iframe.permission-core-iframe',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    # "webde_inbox_ads_preferences_popup_1": {
    #     "description": "Webde email ads preferences popup.",
    #     "required_sublink": "web.de/mail",
    #     "checks": [
    #         {
    #             "name": "Check inbox iframe",
    #             "css_selector": 'iframe[src*="web.de/mail/client"]',
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "Inbox iframe",
    #             "weight": 1.0,
    #             "should_exist": True
    #         },
    #         {
    #             "name": "Emails sidebar",
    #             "css_selector": 'webmailer-mail-sidebar#sidebar',
    #             "deep_search": True,
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "",
    #             "weight": 1.0,
    #             "should_exist": True
    #         },
    #         {
    #             "name": "User avatar",
    #             "css_selector": 'div.nav-header__icons > account-avatar-navigator',
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "",
    #             "weight": 1.0,
    #             "should_exist": True
    #         },
    #         {
    #             "name": "Advertising pop-up",
    #             "css_selector": 'iframe#thirdPartyFrame_permission_dialog',
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "",
    #             "weight": 4.0,
    #             "should_exist": True
    #         },
    #     ]
    # },
    # "webde_inbox_ads_preferences_popup_2": {
    #     "description": "Webde email ads preferences popup.",
    #     "required_sublink": "web.de/mail",
    #     "checks": [
    #         {
    #             "name": "Check inbox iframe",
    #             "css_selector": 'iframe[src*="web.de/mail/client"]',
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "Inbox iframe",
    #             "weight": 1.0,
    #             "should_exist": True
    #         },
    #         {
    #             "name": "Emails sidebar",
    #             "css_selector": 'webmailer-mail-sidebar#sidebar',
    #             "deep_search": True,
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "",
    #             "weight": 1.0,
    #             "should_exist": True
    #         },
    #         {
    #             "name": "User avatar",
    #             "css_selector": 'div.nav-header__icons > account-avatar-navigator',
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "",
    #             "weight": 1.0,
    #             "should_exist": True
    #         },
    #         {
    #             "name": "Advertising pop-up",
    #             "css_selector": 'iframe#thirdPartyFrame_upp_dialog[src*="navigator.web.de/upp-dialog"]',
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "",
    #             "weight": 2.0,
    #             "should_exist": True
    #         },
    #         {
    #             "name": "Advertising popup deny button",
    #             "css_selector": 'button#deny',
    #             "deep_search": True,
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "",
    #             "weight": 1.0,
    #             "should_exist": True
    #         },
    #         {
    #             "name": "Advertising popup accept button",
    #             "css_selector": 'button#cta',
    #             "deep_search": True,
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "",
    #             "weight": 1.0,
    #             "should_exist": True
    #         },
    #     ]
    # },
    "webde_inbox_smart_features_popup": {
        "description": "Webde email smart features popup.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div#actions-menu-static > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Smart features pop-up",
                "css_selector": 'iframe#thirdPartyFrame_upp_dialog',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Accept button",
                "css_selector": 'button[data-component-path="accept-button"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Deny button",
                "css_selector": 'button[data-component-path="deny-button"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            }
        ]
    },
    "webde_security_suspension": {
        "description": "Webde security suspension page.",
        "required_sublink": "assistent.web.de",
        "checks": [
            {
                "name": "Check security suspension iframe",
                "css_selector": 'div[type="error"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Security error message.",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "webde_inbox": {
        "description": "Webde email inbox page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Inbox iframe",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Emails sidebar",
                "css_selector": 'webmailer-mail-sidebar#sidebar',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div#actions-menu-static > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active inbox button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-inbox',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            # {
            #     "name": "Advertising pop-up",
            #     "css_selector": 'iframe#thirdPartyFrame_permission_dialog',
            #     "contains_text": None,
            #     "description": "",
            #     "weight": 4.0,
            #     "should_exist": False
            # },
            # {
            #     "name": "Smart features pop-up",
            #     "css_selector": 'iframe#thirdPartyFrame_upp_dialog',
            #     "contains_text": None,
            #     "description": "",
            #     "weight": 4.0,
            #     "should_exist": False
            # },
        ]
    },
    "webde_account_settings": {
        "description": "Webde account settings page.",
        "required_sublink": "web.de/ciss",
        "checks": [
            {
                "name": "My account button",
                "css_selector": 'li[data-icon="my-account"]',
                "contains_text": None,
                "min_count": 1,
                "description": "My account button in the navigation menu",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Personal data button",
                "css_selector": 'li[data-icon="personal-data"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Personal data button in the navigation menu",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Security button",
                "css_selector": 'li[data-icon="security"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Security button in the navigation menu",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Contracts button",
                "css_selector": 'li[data-icon="contracts"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Contracts button in the navigation menu",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Permissions button",
                "css_selector": 'li[data-icon="permissions"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Permissions button in the navigation menu",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "webde_favorites": {
        "description": "Webde email favorites page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active favorites button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-favorite',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_general": {
        "description": "Webde email general page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active general button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-general',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_newsletter": {
        "description": "Webde email newsletter page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active newsletter button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-newsletter',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_orders": {
        "description": "Webde email orders page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active orders button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-shopping',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_contracts-and-subscriptions": {
        "description": "Webde email contracts and subscriptions page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active contracts and subscriptions button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-contracts',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_socialmedia": {
        "description": "Webde email socialmedia page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active socialmedia button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-socialmedia',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_trash": {
        "description": "Webde email trash page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active trash button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-trash',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_spam": {
        "description": "Webde email spam page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_sent": {
        "description": "Webde email sent page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active sent button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-sent',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_drafts": {
        "description": "Webde email drafts page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active drafts button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-drafts',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "webde_outbox": {
        "description": "Webde email outbox page.",
        "required_sublink": "web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar",
                "css_selector": 'div.nav-header__icons > account-avatar-navigator',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Active outbox button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-outbox',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
}