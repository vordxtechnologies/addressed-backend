from fastapi import APIRouter, HTTPException
import firebase_admin
from firebase_admin import auth, credentials
from app.core.security import create_jwt_token

# Initialize Firebase Admin SDK
cred = credentials.Certificate("addressed-firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

router = APIRouter()

@router.post("/signup")
def signup(email: str, password: str):
    try:
        user = auth.create_user(email=email, password=password)
        return {"message": "User created", "uid": user.uid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        jwt_token = create_jwt_token(decoded_token["uid"])
        return {"access_token": jwt_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
