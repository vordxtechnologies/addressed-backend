from fastapi.security import HTTPBearer

security_scheme = HTTPBearer(
    scheme_name="Firebase",
    description="Enter your Firebase JWT token",
    bearerFormat="JWT"
)