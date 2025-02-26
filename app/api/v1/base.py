from fastapi import APIRouter
from typing import Dict, Any

def create_base_router(prefix: str = "", tags: list[str] = None) -> APIRouter:
    """Create a base router with standard configuration"""
    return APIRouter(
        prefix=prefix,
        tags=tags or [],
        responses={
            401: {"description": "Authentication failed"},
            500: {"description": "Internal server error"}
        }
    )