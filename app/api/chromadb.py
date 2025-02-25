from chromadb import ChromaClient

# Initialize ChromaDB client
chroma_client = ChromaClient(api_key="your_chromadb_api_key")

def get_chroma_collection(collection_name: str):
    return chroma_client.get_collection(collection_name)