from typing import Dict, Any
import aiohttp
from app.core.config.settings import get_settings
from app.core.logging.logging_config import logger

settings = get_settings()

class HuggingFaceClient:
    def __init__(self):
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.base_url = "https://api-inference.huggingface.co/models"
        # Remove Content-Type header to let aiohttp set it automatically for binary data
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    async def query_model(self, model_id: str, image_bytes: bytes) -> Dict[str, Any]:
        """Query Hugging Face model API with raw image data"""
        url = f"{self.base_url}/{model_id}"
        try:
            async with aiohttp.ClientSession() as session:
                # Send image bytes directly without any JSON encoding
                async with session.post(
                    url,
                    headers=self.headers,
                    data=image_bytes,
                    timeout=30
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"HuggingFace API error: {error_text}")
                        raise Exception(f"API request failed: {error_text}")
                    
                    return await response.json()
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"HuggingFace API error: {str(e)}")
            raise