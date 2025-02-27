from app.tools.base.service import BaseToolService
from app.infrastructure.ai.huggingface.client import HuggingFaceClient
from fastapi import UploadFile, HTTPException
from pathlib import Path
import aiofiles
import time
from typing import Dict, Any
from app.core.config.settings import get_settings
from app.core.logging.logging_config import logger

settings = get_settings()

class ImageCaptioningService(BaseToolService):
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/jpg', 'image/webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self):
        super().__init__()
        self.hf_client = HuggingFaceClient()
        self.model_id = "Salesforce/blip-image-captioning-large"
        self.upload_dir = Path(settings.UPLOAD_DIR) / "images"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @property
    def tool_name(self) -> str:
        return "image_captioning"

    async def execute(self, file: UploadFile) -> Dict[str, Any]:
        """Execute image captioning on the uploaded file"""
        try:
            # Validate file
            await self._validate_file(file)
            
            # Read file content once
            image_bytes = await file.read()
            
            # Generate caption first
            caption = await self._generate_caption(image_bytes)
            
            # Save file after successful caption generation
            timestamp = int(time.time())
            unique_filename = f"{timestamp}_{file.filename}"
            file_path = await self._save_upload_file(unique_filename, image_bytes)
            
            return {
                "success": True,
                "caption": caption,
                "file_path": str(file_path)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Image captioning failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        if not file.content_type in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(self.ALLOWED_MIME_TYPES)}"
            )

        # Check file size
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size too large. Maximum size: {self.MAX_FILE_SIZE/1024/1024}MB"
            )

    async def _save_upload_file(self, filename: str, content: bytes) -> Path:
        """Save file content to disk"""
        file_path = self.upload_dir / filename
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                await out_file.write(content)
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to save file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save file")

    async def _generate_caption(self, image_bytes: bytes) -> str:
        """Generate caption using HuggingFace model"""
        try:
            result = await self.hf_client.query_model(self.model_id, image_bytes)
            
            if not isinstance(result, list) or not result:
                raise ValueError("Invalid response from model")
                
            caption = result[0].get('generated_text')
            if not caption:
                raise ValueError("No caption generated")
                
            return caption
            
        except Exception as e:
            self.logger.error(f"Caption generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate caption: {str(e)}"
            )