PAGE_SIGNATURES = {
    "webde_register_page": {
        "description": "Webde Register page.",
        "required_sublink": "web.de",
        "checks": [
            {
                "name": "Register button",
                "css_selector": 'button.register__button',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Register form",
                "css_selector": 'form[action*="registrierung.web.de"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Login button",
                "css_selector": 'form.login-link.login-mobile > button[type="submit"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Email input",
                "css_selector": 'form[action*="registrierung.web.de"] input[type="text"]',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Register button",
                "css_selector": 'form[action*="registrierung.web.de"] button[type="submit"]',
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
    "webde_logged_in_page": {
        "description": "WebDE Logged In page.",
        "required_sublink": "www.web.de",
        "checks": [
            {
                "name": "Register button",
                "css_selector": 'button.register__button',
                "deep_search": True,
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
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
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Login button",
                "css_selector": 'form.login-link.login-mobile > button[type="submit"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
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
                "require_english": False,
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
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
        ]
    },
    "webde_login_page": {
        "description": "Webde Login page.",
        "required_sublink": "auth.web.de/login/mobile",
        "checks": [
            {
                "name": "Email input",
                "css_selector": 'form input#username',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Continue button",
                "css_selector": 'form button[type="submit"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Registration button",
                "css_selector": 'button[data-testid="button-registration"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Login button",
                "css_selector": 'form.login-link.login-mobile > button[type="submit"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": False
            },
        ]
    },
    "webde_inbox_ads_preferences_popup_1": {
        "description": "Webde email ads preferences popup (core).",
        "required_sublink": "web.de",
        "checks": [
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
    "webde_inbox_ads_preferences_popup_2": {
        "description": "Webde email ads preferences popup.",
        "required_sublink": "web.de",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="permission"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "Inbox iframe",
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
                "weight": 2.0,
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
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "webde_inbox_smart_features_popup": {
        "description": "Webde email smart features popup.",
        "required_sublink": "navigator.web.de/mail",
        "checks": [
            {
                "name": "Check inbox iframe",
                "css_selector": 'iframe[src*="web.de/mail/client"]',
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
                "css_selector": 'iframe[src*="spl.web.de/smart-inbox/twoinone"]',
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
    "webde_folder_list_page": {
        "description": "Webde folder list page.",
        "required_sublink": "web.de/folderlist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Webde logo in folder list page",
                "css_selector": 'div.sidebar__top > div.sidebar__logo',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
            {
                "name": "Search input",
                "css_selector": 'input.search-form__input',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Middle sidebar folder list",
                "css_selector": 'div.sidebar__middle > ul.sidebar__folder-list',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "webde_inbox": {
        "description": "Webde email inbox page.",
        "required_sublink": "web.de/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Posteingang",
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "webde_deleted": {
        "description": "Webde deleted emails page.",
        "required_sublink": "web.de/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Gelöscht",
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "webde_spam": {
        "description": "Webde spam emails page.",
        "required_sublink": "web.de/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Spam",
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "webde_sent": {
        "description": "Webde sent emails page.",
        "required_sublink": "web.de/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Gesendet",
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "webde_draft": {
        "description": "Webde draft emails page.",
        "required_sublink": "web.de/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Entwürfe",
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
    "webde_outbox": {
        "description": "Webde outbox emails page.",
        "required_sublink": "web.de/messagelist",
        "checks": [
            {
                "name": "Logout button",
                "css_selector": 'div.navigator-panel > ul.toolbar__icon[data-position="right"] a',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 1.0,
                "should_exist": True
            },
            {
                "name": "Folder title",
                "css_selector": 'div.message-list-panel__navigation-bar li.toolbar__content a',
                "contains_text": "Postausgang",
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Messages list",
                "css_selector": 'div.message-list-panel__content[role="main"]',
                "contains_text": None,
                "min_count": 1,
                "require_english": False,
                "description": "",
                "weight": 2.0,
                "should_exist": True
            },
        ]
    },
}