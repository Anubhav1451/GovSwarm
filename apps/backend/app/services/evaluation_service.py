from sqlalchemy.orm import Session
from app.audit.compliance_engine import ComplianceEngine
from app.audit.risk_engine import RiskEngine
from app.models.audit_finding import AuditFinding
from app.services.audit_service import AuditService

class EvaluationService:
    """Centralized evaluation service for document compliance and risk assessment"""
    
    @staticmethod
    def evaluate_document(db: Session, document_id: int) -> dict:
        """
        Evaluate document compliance and risk.
        
        Args:
            db: Database session
            document_id: ID of the document to evaluate
            
        Returns:
            Dictionary containing unified evaluation result
        """
        # Step a: Trigger compliance check
        compliance_result = ComplianceEngine.run_compliance_check(db=db, document_id=document_id)
        
        # Step b: Calculate risk score
        risk_result = RiskEngine.calculate_risk_score(compliance_result)
        
        # Step c: Persistence Layer Entry - Clear old findings
        db.query(AuditFinding).filter(AuditFinding.document_id == document_id).delete()
        
        # Insert new findings
        for finding in risk_result["findings"]:
            audit_finding = AuditFinding(
                document_id=document_id,
                severity=finding["severity"],
                rule=finding["rule"],
                message=finding["message"],
                risk_score_snapshot=risk_result["risk_score"],
                risk_rating_snapshot=risk_result["risk_rating"]
            )
            db.add(audit_finding)
        
        # Step d: Commit findings to database
        db.commit()
        
        # Step e: Central System Audit Log
        AuditService.log_action(
            db=db,
            actor_id="system",
            action="DOCUMENT_AUDIT_COMPLETED",
            resource_type="document",
            resource_id=str(document_id),
            log_metadata={
                "risk_score": risk_result["risk_score"],
                "risk_rating": risk_result["risk_rating"],
                "total_findings": len(risk_result["findings"]),
                "failed_findings": len(risk_result["failed_findings"])
            }
        )
        
        # Return unified result
        return {
            "document_id": document_id,
            "compliance": compliance_result,
            "risk": risk_result
        }

# Singleton instance
evaluation_service = EvaluationService()
