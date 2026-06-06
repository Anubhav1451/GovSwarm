from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.verification_result import VerificationResult as VerificationResultModel
from app.models.audit_finding import AuditFinding
from fpdf import FPDF
from io import BytesIO

class ReportService:
    """Service for generating PDF executive summary reports"""
    
    @staticmethod
    def generate_executive_report(db: Session, document_id: int) -> bytes:
        """
        Generate executive summary report for a document.
        
        Args:
            db: Database session
            document_id: ID of the document to generate report for
            
        Returns:
            PDF report as bytes
        """
        # Fetch document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Fetch verification results
        verification_results = db.query(VerificationResultModel).filter(
            VerificationResultModel.document_id == document_id
        ).all()
        
        # Fetch audit findings
        audit_findings = db.query(AuditFinding).filter(
            AuditFinding.document_id == document_id
        ).all()
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "GovSwarm Executive Summary Report", ln=True, align="C")
        pdf.ln(10)
        
        # Document Information
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Document Information", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, f"Document ID: {document.id}", ln=True)
        pdf.cell(0, 8, f"Filename: {document.filename or 'N/A'}", ln=True)
        pdf.cell(0, 8, f"Document Type: {document.document_type or 'N/A'}", ln=True)
        pdf.cell(0, 8, f"Processing Status: {document.processing_status}", ln=True)
        pdf.cell(0, 8, f"Upload Date: {document.created_at.strftime('%Y-%m-%d %H:%M:%S') if document.created_at else 'N/A'}", ln=True)
        pdf.ln(10)
        
        # Verification Results
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Verification Results", ln=True)
        pdf.set_font("Helvetica", "", 10)
        
        if verification_results:
            for vr in verification_results:
                pdf.cell(0, 8, f"Type: {vr.verification_type}", ln=True)
                pdf.cell(0, 8, f"Status: {vr.verification_status}", ln=True)
                pdf.cell(0, 8, f"Created: {vr.created_at.strftime('%Y-%m-%d %H:%M:%S') if vr.created_at else 'N/A'}", ln=True)
                pdf.ln(5)
        else:
            pdf.cell(0, 8, "No verification results found.", ln=True)
        pdf.ln(10)
        
        # Audit Findings
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Audit Findings", ln=True)
        pdf.set_font("Helvetica", "", 10)
        
        if audit_findings:
            for af in audit_findings:
                pdf.cell(0, 8, f"Severity: {af.severity}", ln=True)
                pdf.cell(0, 8, f"Rule: {af.rule}", ln=True)
                pdf.cell(0, 8, f"Message: {af.message}", ln=True)
                pdf.cell(0, 8, f"Risk Score: {af.risk_score_snapshot}", ln=True)
                pdf.cell(0, 8, f"Risk Rating: {af.risk_rating_snapshot}", ln=True)
                pdf.ln(5)
        else:
            pdf.cell(0, 8, "No audit findings found.", ln=True)
        
        # Generate PDF bytes
        pdf_bytes = pdf.output(dest="S").encode("latin-1")
        
        return pdf_bytes
