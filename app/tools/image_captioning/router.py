from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.security.firebase_auth import verify_firebase_token
from .service import ImageCaptioningService
from .schemas import ImageCaptioningResponse, ErrorResponse
from typing import Dict, Any

router = APIRouter(prefix="/image-captioning", tags=["Image Captioning"])
service = ImageCaptioningService()

@router.post(
    "/generate",
    response_model=ImageCaptioningResponse,
    responses={
        200: {
            "description": "Successfully generated image caption",
            "model": ImageCaptioningResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def generate_caption(
    file: UploadFile = File(...),
    token_data: Dict[str, Any] = Depends(verify_firebase_token)
):
    """Generate caption for an image"""
    result = await service.execute(file)
    return ImageCaptioningResponse(**result)