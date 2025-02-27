from typing import Any

def validate_email(email: str) -> bool:
    import re
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def format_response(data: Any, message: str = "Success") -> dict:
    return {
        "message": message,
        "data": data
    }