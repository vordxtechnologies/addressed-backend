from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config.settings import get_settings
from app.api.v1.routes import api_router
from app.api.v1.security import security_scheme

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    Addressed API - Backend service for handling various tools and functionalities.
    
    ## Authentication
    All protected endpoints require a valid Firebase token in the Authorization header:
    `Authorization: Bearer your-firebase-token`
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)



# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router with version prefix
app.include_router(api_router, prefix=settings.API_V1_STR)
