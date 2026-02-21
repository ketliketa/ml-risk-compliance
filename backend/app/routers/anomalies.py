from fastapi import APIRouter
from ..models import AnomaliesResponse, Anomaly
from ..services.anomaly_service import detect_anomalies
from ..services.document_anomaly_aggregator import get_all_document_anomalies

router = APIRouter()


@router.get("/api/anomalies", response_model=AnomaliesResponse)
async def get_anomalies():
    """Get detected anomalies from transactions.csv and all uploaded documents."""
    # Get anomalies from transactions.csv
    transaction_anomalies = detect_anomalies()
    
    # Get anomalies from all uploaded documents
    document_anomalies = get_all_document_anomalies()
    
    # Combine all anomalies
    all_anomalies = transaction_anomalies + document_anomalies
    
    anomalies = [Anomaly(**anom) for anom in all_anomalies]
    return AnomaliesResponse(anomalies=anomalies, total=len(anomalies))
