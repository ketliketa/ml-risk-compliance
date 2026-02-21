from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid
from datetime import datetime
from pathlib import Path
import logging

from ..models import DocumentUploadResponse, DocumentMetadata
from ..services.document_service import (
    save_document_metadata,
    load_document_metadata,
    get_all_documents,
    extract_text_from_file,
    analyze_document,
    get_safe_filename,
    delete_document,
    UPLOADS_DIR
)
from ..services.rag_service import index_document
from ..services.compliance_service import check_compliance
from ..services.risk_service import calculate_risk_score
from ..services.csv_anomaly_service import detect_csv_anomalies
from ..services.document_anomaly_service import detect_document_anomalies

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    try:
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Save file
        safe_filename = get_safe_filename(file.filename)
        file_path = UPLOADS_DIR / safe_filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"File saved: {file_path}")
        
        # Extract text
        text, error = extract_text_from_file(file_path, file.filename)
        
        if error:
            return DocumentUploadResponse(
                document_id=document_id,
                filename=file.filename,
                message=error,
                text_length=0
            )
        
        # Analyze document
        analysis = analyze_document(text)
        
        # Check compliance
        violations = check_compliance(text)
        
        # Calculate risk score
        risk_score = calculate_risk_score(document_id, text, violations)
        
        # Detect anomalies for CSV files
        csv_anomalies = None
        if Path(file.filename).suffix.lower() == '.csv':
            csv_anomalies = detect_csv_anomalies(file_path, file.filename)
            logger.info(f"Detected {csv_anomalies.get('anomaly_count', 0)} anomalies in CSV file")
        
        # Detect anomalies for ALL document types
        document_anomalies = detect_document_anomalies(text, file.filename)
        logger.info(f"Detected {document_anomalies.get('anomaly_count', 0)} anomalies in document")
        
        # Store metadata
        metadata = {
            "document_id": document_id,
            "filename": file.filename,
            "safe_filename": safe_filename,
            "uploaded_at": datetime.now().isoformat(),
            "text_length": len(text),
            "file_type": Path(file.filename).suffix,
            "analysis": analysis,
            "violations": violations,
            "risk_score": risk_score,
            "csv_anomalies": csv_anomalies,  # Store CSV-specific anomalies
            "document_anomalies": document_anomalies,  # Store general document anomalies
            "text": text  # Store text for later retrieval
        }
        
        save_document_metadata(document_id, metadata)
        
        # Index for RAG
        index_document(document_id, text)
        
        # Delete physical file after processing (keep only metadata and text)
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Physical file deleted after processing: {file_path}")
        except Exception as e:
            logger.warning(f"Could not delete physical file: {e}")
        
        # Generate report automatically after document processing
        try:
            from ..services.report_service import generate_report
            report_result = generate_report()
            logger.info(f"Auto-generated report: {report_result.get('report_id')}")
        except Exception as e:
            logger.warning(f"Could not auto-generate report: {e}")
        
        logger.info(f"Document processed: {document_id}")
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            message="Document uploaded and processed successfully",
            text_length=len(text),
            analysis=analysis
        )
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/documents", response_model=List[DocumentMetadata])
async def list_documents():
    """List all documents."""
    documents = get_all_documents()
    result = []
    
    for doc_id, metadata in documents.items():
        result.append(DocumentMetadata(
            document_id=doc_id,
            filename=metadata.get("filename", ""),
            uploaded_at=metadata.get("uploaded_at", ""),
            text_length=metadata.get("text_length", 0),
            file_type=metadata.get("file_type", ""),
            analysis=metadata.get("analysis")
        ))
    
    return result


@router.get("/api/documents/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str):
    """Get document details."""
    metadata = load_document_metadata(document_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentMetadata(
        document_id=document_id,
        filename=metadata.get("filename", ""),
        uploaded_at=metadata.get("uploaded_at", ""),
        text_length=metadata.get("text_length", 0),
        file_type=metadata.get("file_type", ""),
        analysis=metadata.get("analysis"),
        csv_anomalies=metadata.get("csv_anomalies"),
        document_anomalies=metadata.get("document_anomalies")
    )


@router.delete("/api/documents/{document_id}")
async def delete_document_endpoint(document_id: str):
    """Delete a document."""
    success = delete_document(document_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Also remove from RAG index
    try:
        from ..services.rag_service import _embeddings_cache, _documents_cache
        # Remove chunks for this document
        keys_to_remove = [k for k in _embeddings_cache.keys() if k.startswith(f"{document_id}_chunk_")]
        for key in keys_to_remove:
            _embeddings_cache.pop(key, None)
            _documents_cache.pop(key, None)
        logger.info(f"Removed {len(keys_to_remove)} chunks from RAG index")
    except Exception as e:
        logger.warning(f"Error removing from RAG index: {e}")
    
    return {"message": "Document deleted successfully", "document_id": document_id}
