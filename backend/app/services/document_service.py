import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
import pdfplumber
from docx import Document
import pandas as pd
import pytesseract
from PIL import Image
import logging

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
INDEX_FILE = UPLOADS_DIR / "index.json"

# Ensure directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def get_safe_filename(filename: str) -> str:
    """Generate a safe filename."""
    import re
    safe = re.sub(r'[^\w\s.-]', '', filename)
    safe = re.sub(r'\s+', '_', safe)
    return safe


def extract_text_from_pdf(file_path: Path) -> tuple[str, bool]:
    """Extract text from PDF. Returns (text, needs_ocr)."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if not text.strip():
            # Try OCR if available
            try:
                # Check if pytesseract is available
                pytesseract.get_tesseract_version()
                # Try to use pdf2image if available, otherwise skip OCR
                try:
                    from pdf2image import convert_from_path
                    images = convert_from_path(file_path)
                    ocr_text = ""
                    for image in images:
                        ocr_text += pytesseract.image_to_string(image) + "\n"
                    if ocr_text.strip():
                        return ocr_text, True
                except ImportError:
                    logger.warning("pdf2image not installed, OCR unavailable")
                    return "", True
            except Exception as e:
                logger.warning(f"OCR not available: {e}")
                return "", True  # Needs OCR but not available
        
        return text, False
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return "", False


def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from DOCX."""
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""


def extract_text_from_txt(file_path: Path) -> str:
    """Extract text from TXT/MD."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        logger.error(f"TXT extraction error: {e}")
        return ""


def extract_text_from_xlsx(file_path: Path) -> str:
    """Extract text from XLSX."""
    try:
        df = pd.read_excel(file_path, sheet_name=None)
        text_parts = []
        for sheet_name, sheet_df in df.items():
            text_parts.append(f"Sheet: {sheet_name}\n")
            text_parts.append(sheet_df.to_string())
            text_parts.append("\n")
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"XLSX extraction error: {e}")
        return ""


def extract_text_from_csv(file_path: Path) -> str:
    """Extract text from CSV."""
    try:
        df = pd.read_csv(file_path)
        text_parts = []
        text_parts.append(f"CSV File with {len(df)} rows and {len(df.columns)} columns\n")
        text_parts.append("Columns: " + ", ".join(df.columns.tolist()) + "\n\n")
        text_parts.append(df.to_string())
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"CSV extraction error: {e}")
        return ""


def extract_text_from_file(file_path: Path, filename: str) -> tuple[str, Optional[str]]:
    """Extract text from file based on extension."""
    ext = Path(filename).suffix.lower()
    
    if ext == '.pdf':
        text, needs_ocr = extract_text_from_pdf(file_path)
        if needs_ocr and not text:
            return "", "OCR not available. Please install pytesseract and poppler."
        return text, None
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path), None
    elif ext in ['.txt', '.md']:
        return extract_text_from_txt(file_path), None
    elif ext in ['.xlsx', '.xls']:
        return extract_text_from_xlsx(file_path), None
    elif ext == '.csv':
        return extract_text_from_csv(file_path), None
    else:
        return "", f"Unsupported file type: {ext}"


def analyze_document(text: str) -> Dict[str, Any]:
    """Basic analysis of document text."""
    if not text:
        return {
            "summary": "No text extracted from document.",
            "key_findings": [],
            "keywords": []
        }
    
    # Simple keyword extraction (common financial/risk terms)
    risk_keywords = ['fraud', 'suspicious', 'violation', 'breach', 'unauthorized', 
                     'risk', 'compliance', 'regulatory', 'penalty', 'fine']
    keywords = [kw for kw in risk_keywords if kw.lower() in text.lower()]
    
    # Simple summary (first 200 chars + word count)
    words = text.split()
    word_count = len(words)
    summary = text[:200] + "..." if len(text) > 200 else text
    
    # Key findings (simple heuristic)
    findings = []
    if any(kw in text.lower() for kw in ['fraud', 'suspicious']):
        findings.append("Potential fraud indicators detected")
    if any(kw in text.lower() for kw in ['violation', 'breach']):
        findings.append("Compliance violations mentioned")
    if word_count > 1000:
        findings.append("Large document with extensive content")
    
    return {
        "summary": summary,
        "key_findings": findings,
        "keywords": list(set(keywords)),
        "word_count": word_count
    }


def save_document_metadata(document_id: str, metadata: Dict[str, Any]):
    """Save document metadata to index.json."""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {}
    
    index[document_id] = metadata
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def load_document_metadata(document_id: Optional[str] = None) -> Dict[str, Any]:
    """Load document metadata from index.json."""
    if not INDEX_FILE.exists():
        return {} if document_id is None else None
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    if document_id:
        return index.get(document_id)
    return index


def get_all_documents() -> Dict[str, Any]:
    """Get all documents from index."""
    return load_document_metadata()


def delete_document(document_id: str) -> bool:
    """Delete a document (metadata and physical file if exists)."""
    try:
        # Load metadata to get file path
        metadata = load_document_metadata(document_id)
        if not metadata:
            return False
        
        # Delete physical file if exists
        safe_filename = metadata.get("safe_filename")
        if safe_filename:
            file_path = UPLOADS_DIR / safe_filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted physical file: {file_path}")
        
        # Remove from index
        if INDEX_FILE.exists():
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            if document_id in index:
                del index[document_id]
                
                with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                    json.dump(index, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Deleted document metadata: {document_id}")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        return False
