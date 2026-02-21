from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from ..services.pdf_rag_service import query_rag, build_index, get_index_status

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    source: str
    page: int
    snippet: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


class IndexStatusResponse(BaseModel):
    indexed: bool
    num_documents: int
    num_chunks: int


@router.post("/api/chat/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """Ask a question to the RAG chatbot."""
    try:
        result = query_rag(request.question)
        
        # Convert sources to Source models
        sources = [
            Source(
                source=s["source"],
                page=s["page"],
                snippet=s["snippet"],
                score=s["score"]
            )
            for s in result["sources"]
        ]
        
        return ChatResponse(
            answer=result["answer"],
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.post("/api/chat/reindex")
async def reindex_documents():
    """Rebuild the RAG index from bank_docs directory."""
    try:
        result = build_index()
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Indexing failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebuilding index: {str(e)}")


@router.get("/api/chat/status", response_model=IndexStatusResponse)
async def get_status():
    """Get the status of the RAG index."""
    try:
        status = get_index_status()
        return IndexStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")
