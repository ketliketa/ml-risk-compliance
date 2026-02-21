from fastapi import APIRouter
from ..models import AlertsResponse, Alert
from ..services.alert_service import get_alerts

router = APIRouter()


@router.get("/api/alerts", response_model=AlertsResponse)
async def get_alerts_endpoint():
    """Get all alerts."""
    alerts_data = get_alerts()
    alerts = [Alert(**alert) for alert in alerts_data]
    return AlertsResponse(alerts=alerts, total=len(alerts))
