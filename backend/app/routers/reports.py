from fastapi import APIRouter
from ..models import ReportResponse
from ..services.report_service import generate_report

router = APIRouter()


@router.post("/api/reports/generate", response_model=ReportResponse)
async def generate_report_endpoint():
    """Generate PDF and Excel reports."""
    result = generate_report()
    return ReportResponse(**result)
