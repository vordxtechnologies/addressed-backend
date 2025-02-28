# app/tools/base/controller.py
from typing import Any, Dict, Generic, List, Optional, TypeVar
from fastapi import HTTPException, Request
from app.shared.exceptions.base import AppException, NotFoundError
from app.core.logging.logging_config import logger
from app.shared.utils.helpers.general_helpers import format_response
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseController(Generic[T]):
    """
    Base controller with common CRUD operations and utility methods
    
    Generic type T should be a Pydantic model
    """
    
    def __init__(self, service: Any):
        self.service = service
        self.logger = logger

    async def handle_request(self, operation: str, *args, **kwargs) -> Dict[str, Any]:
        """Generic request handler with logging and error handling"""
        request_id = kwargs.get('request_id', 'unknown')
        
        try:
            self.logger.info(
                f"Handling {operation} request",
                extra={
                    "operation": operation,
                    "request_id": request_id,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
            )
            
            result = await getattr(self.service, operation)(*args, **kwargs)
            
            self.logger.info(
                f"Successfully handled {operation} request",
                extra={
                    "operation": operation,
                    "request_id": request_id
                }
            )
            
            return format_response(result)
            
        except AppException as e:
            self.logger.error(
                f"Application error in {operation}",
                extra={
                    "operation": operation,
                    "request_id": request_id,
                    "error": str(e)
                }
            )
            raise
            
        except Exception as e:
            self.logger.error(
                f"Unexpected error in {operation}",
                exc_info=True,
                extra={
                    "operation": operation,
                    "request_id": request_id
                }
            )
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all(self, request: Request, **kwargs) -> Dict[str, Any]:
        """Get all items"""
        return await self.handle_request('get_all', **kwargs)

    async def get_by_id(self, id: str, request: Request, **kwargs) -> Dict[str, Any]:
        """Get item by ID"""
        return await self.handle_request('get_by_id', id, **kwargs)

    async def create(self, item: T, request: Request, **kwargs) -> Dict[str, Any]:
        """Create new item"""
        return await self.handle_request('create', item, **kwargs)

    async def update(self, id: str, item: T, request: Request, **kwargs) -> Dict[str, Any]:
        """Update existing item"""
        return await self.handle_request('update', id, item, **kwargs)

    async def delete(self, id: str, request: Request, **kwargs) -> Dict[str, Any]:
        """Delete item"""
        return await self.handle_request('delete', id, **kwargs)

    async def bulk_create(self, items: List[T], request: Request, **kwargs) -> Dict[str, Any]:
        """Bulk create items"""
        return await self.handle_request('bulk_create', items, **kwargs)

    async def bulk_update(self, items: List[Dict[str, Any]], request: Request, **kwargs) -> Dict[str, Any]:
        """Bulk update items"""
        return await self.handle_request('bulk_update', items, **kwargs)

    async def search(self, query: Dict[str, Any], request: Request, **kwargs) -> Dict[str, Any]:
        """Search items"""
        return await self.handle_request('search', query, **kwargs)

    def validate_id(self, id: str) -> None:
        """Validate ID format"""
        if not id or not isinstance(id, str):
            raise ValueError("Invalid ID format")

    def validate_item(self, item: T) -> None:
        """Validate item data"""
        if not item:
            raise ValueError("Item cannot be empty")
            
    async def handle_file_upload(
        self,
        file: Any,
        allowed_types: Optional[List[str]] = None,
        max_size: Optional[int] = None
    ) -> str:
        """Handle file upload with validation"""
        if not file:
            raise ValueError("No file provided")
            
        if allowed_types and file.content_type not in allowed_types:
            raise ValueError(f"Invalid file type. Allowed types: {', '.join(allowed_types)}")
            
        if max_size and file.size > max_size:
            raise ValueError(f"File too large. Maximum size: {max_size/1024/1024}MB")

# app/tools/base/service.py
class BaseService:
    def __init__(self, repository):
        self.repository = repository

# app/tools/base/repository.py
class BaseRepository:
    def __init__(self, db):
        self.db = db