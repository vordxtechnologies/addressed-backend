from fastapi import APIRouter, HTTPException
from typing import Dict, Any

def create_base_router(prefix: str = "", tags: list[str] = None) -> APIRouter:
    """Create a base router with standard configuration
    
    Args:
        prefix: URL prefix for all routes in this router
        tags: OpenAPI tags for grouping endpoints
        
    Returns:
        Configured FastAPI router with standard error responses
    """
    return APIRouter(
        prefix=prefix,
        tags=tags or [],
        responses={
            400: {"description": "Bad request"},
            401: {"description": "Authentication failed"},
            403: {"description": "Permission denied"},
            404: {"description": "Resource not found"},
            429: {"description": "Too many requests"}, 
            500: {"description": "Internal server error"}
        }
    )