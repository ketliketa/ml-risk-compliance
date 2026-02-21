from typing import List, Dict, Any
import logging
from ..services.document_service import get_all_documents
from ..services.compliance_service import check_compliance

logger = logging.getLogger(__name__)


def calculate_risk_score(document_id: str, document_text: str, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate risk score for a document."""
    score = 0
    factors = []
    
    # Base score from violations
    violation_count = len(violations)
    score += violation_count * 15
    if violation_count > 0:
        factors.append(f"{violation_count} compliance violation(s)")
    
    # High severity violations
    high_severity = sum(1 for v in violations if v.get("severity") == "high")
    score += high_severity * 20
    if high_severity > 0:
        factors.append(f"{high_severity} high severity violation(s)")
    
    # Suspicious keywords
    suspicious_keywords = ['fraud', 'suspicious', 'unauthorized', 'breach', 'hack', 'leak']
    found_keywords = [kw for kw in suspicious_keywords if kw.lower() in document_text.lower()]
    score += len(found_keywords) * 10
    if found_keywords:
        factors.append(f"Suspicious keywords: {', '.join(found_keywords)}")
    
    # Risk level keywords
    risk_keywords = ['high risk', 'critical', 'urgent', 'immediate action']
    found_risk = [kw for kw in risk_keywords if kw.lower() in document_text.lower()]
    score += len(found_risk) * 15
    if found_risk:
        factors.append(f"Risk indicators: {', '.join(found_risk)}")
    
    # Cap at 100
    score = min(100, score)
    
    if not factors:
        factors.append("No risk factors detected")
    
    return {
        "document_id": document_id,
        "score": score,
        "factors": factors
    }


def get_all_risk_scores() -> List[Dict[str, Any]]:
    """Get risk scores for all documents."""
    documents = get_all_documents()
    scores = []
    
    for doc_id, metadata in documents.items():
        # Get document text (would need to load from file or cache)
        text = metadata.get("text", "")
        violations = metadata.get("violations", [])
        score_data = calculate_risk_score(doc_id, text, violations)
        scores.append(score_data)
    
    return scores


def get_risk_dashboard() -> Dict[str, Any]:
    """Get risk dashboard data."""
    scores = get_all_risk_scores()
    
    if not scores:
        return {
            "total_documents": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "average_score": 0.0,
            "scores": []
        }
    
    high_risk = sum(1 for s in scores if s["score"] >= 70)
    medium_risk = sum(1 for s in scores if 40 <= s["score"] < 70)
    low_risk = sum(1 for s in scores if s["score"] < 40)
    avg_score = sum(s["score"] for s in scores) / len(scores)
    
    return {
        "total_documents": len(scores),
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "average_score": round(avg_score, 2),
        "scores": scores
    }
