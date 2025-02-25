from fastapi import APIRouter, HTTPException
from app.services.ai_service import query_chroma, huggingface_infer, deepseeck_r1_infer, janus_pro_infer, langchain_query

router = APIRouter()

@router.post("/chroma-query")
def chroma_query(collection_name: str, query: str):
    try:
        results = query_chroma(collection_name, query)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/huggingface-infer")
def huggingface_infer(input_data: dict):
    try:
        results = huggingface_infer(input_data)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/deepseeck-r1")
def deepseeck_r1_infer(input_data: dict):
    try:
        results = deepseeck_r1_infer(input_data)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/janus-pro")
def janus_pro_infer(input_data: dict):
    try:
        results = janus_pro_infer(input_data)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/langchain")
def langchain_query(input_data: dict):
    try:
        results = langchain_query(input_data)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))