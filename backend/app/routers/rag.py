from fastapi import APIRouter, Query
from ..models import RAGQueryResponse
from ..services.rag_service import query_rag, query_rag_with_context, generate_answer

router = APIRouter()


@router.get("/api/rag/query", response_model=RAGQueryResponse)
async def query_rag_endpoint(
    q: str = Query(..., description="Query string"),
    document_id: str = Query(None, description="Optional document ID to filter by")
):
    """Query the RAG system with optional document filtering."""
    if document_id:
        results = query_rag_with_context(q, document_id, top_k=5)
    else:
        results = query_rag(q, top_k=5)
    
    # Generate a natural answer from the results
    if results:
        answer = generate_answer(q, results)
        # Add the generated answer to the first result
        if results:
            results[0]["answer"] = answer
    
    return RAGQueryResponse(query=q, results=results)
