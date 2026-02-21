import os
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
REGULATIONS_DIR = DATA_DIR / "regulations"


def load_regulations() -> Dict[str, str]:
    """Load all regulation markdown files."""
    regulations = {}
    
    if not REGULATIONS_DIR.exists():
        REGULATIONS_DIR.mkdir(parents=True, exist_ok=True)
        return regulations
    
    for md_file in REGULATIONS_DIR.glob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                reg_id = md_file.stem
                regulations[reg_id] = content
        except Exception as e:
            logger.error(f"Error loading regulation {md_file}: {e}")
    
    return regulations


def check_compliance(document_text: str) -> List[Dict[str, Any]]:
    """Check document against regulations."""
    violations = []
    regulations = load_regulations()
    
    if not regulations:
        return violations
    
    # Simple heuristic matching
    document_lower = document_text.lower()
    
    for reg_id, reg_text in regulations.items():
        # Extract requirement IDs and text from markdown
        lines = reg_text.split('\n')
        current_requirement = None
        requirement_text = ""
        
        for line in lines:
            if line.startswith('##') or line.startswith('#'):
                if current_requirement:
                    # Check previous requirement
                    if any(keyword in document_lower for keyword in requirement_text.lower().split()[:10]):
                        # Check if it's a violation (simple heuristic: negative keywords)
                        negative_keywords = ['violate', 'breach', 'non-compliance', 'fail', 'missing']
                        if any(nkw in document_lower for nkw in negative_keywords):
                            # Find evidence snippet
                            evidence_start = max(0, document_lower.find(requirement_text.lower().split()[0]) - 50)
                            evidence_end = min(len(document_text), evidence_start + 200)
                            evidence = document_text[evidence_start:evidence_end]
                            
                            violations.append({
                                "requirement_id": current_requirement,
                                "requirement_text": requirement_text[:200],
                                "evidence": evidence,
                                "severity": "high" if any(nkw in document_lower for nkw in ['violate', 'breach']) else "medium"
                            })
                
                # Start new requirement
                if line.startswith('##'):
                    current_requirement = line.replace('#', '').strip()
                    requirement_text = line
                else:
                    current_requirement = None
            elif current_requirement:
                requirement_text += " " + line
        
        # Check last requirement
        if current_requirement:
            if any(keyword in document_lower for keyword in requirement_text.lower().split()[:10]):
                negative_keywords = ['violate', 'breach', 'non-compliance', 'fail', 'missing']
                if any(nkw in document_lower for nkw in negative_keywords):
                    evidence_start = max(0, document_lower.find(requirement_text.lower().split()[0]) - 50)
                    evidence_end = min(len(document_text), evidence_start + 200)
                    evidence = document_text[evidence_start:evidence_end]
                    
                    violations.append({
                        "requirement_id": current_requirement,
                        "requirement_text": requirement_text[:200],
                        "evidence": evidence,
                        "severity": "high" if any(nkw in document_lower for nkw in ['violate', 'breach']) else "medium"
                    })
    
    return violations
