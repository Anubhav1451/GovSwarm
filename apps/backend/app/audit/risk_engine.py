class RiskEngine:
    """Risk scoring engine for compliance evaluation"""
    
    # Severity deduction matrix
    SEVERITY_DEDUCTIONS = {
        "HIGH": 30,
        "MEDIUM": 15,
        "LOW": 5
    }
    
    # Finding messages mapping
    FINDING_MESSAGES = {
        "validate_gst_active": "GST registration status check",
        "validate_taxpayer_type": "Taxpayer type validation",
        "validate_registration_state": "Registration state validation",
        "validate_pan_active": "PAN status check",
        "validate_holder_type": "PAN holder type validation",
        "validate_cin_active": "CIN status check",
        "validate_authorized_capital": "Authorized capital validation"
    }
    
    @staticmethod
    def calculate_risk_score(compliance_result: dict) -> dict:
        """
        Calculate risk score based on compliance check results.
        
        Args:
            compliance_result: Compliance check result from ComplianceEngine
            
        Returns:
            Dictionary containing risk_score, risk_rating, findings, and failed_findings
        """
        details = compliance_result.get("details", [])
        
        # Start with perfect score of 100
        risk_score = 100
        findings = []
        failed_findings = []
        
        # Process each compliance check
        for check in details:
            rule = check.get("rule", "")
            passed = check.get("passed", False)
            severity = check.get("severity", "LOW")
            message = check.get("message", "")
            
            # Get finding message
            finding_message = RiskEngine.FINDING_MESSAGES.get(rule, rule)
            
            # Create finding entry
            finding = {
                "rule": rule,
                "severity": severity,
                "message": finding_message,
                "passed": passed,
                "details": message
            }
            
            findings.append(finding)
            
            # If check failed, apply deduction
            if not passed:
                deduction = RiskEngine.SEVERITY_DEDUCTIONS.get(severity, 5)
                risk_score -= deduction
                failed_findings.append(finding)
        
        # Ensure minimum score of 0
        risk_score = max(0, risk_score)
        
        # Determine risk rating
        if risk_score >= 90:
            risk_rating = "LOW"
        elif risk_score >= 70:
            risk_rating = "MEDIUM"
        elif risk_score >= 50:
            risk_rating = "HIGH"
        else:
            risk_rating = "CRITICAL"
        
        return {
            "risk_score": risk_score,
            "risk_rating": risk_rating,
            "findings": findings,
            "failed_findings": failed_findings
        }
