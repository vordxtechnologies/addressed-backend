from app.db.firestore import db
from app.db.redis import cache_data, get_cached_data
from app.models.user import User

def get_user(user_id: str) -> User:
    cached_user = get_cached_data(user_id)
    if cached_user:
        return User(**cached_user)
    
    user_ref = db.collection("users").document(user_id)
    user = user_ref.get()
    if user.exists:
        user_data = user.to_dict()
        cache_data(user_id, user_data)
        return User(**user_data)
    return None

def update_user(user_id: str, user_data: dict) -> None:
    user_ref = db.collection("users").document(user_id)
    user_ref.update(user_data)
    cache_data(user_id, user_data)

def delete_user(user_id: str) -> None:
    user_ref = db.collection("users").document(user_id)
    user_ref.delete()
    cache_data(user_id, None)