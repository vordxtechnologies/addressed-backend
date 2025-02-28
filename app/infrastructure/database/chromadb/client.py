# from chromadb import Client
# from chromadb.config import Settings

# # Initialize ChromaDB client with default settings
# chroma_client = Client(Settings())

# def get_chroma_collection(collection_name: str):
#     return chroma_client.get_collection(collection_name)

from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings
from chromadb.api import Collection
from app.core.config.settings import get_settings
from app.core.logging.logging_config import logger
from app.shared.exceptions.base import AppException
from tenacity import retry, stop_after_attempt, wait_exponential

settings = get_settings()

class ChromaDBClient:
    """Client for interacting with ChromaDB vector database"""
    
    _instance = None
    _max_retries = 3
    _retry_delay = 1
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_client()
            self.logger = logger
            self._initialized = True
            
    def _initialize_client(self):
        """Initialize ChromaDB client with retry mechanism"""
        try:
            self.client = chromadb.Client(Settings(
                chroma_api_impl="rest",
                chroma_server_host=settings.CHROMADB_HOST,
                chroma_server_http_port=settings.CHROMADB_PORT,
                chroma_server_ssl_enabled=settings.CHROMADB_SSL_ENABLED
            ))
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise AppException("ChromaDB connection failed")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Collection:
        """Get or create a collection with retry mechanism"""
        try:
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=metadata or {}
            )
            self.logger.info(f"Successfully accessed collection: {name}")
            return collection
        except Exception as e:
            self.logger.error(f"ChromaDB error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to get/create collection: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to a collection with retry mechanism"""
        try:
            collection = await self.get_or_create_collection(collection_name)
            
            # Validate input
            if not documents:
                raise AppException("No documents provided")
                
            if metadatas and len(metadatas) != len(documents):
                raise AppException("Number of metadatas must match number of documents")
                
            if ids and len(ids) != len(documents):
                raise AppException("Number of ids must match number of documents")
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids or [str(i) for i in range(len(documents))]
            )
            
            self.logger.info(f"Successfully added {len(documents)} documents to collection: {collection_name}")
            
        except Exception as e:
            self.logger.error(f"ChromaDB error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to add documents: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query documents from a collection with retry mechanism"""
        try:
            collection = await self.get_or_create_collection(collection_name)
            
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where
            )
            
            self.logger.info(f"Successfully queried collection: {collection_name}")
            
            return {
                'documents': results['documents'],
                'metadatas': results['metadatas'],
                'distances': results['distances'],
                'ids': results['ids']
            }
            
        except Exception as e:
            self.logger.error(f"ChromaDB error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to query documents: {str(e)}")

    async def delete_collection(self, name: str) -> None:
        """Delete a collection"""
        try:
            self.client.delete_collection(name)
        except Exception as e:
            self.logger.error(f"ChromaDB error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to delete collection: {str(e)}")

    async def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.list_collections()
            return [collection.name for collection in collections]
        except Exception as e:
            self.logger.error(f"ChromaDB error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to list collections: {str(e)}")

    async def get_collection_info(self, name: str) -> Dict[str, Any]:
        """Get collection information"""
        try:
            collection = await self.get_or_create_collection(name)
            return {
                'name': collection.name,
                'metadata': collection.metadata,
                'count': collection.count()
            }
        except Exception as e:
            self.logger.error(f"ChromaDB error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to get collection info: {str(e)}")
