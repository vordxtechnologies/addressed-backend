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
    image: UploadFile = File(...),
    token_data: Dict[str, Any] = Depends(verify_firebase_token)
):
    """
    Generate caption for uploaded image
    
    - **image**: Image file to generate caption for
    - Requires Firebase authentication
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )

        # Save the uploaded file
        file_path = await service.save_upload_file(image)
        
        # Generate caption
        caption = await service.generate_caption(file_path)
        
        return ImageCaptioningResponse(
            prompt=caption,
            image_path=file_path
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )