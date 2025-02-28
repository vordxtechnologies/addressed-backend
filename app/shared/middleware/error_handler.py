from fastapi import Request
from fastapi.responses import JSONResponse
from app.shared.exceptions.base import AppException
from app.core.logging.logging_config import logger
from typing import Union, Dict, Any

async def error_handler_middleware(
    request: Request,
    call_next: callable
) -> Union[JSONResponse, Any]:
    try:
        return await call_next(request)
    except AppException as e:
        logger.error(
            f"Application error: {str(e)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": e.status_code,
                **e.extra
            }
        )
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.message, **e.extra}
        )
    except Exception as e:
        logger.error(
            f"Unhandled error: {str(e)}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method
            }
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
