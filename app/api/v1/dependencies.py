from typing import Dict, Any
from fastapi import Depends, HTTPException
from app.core.security.firebase_auth import verify_firebase_token

async def get_current_user(token_data: Dict[str, Any] = Depends(verify_firebase_token)) -> Dict[str, Any]:
    """Common dependency for getting authenticated user data"""
    return token_data

async def get_admin_user(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency for admin-only routes"""
    if not user.get("admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user