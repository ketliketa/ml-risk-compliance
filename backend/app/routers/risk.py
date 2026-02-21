from fastapi import APIRouter
from ..models import RiskScore, RiskDashboard
from ..services.risk_service import get_all_risk_scores, get_risk_dashboard

router = APIRouter()


@router.get("/api/risk/scores", response_model=list[RiskScore])
async def get_risk_scores():
    """Get all risk scores."""
    scores = get_all_risk_scores()
    return [RiskScore(**score) for score in scores]


@router.get("/api/risk/dashboard", response_model=RiskDashboard)
async def get_risk_dashboard_endpoint():
    """Get risk dashboard."""
    dashboard = get_risk_dashboard()
    return RiskDashboard(**dashboard)
