from fastapi import FastAPI
from app.api import auth, user, ai, data
from app.core.exceptions import http_exception_handler, validation_exception_handler, generic_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title="Addressed FastAPI Backend",
    description="API for handling authentication, AI, and data processing",
    version="1.0.0"
)

# Include Routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/user", tags=["User Management"])
app.include_router(ai.router, prefix="/ai", tags=["AI Processing"])
app.include_router(data.router, prefix="/data", tags=["Data Processing"])
# app.include_router(scrape.router, prefix="/scrape", tags=["Web Scraping"])

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Root Route
@app.get("/")
def home():
    return {"message": "FastAPI backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
