from sqlalchemy.orm import Session
from app.models.verification_result import VerificationResult as VerificationResultModel
from app.audit.rules.gst_rules import validate_gst_active, validate_taxpayer_type, validate_registration_state
from app.audit.rules.pan_rules import validate_pan_active, validate_holder_type
from app.audit.rules.cin_rules import validate_cin_active, validate_authorized_capital

class ComplianceEngine:
    """Central compliance engine for running rule-based compliance checks"""
    
    @staticmethod
    def run_compliance_check(db: Session, document_id: int) -> dict:
        """
        Run compliance checks on a document based on verification results.
        
        Args:
            db: Database session
            document_id: ID of the document to check
            
        Returns:
            Dictionary containing compliance check results
        """
        # Query verification results for the document
        verification_results = db.query(VerificationResultModel).filter(
            VerificationResultModel.document_id == document_id
        ).all()
        
        checks = []
        
        # Loop through verification results and run appropriate rules
        for verification in verification_results:
            payload = verification.response_payload or {}
            verification_type = verification.verification_type.upper()
            
            if verification_type == "GST":
                # Run GST rules
                checks.append(validate_gst_active(payload))
                checks.append(validate_taxpayer_type(payload))
                checks.append(validate_registration_state(payload))
            
            elif verification_type == "PAN":
                # Run PAN rules
                checks.append(validate_pan_active(payload))
                checks.append(validate_holder_type(payload))
            
            elif verification_type == "CIN":
                # Run CIN rules
                checks.append(validate_cin_active(payload))
                checks.append(validate_authorized_capital(payload))
        
        # Calculate summary
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks if check["passed"])
        failed_checks = total_checks - passed_checks
        
        # Determine overall status
        overall_status = "PASS" if failed_checks == 0 else "FAIL"
        
        return {
            "document_id": document_id,
            "status": overall_status,
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks
            },
            "details": checks
        }
