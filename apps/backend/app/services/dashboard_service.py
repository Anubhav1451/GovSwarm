from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.document import Document
from app.models.verification_result import VerificationResult as VerificationResultModel
from app.models.audit_finding import AuditFinding

class DashboardService:
    """Service for aggregating dashboard statistics"""
    
    @staticmethod
    def get_stats(db: Session) -> dict:
        """
        Get dashboard statistics from database.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary containing dashboard statistics
        """
        # Document statistics
        total_documents = db.query(func.count(Document.id)).scalar()
        processed_documents = db.query(func.count(Document.id)).filter(
            Document.processing_status == "completed"
        ).scalar()
        pending_documents = db.query(func.count(Document.id)).filter(
            Document.processing_status == "pending"
        ).scalar()
        
        # Verification statistics by type
        verification_stats = db.query(
            VerificationResultModel.verification_type,
            func.count(VerificationResultModel.id)
        ).group_by(VerificationResultModel.verification_type).all()
        verifications = {v_type: count for v_type, count in verification_stats}
        
        # Findings statistics by severity
        findings_stats = db.query(
            AuditFinding.severity,
            func.count(AuditFinding.id)
        ).group_by(AuditFinding.severity).all()
        findings = {severity: count for severity, count in findings_stats}
        
        # Risk distribution from findings
        risk_distribution = db.query(
            AuditFinding.risk_rating_snapshot,
            func.count(AuditFinding.id)
        ).group_by(AuditFinding.risk_rating_snapshot).all()
        risk_dist = {rating: count for rating, count in risk_distribution}
        
        # Summary statistics
        failed_findings = db.query(func.count(AuditFinding.id)).filter(
            AuditFinding.severity == "HIGH"
        ).scalar() or 0
        
        return {
            "documents": {
                "total": total_documents or 0,
                "processed": processed_documents or 0,
                "pending": pending_documents or 0
            },
            "verifications": verifications,
            "findings": findings,
            "risk_distribution": risk_dist,
            "summary": {
                "failed_findings": failed_findings
            }
        }
