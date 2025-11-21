"""Default Self-Healing Strategies (하드코딩된 공통 전략)"""

# 로그인 폼 공통 전략
DEFAULT_LOGIN_STRATEGIES = {
    "username_input": [
        # Priority 10-19: 공통 전략
        {"selector": "input[type='text']", "priority": 10, "method": "type"},
        {"selector": "input[type='email']", "priority": 11, "method": "type"},
        {"selector": "input[name='username']", "priority": 12, "method": "name"},
        {"selector": "input[name='email']", "priority": 13, "method": "name"},
        {"selector": "input[name='user_id']", "priority": 14, "method": "name"},
        {"selector": "input[placeholder*='아이디']", "priority": 15, "method": "placeholder"},
        {"selector": "input[placeholder*='이메일']", "priority": 16, "method": "placeholder"},
        {"selector": "input[placeholder*='ID']", "priority": 17, "method": "placeholder"},
        {"selector": "#username", "priority": 18, "method": "id"},
        {"selector": "#user_id", "priority": 19, "method": "id"},
    ],

    "password_input": [
        {"selector": "input[type='password']", "priority": 10, "method": "type"},
        {"selector": "input[name='password']", "priority": 11, "method": "name"},
        {"selector": "input[name='passwd']", "priority": 12, "method": "name"},
        {"selector": "input[placeholder*='비밀번호']", "priority": 13, "method": "placeholder"},
        {"selector": "input[placeholder*='패스워드']", "priority": 14, "method": "placeholder"},
        {"selector": "input[placeholder*='password']", "priority": 15, "method": "placeholder"},
        {"selector": "#password", "priority": 16, "method": "id"},
        {"selector": "#passwd", "priority": 17, "method": "id"},
    ],

    "submit_button": [
        {"selector": "button[type='submit']", "priority": 10, "method": "type"},
        {"selector": "input[type='submit']", "priority": 11, "method": "type"},
        {"selector": "button:has-text('로그인')", "priority": 12, "method": "text"},
        {"selector": "button:has-text('로그인하기')", "priority": 13, "method": "text"},
        {"selector": "button:has-text('확인')", "priority": 14, "method": "text"},
        {"selector": "button:has-text('Login')", "priority": 15, "method": "text"},
        {"selector": "button:has-text('Sign in')", "priority": 16, "method": "text"},
        {"selector": "#login-button", "priority": 17, "method": "id"},
        {"selector": "#login-btn", "priority": 18, "method": "id"},
        {"selector": ".login-button", "priority": 19, "method": "class"},
    ],

    "error_message": [
        {"selector": ".error", "priority": 10, "method": "class"},
        {"selector": ".error-message", "priority": 11, "method": "class"},
        {"selector": ".login-error", "priority": 12, "method": "class"},
        {"selector": ".alert-danger", "priority": 13, "method": "class"},
        {"selector": "#error-message", "priority": 14, "method": "id"},
        {"selector": "[role='alert']", "priority": 15, "method": "role"},
    ]
}


# 폼 제출 공통 전략
DEFAULT_FORM_STRATEGIES = {
    "submit_button": [
        {"selector": "button[type='submit']", "priority": 10, "method": "type"},
        {"selector": "input[type='submit']", "priority": 11, "method": "type"},
        {"selector": "button:has-text('등록')", "priority": 12, "method": "text"},
        {"selector": "button:has-text('등록하기')", "priority": 13, "method": "text"},
        {"selector": "button:has-text('제출')", "priority": 14, "method": "text"},
        {"selector": "button:has-text('제출하기')", "priority": 15, "method": "text"},
        {"selector": "button:has-text('확인')", "priority": 16, "method": "text"},
        {"selector": "button:has-text('Submit')", "priority": 17, "method": "text"},
        {"selector": "button:has-text('Save')", "priority": 18, "method": "text"},
        {"selector": "#submit-button", "priority": 19, "method": "id"},
    ],

    "success_message": [
        {"selector": ".success", "priority": 10, "method": "class"},
        {"selector": ".success-message", "priority": 11, "method": "class"},
        {"selector": ".alert-success", "priority": 12, "method": "class"},
        {"selector": ".notification-success", "priority": 13, "method": "class"},
        {"selector": "#success-message", "priority": 14, "method": "id"},
        {"selector": "[role='status']", "priority": 15, "method": "role"},
    ],

    "error_message": [
        {"selector": ".error", "priority": 10, "method": "class"},
        {"selector": ".error-message", "priority": 11, "method": "class"},
        {"selector": ".alert-danger", "priority": 12, "method": "class"},
        {"selector": ".alert-error", "priority": 13, "method": "class"},
        {"selector": "#error-message", "priority": 14, "method": "id"},
        {"selector": "[role='alert']", "priority": 15, "method": "role"},
    ]
}


def get_default_strategies(element_key: str, context: str = 'form'):
    """
    하드코딩된 공통 전략 반환

    Parameters:
    -----------
    element_key : str
        요소 키 (예: 'username_input', 'submit_button')
    context : str
        컨텍스트 ('login' 또는 'form')

    Returns:
    --------
    list
        전략 리스트
    """
    if context == 'login':
        return DEFAULT_LOGIN_STRATEGIES.get(element_key, [])
    else:
        return DEFAULT_FORM_STRATEGIES.get(element_key, [])
