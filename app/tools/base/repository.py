from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel
from app.core.logging.logging_config import logger
from app.shared.utils.decorators.auth_decorator import log_execution

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """
    Base repository with common database operations
    
    Generic type T should be a Pydantic model
    """
    
    def __init__(self, db: Any, collection_name: str):
        self.db = db
        self.collection_name = collection_name
        self.logger = logger

    @log_execution()
    async def get_all(self, **kwargs) -> List[T]:
        """Get all items from collection"""
        collection = self.db.collection(self.collection_name)
        docs = await collection.get()
        return [self._to_model(doc.to_dict()) for doc in docs]

    @log_execution()
    async def get_by_id(self, id: str, **kwargs) -> Optional[T]:
        """Get item by ID"""
        doc = await self.db.collection(self.collection_name).document(id).get()
        return self._to_model(doc.to_dict()) if doc.exists else None

    @log_execution()
    async def create(self, item: T, **kwargs) -> T:
        """Create new item"""
        doc_ref = self.db.collection(self.collection_name).document()
        item_dict = item.dict()
        item_dict['id'] = doc_ref.id
        await doc_ref.set(item_dict)
        return self._to_model(item_dict)

    @log_execution()
    async def update(self, id: str, item: T, **kwargs) -> T:
        """Update existing item"""
        doc_ref = self.db.collection(self.collection_name).document(id)
        item_dict = item.dict(exclude={'id'})
        await doc_ref.update(item_dict)
        updated_doc = await doc_ref.get()
        return self._to_model(updated_doc.to_dict())

    @log_execution()
    async def delete(self, id: str, **kwargs) -> bool:
        """Delete item"""
        await self.db.collection(self.collection_name).document(id).delete()
        return True

    @log_execution()
    async def bulk_create(self, items: List[T], **kwargs) -> List[T]:
        """Bulk create items"""
        batch = self.db.batch()
        created_items = []
        
        for item in items:
            doc_ref = self.db.collection(self.collection_name).document()
            item_dict = item.dict()
            item_dict['id'] = doc_ref.id
            batch.set(doc_ref, item_dict)
            created_items.append(self._to_model(item_dict))
            
        await batch.commit()
        return created_items

    @log_execution()
    async def bulk_update(self, items: List[Dict[str, Any]], **kwargs) -> List[T]:
        """Bulk update items"""
        batch = self.db.batch()
        updated_items = []
        
        for item in items:
            doc_ref = self.db.collection(self.collection_name).document(item['id'])
            update_data = {k: v for k, v in item.items() if k != 'id'}
            batch.update(doc_ref, update_data)
            
        await batch.commit()
        
        # Fetch updated documents
        for item in items:
            doc = await self.db.collection(self.collection_name).document(item['id']).get()
            updated_items.append(self._to_model(doc.to_dict()))
            
        return updated_items

    @log_execution()
    async def search(self, query: Dict[str, Any], **kwargs) -> List[T]:
        """Search items based on query"""
        collection_ref = self.db.collection(self.collection_name)
        
        # Apply filters from query
        for field, value in query.items():
            if isinstance(value, dict):
                operator = value.get('operator', '==')
                collection_ref = collection_ref.where(field, operator, value.get('value'))
            else:
                collection_ref = collection_ref.where(field, '==', value)
                
        docs = await collection_ref.get()
        return [self._to_model(doc.to_dict()) for doc in docs]

    async def exists(self, id: str, **kwargs) -> bool:
        """Check if item exists"""
        doc = await self.db.collection(self.collection_name).document(id).get()
        return doc.exists

    async def count(self, query: Optional[Dict[str, Any]] = None, **kwargs) -> int:
        """Count items matching query"""
        collection_ref = self.db.collection(self.collection_name)
        
        if query:
            for field, value in query.items():
                if isinstance(value, dict):
                    operator = value.get('operator', '==')
                    collection_ref = collection_ref.where(field, operator, value.get('value'))
                else:
                    collection_ref = collection_ref.where(field, '==', value)
                    
        docs = await collection_ref.get()
        return len(docs)

    def _to_model(self, data: Dict[str, Any]) -> T:
        """Convert dictionary to model instance"""
        raise NotImplementedError("Implement in derived class")
