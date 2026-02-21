from typing import List, Dict, Any
from ..services.document_service import get_all_documents
import logging

logger = logging.getLogger(__name__)


def get_all_document_anomalies() -> List[Dict[str, Any]]:
    """Get all anomalies from all uploaded documents."""
    documents = get_all_documents()
    all_anomalies = []
    
    for doc_id, metadata in documents.items():
        filename = metadata.get("filename", "Unknown")
        
        # CSV anomalies
        csv_anomalies = metadata.get("csv_anomalies", {})
        if csv_anomalies and csv_anomalies.get("anomalies"):
            for anomaly in csv_anomalies["anomalies"]:
                all_anomalies.append({
                    "document_id": doc_id,
                    "filename": filename,
                    "transaction_id": f"{doc_id}_{anomaly.get('row_index', 'unknown')}",
                    "amount": anomaly.get("value", 0.0),
                    "date": metadata.get("uploaded_at", "unknown"),
                    "customer_id": f"doc_{doc_id}",
                    "anomaly_type": f"CSV: {anomaly.get('anomaly_type', 'unknown')}",
                    "z_score": anomaly.get("z_score", 0.0)
                })
        
        # Document anomalies
        doc_anomalies = metadata.get("document_anomalies", {})
        if doc_anomalies and doc_anomalies.get("anomalies"):
            for anomaly in doc_anomalies["anomalies"]:
                if anomaly.get("severity") in ["high", "medium"]:
                    all_anomalies.append({
                        "document_id": doc_id,
                        "filename": filename,
                        "transaction_id": f"{doc_id}_anom_{anomaly.get('anomaly_type', 'unknown')}",
                        "amount": 0.0,
                        "date": metadata.get("uploaded_at", "unknown"),
                        "customer_id": f"doc_{doc_id}",
                        "anomaly_type": f"Document: {anomaly.get('anomaly_type', 'unknown')}",
                        "z_score": 0.0
                    })
    
    return all_anomalies
