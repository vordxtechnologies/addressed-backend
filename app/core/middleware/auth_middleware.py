from fastapi import Request
from fastapi.responses import JSONResponse
from firebase_admin.exceptions import FirebaseError
from typing import Callable

async def auth_middleware(request: Request, call_next: Callable):
    try:
        response = await call_next(request)
        return response
    except FirebaseError as e:
        return JSONResponse(
            status_code=401,
            content={"detail": f"Firebase authentication error: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )