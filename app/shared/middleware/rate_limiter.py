from fastapi import Request
from fastapi.responses import JSONResponse
from app.infrastructure.database.redis.client import redis_client
import time
from typing import Optional

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 60,
        key_prefix: str = "rate_limit"
    ):
        self.requests_per_minute = requests_per_minute
        self.key_prefix = key_prefix

    async def __call__(
        self,
        request: Request,
        call_next: callable
    ):
        client_ip = request.client.host
        key = f"{self.key_prefix}:{client_ip}"
        
        # Get current request count
        current = redis_client.get(key)
        current_count = int(current) if current else 0
        
        if current_count >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "retry_after": "60 seconds"
                }
            )
        
        # Increment request count
        pipe = redis_client.pipeline()
        pipe.incr(key)
        if not current:
            pipe.expire(key, 60)  # Reset after 1 minute
        pipe.execute()
        
        return await call_next(request) 