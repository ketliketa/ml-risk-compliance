from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class HealthResponse(BaseModel):
    status: str


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    message: str
    text_length: int
    analysis: Optional[Dict[str, Any]] = None


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    uploaded_at: str
    text_length: int
    file_type: str
    analysis: Optional[Dict[str, Any]] = None
    csv_anomalies: Optional[Dict[str, Any]] = None
    document_anomalies: Optional[Dict[str, Any]] = None


class RAGQueryResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]


class ComplianceViolation(BaseModel):
    requirement_id: str
    requirement_text: str
    evidence: str
    severity: str


class ComplianceCheckResponse(BaseModel):
    document_id: str
    violations: List[ComplianceViolation]
    total_violations: int


class RiskScore(BaseModel):
    document_id: str
    score: int
    factors: List[str]


class RiskDashboard(BaseModel):
    total_documents: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    average_score: float
    scores: List[RiskScore]


class Anomaly(BaseModel):
    transaction_id: str
    amount: float
    date: str
    customer_id: str
    anomaly_type: str
    z_score: float


class AnomaliesResponse(BaseModel):
    anomalies: List[Anomaly]
    total: int


class Alert(BaseModel):
    alert_id: str
    type: str
    severity: str
    message: str
    timestamp: str
    document_id: Optional[str] = None


class AlertsResponse(BaseModel):
    alerts: List[Alert]
    total: int


class ReportResponse(BaseModel):
    report_id: str
    pdf_path: str
    excel_path: str
    message: str
