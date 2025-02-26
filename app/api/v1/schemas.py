from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str

class ProtectedResponse(BaseModel):
    message: str
    user_id: str
    email: str | None

class AdminResponse(BaseModel):
    message: str