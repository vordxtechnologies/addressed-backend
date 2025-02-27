from pydantic import BaseModel

class ImageCaptioningResponse(BaseModel):
    success: bool
    caption: str
    file_path: str

class ErrorResponse(BaseModel):
    error: str