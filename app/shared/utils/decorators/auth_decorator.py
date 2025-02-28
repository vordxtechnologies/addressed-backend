from functools import wraps
from typing import List, Optional, Callable
from fastapi import HTTPException, Request
from app.shared.exceptions.base import AuthenticationError, AuthorizationError
from app.core.logging.logging_config import logger

def require_auth():
    """Decorator to require authentication for endpoints"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                raise AuthenticationError("No request object found")

            token_data = getattr(request.state, "token_data", None)
            if not token_data:
                raise AuthenticationError("Authentication required")

            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_roles(roles: List[str]):
    """Decorator to require specific roles"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                raise AuthenticationError("No request object found")

            token_data = getattr(request.state, "token_data", None)
            if not token_data:
                raise AuthenticationError("Authentication required")

            user_roles = token_data.get("roles", [])
            if not any(role in user_roles for role in roles):
                raise AuthorizationError("Insufficient permissions")

            return await func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit(
    requests: int,
    period: int = 60,
    by_ip: bool = True,
    by_user: bool = False
):
    """Decorator for rate limiting specific endpoints"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from app.infrastructure.database.redis.client import redis_client
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            
            if not request:
                return await func(*args, **kwargs)

            keys = []
            if by_ip:
                keys.append(f"rate_limit:ip:{request.client.host}")
            if by_user and hasattr(request.state, "token_data"):
                keys.append(f"rate_limit:user:{request.state.token_data['uid']}")

            for key in keys:
                current = redis_client.get(key)
                if current and int(current) >= requests:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Try again in {period} seconds"
                    )
                redis_client.incr(key)
                redis_client.expire(key, period)

            return await func(*args, **kwargs)
        return wrapper
    return decorator

def log_execution(include_args: bool = False):
    """Decorator to log function execution with timing"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            # Log function entry
            log_data = {
                "function": func.__name__,
                "module": func.__module__
            }
            
            if include_args:
                log_data["args"] = str(args)
                log_data["kwargs"] = str(kwargs)
            
            logger.info(f"Executing {func.__name__}", extra=log_data)
            
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                logger.info(
                    f"Completed {func.__name__}",
                    extra={
                        **log_data,
                        "execution_time_ms": execution_time
                    }
                )
                return result
                
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    exc_info=True,
                    extra=log_data
                )
                raise
                
        return wrapper
    return decorator
