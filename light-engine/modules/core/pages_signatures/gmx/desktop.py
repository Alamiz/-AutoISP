PAGE_SIGNATURES = {
    "gmx_onboarding_page": {
        "description": "GMX onboarding page.",
        "required_sublink": "gmx.net",
        "checks": [
            {
                "name": "Onboarding dialog",
                "css_selector": 'div[data-notification-type="onboarding"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Onboarding dialog exists",
                "weight": 10.0,
                "should_exist": True
            },
        ]
    },
    "gmx_login_page_v2": {
        "description": "GMX Login page v2 (split).",
        "required_sublink": "auth.gmx.net",
        "checks": [
            {
                "name": "Check email input",
                "css_selector": 'input[name="username"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Email input field exists",
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
    "gmx_login_captcha_page_v2": {
        "description": "GMX Login captcha page v2.",
        "required_sublink": "auth.gmx.net",
        "checks": [
            {
                "name": "Captcha Container",
                "css_selector": 'div[data-testid="captcha-container"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Captcha container exists",
                "weight": 5.0,
                "should_exist": True
            },
        ]
    },
    "gmx_login_page": {
        "description": "GMX Login page.",
        "required_sublink": "www.gmx.net",
        "checks": [
            {
                "name": "Check login iframe",
                "css_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
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
                "css_selector": 'a[data-component="button"][href^="https://www.gmx.net/mail/tarifvergleich"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Onboarding dialog",
                "css_selector": 'div[data-notification-type="onboarding"]',
                "contains_text": None,
                "description": "Onboarding dialog exists",
                "weight": 10.0,
                "should_exist": False
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
                "description": "Captcha exists",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Onboarding dialog",
                "css_selector": 'div[data-notification-type="onboarding"]',
                "contains_text": None,
                "description": "Onboarding dialog exists",
                "weight": 10.0,
                "should_exist": False
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
                "css_selector": 'a[data-component="button"][href^="https://www.gmx.net/mail/tarifvergleich"]',
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
            {
                "name": "Onboarding dialog",
                "css_selector": 'div[data-notification-type="onboarding"]',
                "contains_text": None,
                "description": "Onboarding dialog exists",
                "weight": 10.0,
                "should_exist": False
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
                "description": "Wrong password error message",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_phone_verification": {
        "description": "GMX Login phone verification page.",
        "required_sublink": "interception.gmx.net",
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
    "gmx_logged_in_page": {
        "description": "GMX Confirm user page.",
        "required_sublink": "www.gmx.net",
        "checks": [
            {
                "name": "Check login iframe",
                "css_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Login iframe",
                "weight": 3.0,
                "should_exist": True
            },
            {
                "name": "User avatar 1",
                "css_selector": 'account-avatar-homepage[role="button"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "User avatar 2",
                "css_selector": 'appa-account-avatar div.appa-user-icon',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Continue button",
                "css_selector": "button[data-component-path='openInbox.continue-button']",
                # "iframe_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
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
                # "iframe_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
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
                # "iframe_selector": 'iframe[src^="https://alligator.navigator.gmx.net"]',
                "deep_search": True,
                "contains_text": None,
                "description": "Email input field inside login iframe",
                "weight": 2.0,
                "should_exist": False
            },
            {
                "name": "Onboarding dialog",
                "css_selector": 'div[data-notification-type="onboarding"]',
                "contains_text": None,
                "description": "Onboarding dialog exists",
                "weight": 10.0,
                "should_exist": False
            },
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
            #     "description": "",
            #     "weight": 1.0,
            #     "should_exist": True
            # },
            # {
            #     "name": "User avatar",
            #     "css_selector": 'div.nav-header__icons > account-avatar-navigator',
            #     "contains_text": None,
            #     "min_count": 1,
            #     "description": "",
            #     "weight": 1.0,
            #     "should_exist": True
            # },
            {
                "name": "Advertising core pop-up",
                "css_selector": 'iframe.permission-core-iframe',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Onboarding dialog",
                "css_selector": 'div[data-notification-type="onboarding"]',
                "contains_text": None,
                "description": "Onboarding dialog exists",
                "weight": 10.0,
                "should_exist": False
            },
        ]
    },
    # "gmx_inbox_ads_preferences_popup_1": {
    #     "description": "GMX email ads preferences popup.",
    #     "required_sublink": "navigator.gmx.net/mail",
    #     "checks": [
    #         {
    #             "name": "Check inbox iframe",
    #             "css_selector": 'iframe[src*="gmx.net/mail/client"]',
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
    # "gmx_inbox_ads_preferences_popup_2": {
    #     "description": "GMX email ads preferences popup.",
    #     "required_sublink": "navigator.gmx.net/mail",
    #     "checks": [
    #         {
    #             "name": "Check inbox iframe",
    #             "css_selector": 'iframe[src*="gmx.net/mail/client"]',
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
    #             "css_selector": 'iframe#thirdPartyFrame_upp_dialog[src*="navigator.gmx.net/upp-dialog"]',
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
    "gmx_inbox_smart_features_popup": {
        "description": "GMX email smart features popup.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                "name": "Smart features pop-up",
                "css_selector": 'iframe#thirdPartyFrame_upp_dialog',
                "contains_text": None,
                "min_count": 1,
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
                "name": "Active inbox button",
                "css_selector": 'div.sidebar-folder__container--active button.sidebar-folder-icon-inbox',
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Advertising pop-up",
                "css_selector": 'iframe#thirdPartyFrame_permission_dialog',
                "contains_text": None,
                "description": "",
                "weight": 4.0,
                "should_exist": False
            },
            {
                "name": "Smart features pop-up",
                "css_selector": 'iframe#thirdPartyFrame_upp_dialog',
                "contains_text": None,
                "description": "",
                "weight": 4.0,
                "should_exist": False
            },
        ]
    },
    "gmx_account_settings": {
        "description": "GMX account settings page.",
        "required_sublink": "gmx.net/ciss",
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
    "gmx_favorites": {
        "description": "GMX email favorites page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
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
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
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
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
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
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
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
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
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
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
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
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
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
    "gmx_sent": {
        "description": "GMX email sent page.",
        "required_sublink": "navigator.gmx.net/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="gmx.net/mail/client"]',
                "contains_text": None,
                "min_count": 1,
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
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
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
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
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
                # "iframe_selector": 'iframe[src*="gmx.net/mail/client"]',
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