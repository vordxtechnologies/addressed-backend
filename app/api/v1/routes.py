from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security.firebase_auth import verify_firebase_token
from app.tools.image_captioning.router import router as image_captioning_router
from typing import Dict, Any
from .schemas import HealthResponse, ProtectedResponse, AdminResponse
# from .security import security_scheme

api_router = APIRouter(
    responses={
        401: {"description": "Authentication failed"},
        500: {"description": "Internal server error"}
    }
)

@api_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running"
)
async def health_check():
    """Returns the health status of the API."""
    return {"status": "healthy"}

@api_router.get(
    "/protected",
    response_model=ProtectedResponse,
    summary="Protected Route",
    description="Example of a protected route requiring authentication",
    responses={
        200: {
            "description": "Successfully accessed protected route",
            "content": {
                "application/json": {
                    "example": {
                        "message": "This is a protected route",
                        "user_id": "user123",
                        "email": "user@example.com"
                    }
                }
            }
        },
        401: {
            "description": "Invalid or missing authentication token"
        }
    }
)
async def protected_route(
    # auth: HTTPAuthorizationCredentials = Security(security_scheme),
    token_data: Dict[str, Any] = Depends(verify_firebase_token)
):
    """Protected endpoint that requires a valid Firebase token."""
    return {
        "message": "This is a protected route",
        "user_id": token_data["uid"],
        "email": token_data.get("email")
    }

@api_router.get(
    "/admin",
    response_model=AdminResponse,
    summary="Admin Route",
    description="Protected route with admin role check",
    responses={
        200: {
            "description": "Successfully accessed admin route",
            "content": {
                "application/json": {
                    "example": {"message": "Admin route accessed"}
                }
            }
        },
        401: {"description": "Invalid or missing authentication token"},
        403: {"description": "User does not have admin privileges"}
    }
)
async def admin_route(
    # auth: HTTPAuthorizationCredentials = Security(security_scheme),
    token_data: Dict[str, Any] = Depends(verify_firebase_token)
):
    """Admin-only endpoint that requires a valid Firebase token with admin claim."""
    if not token_data.get("admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Admin route accessed"}

# Include tool routers
api_router.include_router(image_captioning_router, prefix="/tools")