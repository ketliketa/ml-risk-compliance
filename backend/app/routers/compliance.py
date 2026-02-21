from fastapi import APIRouter, HTTPException
from ..models import ComplianceCheckResponse, ComplianceViolation
from ..services.document_service import load_document_metadata
from ..services.compliance_service import check_compliance

router = APIRouter()


@router.post("/api/compliance/check/{document_id}", response_model=ComplianceCheckResponse)
async def check_compliance_endpoint(document_id: str):
    """Check compliance for a document."""
    metadata = load_document_metadata(document_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    text = metadata.get("text", "")
    violations_data = check_compliance(text)
    
    violations = [
        ComplianceViolation(
            requirement_id=v.get("requirement_id", "unknown"),
            requirement_text=v.get("requirement_text", ""),
            evidence=v.get("evidence", ""),
            severity=v.get("severity", "medium")
        )
        for v in violations_data
    ]
    
    return ComplianceCheckResponse(
        document_id=document_id,
        violations=violations,
        total_violations=len(violations)
    )
