from chromadb import Client
from chromadb.config import Settings

# Initialize ChromaDB client with default settings
chroma_client = Client(Settings())

def get_chroma_collection(collection_name: str):
    return chroma_client.get_collection(collection_name)
