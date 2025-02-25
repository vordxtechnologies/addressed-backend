from pydantic import BaseModel

class User(BaseModel):
    id: str
    email: str
    name: str
    created_at: str
    updated_at: str