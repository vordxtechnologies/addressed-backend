# app/core/security/firebase_auth.py
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
from typing import Dict, Any
from app.core.config.settings import settings

security = HTTPBearer()

def initialize_firebase():
    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        return firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase initialization error: {str(e)}")
        raise

firebase_app = initialize_firebase()

async def verify_firebase_token(credential: Security = Security(security)) -> Dict[str, Any]:
    """
    Verify Firebase JWT token from request Authorization header
    Returns decoded token if valid, raises HTTPException if invalid
    """
    try:
        decoded_token = auth.verify_id_token(credential.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}"
        )