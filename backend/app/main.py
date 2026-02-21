from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .routers import health, documents, rag, compliance, risk, anomalies, alerts, reports, chat
from .services.document_service import get_all_documents
from .services.rag_service import index_document
from .services.bank_docs_service import index_bank_documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("ML Project API starting up...")
    
    # Load or build PDF RAG index
    try:
        from .services.pdf_rag_service import load_index, build_index
        if not load_index():
            logging.info("No existing RAG index found, building new index...")
            result = build_index()
            if result.get("status") == "success":
                logging.info(f"Built RAG index: {result.get('num_chunks', 0)} chunks from {result.get('num_documents', 0)} documents")
        else:
            logging.info("Loaded existing RAG index")
    except Exception as e:
        logging.warning(f"Error loading/building PDF RAG index: {e}")
    
    # Index bank documents from bank_docs directory (legacy)
    try:
        count = index_bank_documents()
        logging.info(f"Indexed {count} bank documents from bank_docs directory")
    except Exception as e:
        logging.warning(f"Error indexing bank documents: {e}")
    
    # Reload existing uploaded documents into RAG index
    try:
        documents = get_all_documents()
        for doc_id, metadata in documents.items():
            text = metadata.get("text", "")
            if text:
                index_document(doc_id, text)
                logging.info(f"Reloaded document {doc_id} into RAG index")
    except Exception as e:
        logging.warning(f"Error reloading documents into RAG: {e}")
    
    yield
    
    # Shutdown (if needed)
    logging.info("ML Project API shutting down...")


app = FastAPI(title="ML Project API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(rag.router)
app.include_router(compliance.router)
app.include_router(risk.router)
app.include_router(anomalies.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(chat.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
