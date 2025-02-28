from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, Optional, List
from app.services.ai_service import AIService
from app.core.security.firebase_auth import verify_firebase_token
from app.shared.utils.decorators.auth_decorator import require_auth, rate_limit
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["AI Services"])
ai_service = AIService()

class TextAnalysisRequest(BaseModel):
    text: str
    context_collection: str
    instruction: str
    n_context: Optional[int] = 3

class ProductRecommendationRequest(BaseModel):
    user_input: str
    max_products: Optional[int] = 5

class DocumentRequest(BaseModel):
    document: str
    metadata: Optional[Dict[str, Any]] = None
    collection_name: Optional[str] = "documents"

class SearchRequest(BaseModel):
    query: str
    collection_name: str
    n_results: Optional[int] = 5
    rerank: Optional[bool] = True

@router.post("/analyze")
@require_auth()
@rate_limit(requests=30, period=60)
async def analyze_text(
    request: TextAnalysisRequest,
    token_data: Dict[str, Any] = Depends(verify_firebase_token)
) -> Dict[str, Any]:
    """Analyze text with context from ChromaDB"""
    try:
        return await ai_service.analyze_text_with_context(
            text=request.text,
            context_collection=request.context_collection,
            instruction=request.instruction,
            n_context=request.n_context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend")
@require_auth()
@rate_limit(requests=20, period=60)
async def get_recommendations(
    request: ProductRecommendationRequest,
    token_data: Dict[str, Any] = Depends(verify_firebase_token)
) -> Dict[str, Any]:
    """Get personalized product recommendations"""
    try:
        return await ai_service.generate_product_recommendations(
            user_input=request.user_input,
            max_products=request.max_products
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents")
@require_auth()
@rate_limit(requests=50, period=60)
async def process_document(
    request: DocumentRequest,
    token_data: Dict[str, Any] = Depends(verify_firebase_token)
) -> Dict[str, Any]:
    """Store and analyze document"""
    try:
        return await ai_service.store_and_analyze_document(
            document=request.document,
            metadata=request.metadata,
            collection_name=request.collection_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
@require_auth()
@rate_limit(requests=50, period=60)
async def semantic_search(
    request: SearchRequest,
    token_data: Dict[str, Any] = Depends(verify_firebase_token)
) -> Dict[str, Any]:
    """Perform semantic search with optional reranking"""
    try:
        return await ai_service.semantic_search(
            query=request.query,
            collection_name=request.collection_name,
            n_results=request.n_results,
            rerank=request.rerank
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 