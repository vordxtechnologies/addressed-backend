import aiohttp
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
import os
import logging
from app.core.config.settings import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageCaptioningService:
    def __init__(self):
        self.huggingface_api_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
        self.headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"
        }
        logger.info(f"Using Hugging Face API Key: {settings.HUGGINGFACE_API_KEY}")
        self.upload_dir = Path(settings.UPLOAD_DIR) / "images"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload_file(self, file: UploadFile) -> str:
        """Save uploaded file and return the file path"""
        file_path = self.upload_dir / file.filename
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            logger.info(f"File saved successfully at {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save file")

    async def generate_caption(self, file_path: str) -> str:
        """Generate caption using HuggingFace API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with aiofiles.open(file_path, 'rb') as f:
                    data = await f.read()
                    async with session.post(
                        self.huggingface_api_url,
                        headers=self.headers,
                        data=data
                    ) as response:
                        if response.status != 200:
                            logger.error(f"Failed to generate caption: {response.status}")
                            raise HTTPException(
                                status_code=response.status,
                                detail="Failed to generate caption"
                            )
                        result = await response.json()
                        logger.info(f"Caption generated successfully for {file_path}")
                        return result[0].get('generated_text', '')
        except Exception as e:
            logger.error(f"Error during caption generation: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate caption")