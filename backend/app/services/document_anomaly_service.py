import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def detect_document_anomalies(text: str, filename: str) -> Dict[str, Any]:
    """Detect anomalies in any document text (PDF, DOCX, TXT, MD, etc.)."""
    if not text or len(text.strip()) == 0:
        return {
            "has_anomalies": False,
            "anomalies": [],
            "analysis": "Document is empty"
        }
    
    anomalies = []
    analysis_parts = []
    
    text_lower = text.lower()
    words = text.split()
    sentences = text.split('.')
    
    # 1. Suspicious keywords detection
    suspicious_keywords = [
        'fraud', 'fraudulent', 'scam', 'illegal', 'unauthorized', 'breach',
        'hack', 'leak', 'stolen', 'stolen data', 'data breach', 'security breach',
        'suspicious', 'unusual', 'irregular', 'anomaly', 'violation', 'non-compliance',
        'penalty', 'fine', 'lawsuit', 'legal action', 'investigation', 'audit',
        'money laundering', 'terrorist financing', 'sanctioned', 'blacklist'
    ]
    
    found_suspicious = []
    for keyword in suspicious_keywords:
        count = text_lower.count(keyword.lower())
        if count > 0:
            found_suspicious.append({
                "keyword": keyword,
                "count": count
            })
            # Find context around keyword
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            matches = list(pattern.finditer(text))
            for match in matches[:3]:  # First 3 occurrences
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                anomalies.append({
                    "anomaly_type": "suspicious_keyword",
                    "keyword": keyword,
                    "context": context,
                    "position": match.start(),
                    "severity": "high" if keyword in ['fraud', 'breach', 'hack', 'leak'] else "medium"
                })
    
    if found_suspicious:
        analysis_parts.append(f"Found {len(found_suspicious)} suspicious keyword(s)")
    
    # 2. Unusual number patterns (potential amounts, IDs, etc.)
    # Large numbers that might be suspicious
    large_numbers = re.findall(r'\b\d{6,}\b', text)
    if len(large_numbers) > 10:
        anomalies.append({
            "anomaly_type": "unusual_number_pattern",
            "description": f"Found {len(large_numbers)} large numbers (6+ digits)",
            "severity": "medium"
        })
        analysis_parts.append(f"Found {len(large_numbers)} large number patterns")
    
    # 3. Email patterns (potential data leaks)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if len(emails) > 50:
        anomalies.append({
            "anomaly_type": "excessive_emails",
            "description": f"Found {len(emails)} email addresses",
            "count": len(emails),
            "severity": "medium"
        })
        analysis_parts.append(f"Found {len(emails)} email addresses")
    
    # 4. Credit card patterns (potential security issue)
    credit_card_patterns = re.findall(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', text)
    if credit_card_patterns:
        anomalies.append({
            "anomaly_type": "potential_credit_card",
            "description": f"Found {len(credit_card_patterns)} potential credit card numbers",
            "count": len(credit_card_patterns),
            "severity": "high"
        })
        analysis_parts.append(f"Found {len(credit_card_patterns)} potential credit card numbers")
    
    # 5. SSN/ID patterns
    ssn_patterns = re.findall(r'\b\d{3}-\d{2}-\d{4}\b', text)
    if ssn_patterns:
        anomalies.append({
            "anomaly_type": "potential_ssn",
            "description": f"Found {len(ssn_patterns)} potential SSN/ID patterns",
            "count": len(ssn_patterns),
            "severity": "high"
        })
        analysis_parts.append(f"Found {len(ssn_patterns)} potential SSN patterns")
    
    # 6. Unusual text statistics
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    if avg_word_length > 15:
        anomalies.append({
            "anomaly_type": "unusual_word_length",
            "description": f"Average word length is {avg_word_length:.1f} characters (unusually long)",
            "severity": "low"
        })
    
    # 7. Excessive capitalization (potential shouting or emphasis)
    caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
    if caps_ratio > 0.3:
        anomalies.append({
            "anomaly_type": "excessive_capitalization",
            "description": f"{caps_ratio*100:.1f}% of text is capitalized",
            "severity": "low"
        })
        analysis_parts.append("Excessive capitalization detected")
    
    # 8. Repeated phrases (potential spam or errors)
    phrase_counts = {}
    for i in range(len(words) - 2):
        phrase = ' '.join(words[i:i+3]).lower()
        phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
    
    repeated_phrases = {p: c for p, c in phrase_counts.items() if c > 5}
    if repeated_phrases:
        anomalies.append({
            "anomaly_type": "repeated_phrases",
            "description": f"Found {len(repeated_phrases)} frequently repeated phrases",
            "count": len(repeated_phrases),
            "severity": "low"
        })
        analysis_parts.append(f"Found {len(repeated_phrases)} repeated phrases")
    
    # 9. Unusual punctuation patterns
    exclamation_count = text.count('!')
    question_count = text.count('?')
    if exclamation_count > len(sentences) * 0.5:
        anomalies.append({
            "anomaly_type": "excessive_exclamations",
            "description": f"Found {exclamation_count} exclamation marks",
            "severity": "low"
        })
    
    # 10. Missing or unusual spacing
    double_spaces = text.count('  ')
    if double_spaces > len(text) * 0.01:
        anomalies.append({
            "anomaly_type": "unusual_spacing",
            "description": f"Found {double_spaces} double spaces",
            "severity": "low"
        })
    
    # 11. Risk-related phrases
    risk_phrases = [
        'high risk', 'critical risk', 'immediate action required', 'urgent',
        'confidential', 'classified', 'restricted', 'internal use only',
        'do not distribute', 'forbidden', 'prohibited'
    ]
    
    found_risk_phrases = []
    for phrase in risk_phrases:
        if phrase.lower() in text_lower:
            found_risk_phrases.append(phrase)
            anomalies.append({
                "anomaly_type": "risk_phrase",
                "phrase": phrase,
                "severity": "medium"
            })
    
    if found_risk_phrases:
        analysis_parts.append(f"Found {len(found_risk_phrases)} risk-related phrases")
    
    # 12. Document statistics
    char_count = len(text)
    word_count = len(words)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Very short or very long documents
    if char_count < 100:
        anomalies.append({
            "anomaly_type": "very_short_document",
            "description": f"Document is very short ({char_count} characters)",
            "severity": "low"
        })
    elif char_count > 1000000:
        anomalies.append({
            "anomaly_type": "very_long_document",
            "description": f"Document is very long ({char_count:,} characters)",
            "severity": "low"
        })
    
    # Compile analysis
    if not analysis_parts:
        analysis = "No significant anomalies detected in document structure"
    else:
        analysis = "; ".join(analysis_parts)
    
    # Add document statistics
    analysis += f" | Stats: {word_count:,} words, {sentence_count:,} sentences, {char_count:,} chars"
    
    return {
        "has_anomalies": len(anomalies) > 0,
        "anomalies": anomalies[:50],  # Limit to 50 anomalies
        "total_words": word_count,
        "total_sentences": sentence_count,
        "total_characters": char_count,
        "suspicious_keywords_found": len(found_suspicious),
        "analysis": analysis,
        "anomaly_count": len(anomalies),
        "high_severity_count": sum(1 for a in anomalies if a.get("severity") == "high"),
        "medium_severity_count": sum(1 for a in anomalies if a.get("severity") == "medium"),
        "low_severity_count": sum(1 for a in anomalies if a.get("severity") == "low")
    }
