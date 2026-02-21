import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from .document_service import extract_text_from_file
from .rag_service import index_document

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
BANK_DOCS_DIR = DATA_DIR / "bank_docs"


def load_bank_documents() -> List[Dict[str, Any]]:
    """Load all documents from bank_docs directory."""
    documents = []
    
    if not BANK_DOCS_DIR.exists():
        logger.warning(f"Bank docs directory not found: {BANK_DOCS_DIR}")
        return documents
    
    for file_path in BANK_DOCS_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.docx', '.txt', '.md']:
            try:
                text, error = extract_text_from_file(file_path, file_path.name)
                if text:
                    documents.append({
                        "filename": file_path.name,
                        "file_path": str(file_path),
                        "text": text,
                        "document_id": f"bank_doc_{file_path.stem}"
                    })
                    logger.info(f"Loaded bank document: {file_path.name}")
                elif error:
                    logger.warning(f"Could not extract text from {file_path.name}: {error}")
            except Exception as e:
                logger.error(f"Error loading bank document {file_path.name}: {e}")
    
    return documents


def index_bank_documents():
    """Index all bank documents for RAG."""
    documents = load_bank_documents()
    
    for doc in documents:
        try:
            index_document(doc["document_id"], doc["text"])
            logger.info(f"Indexed bank document: {doc['filename']}")
        except Exception as e:
            logger.error(f"Error indexing bank document {doc['filename']}: {e}")
    
    return len(documents)
