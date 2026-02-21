import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import pandas as pd
import logging

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
REPORTS_DIR = DATA_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

from ..services.risk_service import get_risk_dashboard
from ..services.anomaly_service import detect_anomalies
from ..services.alert_service import get_alerts
from ..services.document_service import get_all_documents


def generate_report() -> Dict[str, Any]:
    """Generate PDF and Excel reports."""
    report_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    pdf_path = REPORTS_DIR / f"report_{timestamp}_{report_id[:8]}.pdf"
    excel_path = REPORTS_DIR / f"report_{timestamp}_{report_id[:8]}.xlsx"
    
    # Generate PDF
    try:
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30
        )
        story.append(Paragraph("ML Project Risk & Compliance Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Dashboard
        risk_dashboard = get_risk_dashboard()
        story.append(Paragraph("Risk Dashboard", styles['Heading2']))
        
        risk_data = [
            ['Metric', 'Value'],
            ['Total Documents', str(risk_dashboard['total_documents'])],
            ['High Risk', str(risk_dashboard['high_risk_count'])],
            ['Medium Risk', str(risk_dashboard['medium_risk_count'])],
            ['Low Risk', str(risk_dashboard['low_risk_count'])],
            ['Average Score', f"{risk_dashboard['average_score']:.2f}"]
        ]
        
        risk_table = Table(risk_data, colWidths=[3*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Anomalies
        anomalies = detect_anomalies()
        story.append(Paragraph(f"Anomalies Detected: {len(anomalies)}", styles['Heading2']))
        if anomalies:
            anomaly_data = [['Transaction ID', 'Amount', 'Type', 'Z-Score']]
            for anom in anomalies[:20]:  # Limit to 20
                anomaly_data.append([
                    anom['transaction_id'],
                    f"${anom['amount']:.2f}",
                    anom['anomaly_type'],
                    f"{anom['z_score']:.2f}"
                ])
            
            anomaly_table = Table(anomaly_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
            anomaly_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(anomaly_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Alerts
        alerts = get_alerts()
        story.append(Paragraph(f"Active Alerts: {len(alerts)}", styles['Heading2']))
        if alerts:
            for alert in alerts[:10]:  # Limit to 10
                story.append(Paragraph(f"[{alert['severity'].upper()}] {alert['message']}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        logger.info(f"PDF report generated: {pdf_path}")
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise
    
    # Generate Excel
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Risk scores sheet
            risk_df = pd.DataFrame(risk_dashboard['scores'])
            risk_df.to_excel(writer, sheet_name='Risk Scores', index=False)
            
            # Anomalies sheet
            if anomalies:
                anomalies_df = pd.DataFrame(anomalies)
                anomalies_df.to_excel(writer, sheet_name='Anomalies', index=False)
            
            # Alerts sheet
            if alerts:
                alerts_df = pd.DataFrame(alerts)
                alerts_df.to_excel(writer, sheet_name='Alerts', index=False)
            
            # Documents sheet
            documents = get_all_documents()
            if documents:
                docs_list = []
                for doc_id, metadata in documents.items():
                    csv_anomalies = metadata.get('csv_anomalies', {})
                    doc_anomalies = metadata.get('document_anomalies', {})
                    docs_list.append({
                        'document_id': doc_id,
                        'filename': metadata.get('filename', ''),
                        'uploaded_at': metadata.get('uploaded_at', ''),
                        'text_length': metadata.get('text_length', 0),
                        'file_type': metadata.get('file_type', ''),
                        'risk_score': metadata.get('risk_score', {}).get('score', 0),
                        'has_csv_anomalies': csv_anomalies.get('has_anomalies', False) if csv_anomalies else False,
                        'csv_anomaly_count': csv_anomalies.get('anomaly_count', 0) if csv_anomalies else 0,
                        'has_document_anomalies': doc_anomalies.get('has_anomalies', False) if doc_anomalies else False,
                        'document_anomaly_count': doc_anomalies.get('anomaly_count', 0) if doc_anomalies else 0,
                        'total_anomalies': (csv_anomalies.get('anomaly_count', 0) if csv_anomalies else 0) + 
                                          (doc_anomalies.get('anomaly_count', 0) if doc_anomalies else 0)
                    })
                docs_df = pd.DataFrame(docs_list)
                docs_df.to_excel(writer, sheet_name='Documents', index=False)
            
            # Document Anomalies sheet (all document types)
            if documents:
                all_anomalies = []
                for doc_id, metadata in documents.items():
                    filename = metadata.get('filename', '')
                    # CSV-specific anomalies
                    csv_anomalies = metadata.get('csv_anomalies', {})
                    if csv_anomalies and csv_anomalies.get('anomalies'):
                        for anomaly in csv_anomalies['anomalies']:
                            all_anomalies.append({
                                'document_id': doc_id,
                                'filename': filename,
                                'anomaly_type': anomaly.get('anomaly_type', ''),
                                'column': anomaly.get('column', ''),
                                'row_index': anomaly.get('row_index', -1),
                                'value': anomaly.get('value', ''),
                                'z_score': anomaly.get('z_score', 0),
                                'source': 'CSV'
                            })
                    # General document anomalies
                    doc_anomalies = metadata.get('document_anomalies', {})
                    if doc_anomalies and doc_anomalies.get('anomalies'):
                        for anomaly in doc_anomalies['anomalies']:
                            all_anomalies.append({
                                'document_id': doc_id,
                                'filename': filename,
                                'anomaly_type': anomaly.get('anomaly_type', ''),
                                'description': anomaly.get('description', ''),
                                'keyword': anomaly.get('keyword', ''),
                                'phrase': anomaly.get('phrase', ''),
                                'severity': anomaly.get('severity', ''),
                                'source': 'Document'
                            })
                if all_anomalies:
                    anomalies_df = pd.DataFrame(all_anomalies)
                    anomalies_df.to_excel(writer, sheet_name='Document Anomalies', index=False)
        
        logger.info(f"Excel report generated: {excel_path}")
    except Exception as e:
        logger.error(f"Error generating Excel report: {e}")
        raise
    
    return {
        "report_id": report_id,
        "pdf_path": str(pdf_path.relative_to(DATA_DIR.parent)),
        "excel_path": str(excel_path.relative_to(DATA_DIR.parent)),
        "message": "Report generated successfully"
    }
