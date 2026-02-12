PAGE_SIGNATURES = {
    "libero_login_page": {
        "description": "Libero Login page (email entry).",
        "required_sublink": "login.libero.it",
        "checks": [
            {
                "name": "Email input",
                "css_selector": 'input#loginid',
                "contains_text": None,
                "min_count": 1,
                "description": "Email input field exists",
                "weight": 10.0,
                "should_exist": True
            },
            {
                "name": "Password input",
                "css_selector": 'input[type="password"]', 
                "contains_text": None,
                "description": "Password input field should NOT exist yet",
                "weight": 5.0,
                "should_exist": False
            },
            {
                "name": "Login error",
                "css_selector": 'span#loginid_error',
                "contains_text": "sospesa",
                "description": "Login error should NOT exist yet",
                "weight": 10.0,
                "should_exist": False
            }
        ]
    },
    "libero_suspended_page": {
        "description": "Libero Login page (login error).",
        "required_sublink": "login.libero.it",
        "checks": [
            {
                "name": "Login error",
                "css_selector": 'span#loginid_error',
                "contains_text": "sospesa",
                "min_count": 1,
                "description": "Login error exists",
                "weight": 10.0,
                "should_exist": True
            }
        ]
    },
    "libero_login_password_page": {
        "description": "Libero Login page (password entry).",
        "required_sublink": "login.libero.it",
        "checks": [
            {
                "name": "Password input",
                "css_selector": 'input#password',
                "contains_text": None,
                "min_count": 1,
                "description": "Password input field exists",
                "weight": 10.0,
                "should_exist": True
            },
            {
                "name": "Submit button",
                "css_selector": 'button#form_submit', 
                "contains_text": None,
                "description": "Submit button exists",
                "weight": 5.0,
                "should_exist": True
            },
            {
                "name": "Login error",
                "css_selector": 'span#loginid_error',
                "contains_text": "sospesa",
                "description": "Login error should NOT exist yet",
                "weight": 10.0,
                "should_exist": False
            }
        ]
    },
    "libero_inbox_page": {
        "description": "Libero inbox page.",
        "required_sublink": "mail1.libero.it",
        "checks": [
            {
                "name": "Navigation menu",
                "css_selector": 'div#io-ox-appcontrol',
                "contains_text": None,
                "description": "Navigation menu exists",
                "weight": 4.0,
                "should_exist": True
            },
            {
                "name": "Main menu element",
                "css_selector": 'div#iol-services',
                "contains_text": None,
                "description": "Main menu element exists",
                "weight": 4.0,
                "should_exist": True
            }
        ]
    },
}
