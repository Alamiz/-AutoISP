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
                "css_selector": 'div[data-testid="container-email"], form[data-testid="container-password"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Email input field exists",
                "weight": 5.0,
                "should_exist": True
            },
                        {
                "name": "Wrong username error message",
                "css_selector": "p[data-testid='error-username']",
                "deep_search": True,
                "contains_text": None,
                "description": "Wrong username error message exists",
                "weight": 10.0,
                "should_exist": False
            },
            {
                "name": "Wrong password error message",
                "css_selector": "p[data-testid='error-password']",
                "deep_search": True,
                "contains_text": None,
                "description": "Wrong password error message exists",
                "weight": 10.0,
                "should_exist": False
            },
        ]
    },
    "gmx_login_captcha_page": {
        "description": "GMX Login captcha page.",
        "required_sublink": "auth.gmx.net",
        "checks": [
            {
                "name": "Captcha",
                "css_selector": "form[data-testid='container-captcha']",
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "Captcha exists",
                "weight": 4.0,
                "should_exist": True
            },
                        {
                "name": "Wrong username error message",
                "css_selector": "p[data-testid='error-username']",
                "deep_search": True,
                "contains_text": None,
                "description": "Wrong username error message exists",
                "weight": 10.0,
                "should_exist": False
            },
            {
                "name": "Wrong password error message",
                "css_selector": "p[data-testid='error-password']",
                "deep_search": True,
                "contains_text": None,
                "description": "Wrong password error message exists",
                "weight": 10.0,
                "should_exist": False
            },
        ]
    },
    "gmx_wrong_username_v2_page": {
        "description": "GMX Login wrong username page v2 (split).",
        "required_sublink": "auth.gmx.net",
        "checks": [
            {
                "name": "Wrong username error message",
                "css_selector": 'p[data-testid="error-username"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "Wrong username error message exists",
                "weight": 10.0,
                "should_exist": True
            },
        ]
    },
    "gmx_wrong_password_v2_page": {
        "description": "GMX Login wrong password page v2 (split).",
        "required_sublink": "auth.gmx.net",
        "checks": [
            {
                "name": "Wrong password error message",
                "css_selector": "p[data-testid='error-password']",
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "Wrong password error message exists",
                "weight": 10.0,
                "should_exist": True
            },
        ]
    },
    "gmx_register_page": {
        "description": "GMX Register page.",
        "required_sublink": "www.gmx.net",
        "checks": [
            {
                "name": "Account avatar",
                "css_selector": 'div.login-wrapper  > account-avatar',
                "deep_search": True,
                "contains_text": None,
                "description": "",
                "weight": 4.0,
                "should_exist": False
            },
            {
                "name": "Register button",
                "css_selector": 'button.register__button',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Register form",
                "css_selector": 'form[action*="registrierung.gmx.net"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Login button",
                "css_selector": 'form.login-link.login-mobile > button[type="submit"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Email input",
                "css_selector": 'form[action*="registrierung.gmx.net"] input[type="text"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Register button",
                "css_selector": 'form[action*="registrierung.gmx.net"] button[type="submit"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
        ]
    },
    "gmx_logged_in_page": {
        "description": "GMX Logged In page.",
        "required_sublink": "www.gmx.net",
        "checks": [
            {
                "name": "Register button",
                "css_selector": 'button.register__button',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Account avatar",
                "css_selector": 'div.login-wrapper  > account-avatar',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Login button",
                "css_selector": 'form.login-link.login-mobile > button[type="submit"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Email input",
                "css_selector": 'form[action*="registrierung.gmx.net"] input[type="text"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Register button",
                "css_selector": 'form[action*="registrierung.gmx.net"] button[type="submit"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
        ]
    },
    "gmx_login_page": {
        "description": "GMX Login page.",
        "required_sublink": "auth.gmx.net/login/mobile",
        "checks": [
            {
                "name": "Email input",
                "css_selector": 'form input#username',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Continue button",
                "css_selector": 'form button[type="submit"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Registration button",
                "css_selector": 'button[data-testid="button-registration"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Login button",
                "css_selector": 'form.login-link.login-mobile > button[type="submit"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": False
            },
        ]
    },
    "gmx_login_wrong_username": {
        "description": "GMX login wrong username page.",
        "required_sublink": "auth.gmx.net/login/mobile",
        "checks": [
            {
                "name": "Email input",
                "css_selector": 'form input#username',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Continue button",
                "css_selector": 'form button[type="submit"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Registration button",
                "css_selector": 'button[data-testid="button-registration"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Error message",
                "css_selector": 'p[data-testid="error-username"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Wrong username error message.",
                "weight": 4.0,
                "should_exist": True
            },
        ]
    },
    "gmx_login_wrong_password": {
        "description": "GMX login wrong password page.",
        "required_sublink": "auth.gmx.net/login/mobile",
        "checks": [
            {
                "name": "Email input",
                "css_selector": 'form input#username',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Password input",
                "css_selector": 'input[type="password"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Continue button",
                "css_selector": 'form button[type="submit"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Registration button",
                "css_selector": 'button[data-testid="button-registration"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Error message",
                "css_selector": 'p[data-testid="error-password"]',
                "contains_text": None,
                "min_count": 1,
                "description": "Wrong password error message.",
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
    # "gmx_inbox_ads_preferences_popup_1": {
    #     "description": "GMX email ads preferences popup (core).",
    #     "required_sublink": "gmx.net",
    #     "checks": [
    #         {
    #             "name": "Advertising core pop-up",
    #             "css_selector": 'iframe.permission-core-iframe',
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
    #     "required_sublink": "gmx.net",
    #     "checks": [
    #         {
    #             "name": "Check inbox iframe",
    #             "css_selector": 'iframe[src*="permission"]',
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "Inbox iframe",
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
    #             "weight": 2.0,
    #             "should_exist": True
    #         },
    #         {
    #             "name": "Advertising popup accept button",
    #             "css_selector": 'button#cta',
    #             "deep_search": True,
    #             "contains_text": None,
    #             "min_count": 1,
    #             "description": "",
    #             "weight": 2.0,
    #             "should_exist": True
    #         },
    #     ]
    # },
    "gmx_inbox_smart_features_popup": {
        "description": "GMX email smart features popup.",
        "required_sublink": "gmx.net",
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
                "css_selector": 'iframe[src*="spl.web.de/smart-inbox/twoinone"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "gmx_folder_list_page": {
        "description": "GMX folder list page.",
        "required_sublink": "gmx.net/folderlist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "GMX logo in folder list page",
                "css_selector": 'div.sidebar__top > div.sidebar__logo',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Search input",
                "css_selector": 'input.search-form__input',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Middle sidebar folder list",
                "css_selector": 'div.sidebar__middle > ul.sidebar__folder-list',
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
        "required_sublink": "lightmailer-bs.gmx.net/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Posteingang",
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "gmx_deleted": {
        "description": "GMX deleted emails page.",
        "required_sublink": "lightmailer-bs.gmx.net/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Gelöscht",
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "gmx_spam": {
        "description": "GMX spam emails page.",
        "required_sublink": "lightmailer-bs.gmx.net/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Spamverdacht",
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "gmx_sent": {
        "description": "GMX sent emails page.",
        "required_sublink": "lightmailer-bs.gmx.net/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Gesendet",
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "gmx_draft": {
        "description": "GMX draft emails page.",
        "required_sublink": "lightmailer-bs.gmx.net/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Entwürfe",
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "gmx_outbox": {
        "description": "GMX outbox emails page.",
        "required_sublink": "lightmailer-bs.gmx.net/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Postausgang",
                "min_count": 1,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
}