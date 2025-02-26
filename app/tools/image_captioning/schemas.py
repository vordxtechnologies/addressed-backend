from pydantic import BaseModel
from typing import Optional

class ImageCaptioningResponse(BaseModel):
    prompt: str
    image_path: Optional[str]

class ErrorResponse(BaseModel):
    error: str