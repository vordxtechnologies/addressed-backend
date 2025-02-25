from fastapi import APIRouter, Depends
from app.services.user_service import get_user, update_user, delete_user
from app.core.security import get_current_user

router = APIRouter()

@router.get("/profile")
def get_profile(user_id: str = Depends(get_current_user)):
    user = get_user(user_id)
    if user:
        return user
    return {"error": "User not found"}

@router.put("/profile")
def update_profile(user_data: dict, user_id: str = Depends(get_current_user)):
    update_user(user_id, user_data)
    return {"message": "Profile updated"}

@router.delete("/account")
def delete_account(user_id: str = Depends(get_current_user)):
    delete_user(user_id)
    return {"message": "Account deleted"}