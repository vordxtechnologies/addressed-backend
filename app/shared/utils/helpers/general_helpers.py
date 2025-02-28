from typing import Any, Dict, List, Optional, Union
import re
import json
from datetime import datetime, date
from uuid import UUID
import hashlib
from pathlib import Path

def validate_email(email: str) -> bool:
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def format_response(data: Any, message: str = "Success", status: str = "success") -> Dict:
    """Format standard API response"""
    return {
        "status": status,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limit length
    name, ext = Path(filename).stem, Path(filename).suffix
    if len(name) > 100:
        name = name[:100]
    return f"{name}{ext}"

def generate_file_hash(content: bytes) -> str:
    """Generate SHA-256 hash of file content"""
    return hashlib.sha256(content).hexdigest()

def parse_date(date_str: str) -> Optional[date]:
    """Parse date string in multiple formats"""
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

class JSONEncoder(json.JSONEncoder):
    """Enhanced JSON encoder for handling additional types"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super().default(obj)

def safe_json_dumps(obj: Any) -> str:
    """Safely serialize object to JSON string"""
    return json.dumps(obj, cls=JSONEncoder)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def deep_get(obj: Dict, path: str, default: Any = None) -> Any:
    """Get nested dictionary value using dot notation"""
    try:
        parts = path.split('.')
        for part in parts:
            obj = obj[part]
        return obj
    except (KeyError, TypeError):
        return default

def deep_update(original: Dict, update: Dict) -> Dict:
    """Deep update a nested dictionary"""
    for key, value in update.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            original[key] = deep_update(original[key], value)
        else:
            original[key] = value
    return original

def normalize_phone(phone: str) -> str:
    """Normalize phone number format"""
    # Remove all non-numeric characters
    phone = re.sub(r'\D', '', phone)
    if len(phone) == 10:
        return f"+1{phone}"
    elif len(phone) == 11 and phone.startswith('1'):
        return f"+{phone}"
    return phone

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].strip() + suffix