from typing import List, Dict, Any
from datetime import datetime
import logging
from ..services.risk_service import get_all_risk_scores
from ..services.anomaly_service import detect_anomalies

logger = logging.getLogger(__name__)

_alerts_cache: List[Dict[str, Any]] = []


def generate_alerts():
    """Generate alerts based on risk scores and anomalies from all documents."""
    global _alerts_cache
    _alerts_cache = []
    
    # Check high-risk documents
    risk_scores = get_all_risk_scores()
    for score_data in risk_scores:
        if score_data["score"] >= 70:
            from ..services.document_service import load_document_metadata
            metadata = load_document_metadata(score_data["document_id"])
            filename = metadata.get("filename", "Unknown") if metadata else "Unknown"
            _alerts_cache.append({
                "alert_id": f"risk_{score_data['document_id']}",
                "type": "high_risk",
                "severity": "high",
                "message": f"High risk document detected: {filename} (Score: {score_data['score']})",
                "timestamp": datetime.now().isoformat(),
                "document_id": score_data["document_id"]
            })
    
    # Check anomalies from transactions.csv
    anomalies = detect_anomalies()
    for anomaly in anomalies[:10]:  # Limit to top 10
        _alerts_cache.append({
            "alert_id": f"anomaly_{anomaly['transaction_id']}",
            "type": "anomaly",
            "severity": "medium",
            "message": f"Anomalous transaction detected: {anomaly['transaction_id']} (Amount: ${anomaly['amount']:.2f})",
            "timestamp": datetime.now().isoformat(),
            "document_id": None
        })
    
    # Check anomalies from uploaded documents
    from ..services.document_anomaly_aggregator import get_all_document_anomalies
    from ..services.document_service import load_document_metadata
    doc_anomalies = get_all_document_anomalies()
    for anomaly in doc_anomalies[:10]:  # Limit to top 10
        if anomaly.get("anomaly_type", "").startswith("Document:"):
            metadata = load_document_metadata(anomaly.get("document_id"))
            filename = metadata.get("filename", "Unknown") if metadata else "Unknown"
            _alerts_cache.append({
                "alert_id": f"doc_anomaly_{anomaly['document_id']}",
                "type": "document_anomaly",
                "severity": "medium",
                "message": f"Anomaly detected in document: {filename} - {anomaly.get('anomaly_type', 'Unknown')}",
                "timestamp": datetime.now().isoformat(),
                "document_id": anomaly.get("document_id")
            })


def get_alerts() -> List[Dict[str, Any]]:
    """Get all alerts."""
    if not _alerts_cache:
        generate_alerts()
    return _alerts_cache
