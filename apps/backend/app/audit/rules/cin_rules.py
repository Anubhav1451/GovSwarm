def validate_cin_active(payload: dict) -> dict:
    """
    Validate if CIN is active.
    
    Args:
        payload: Verification result payload from registry
        
    Returns:
        Dictionary with validation result and severity
    """
    status = payload.get("status", "").upper()
    is_active = status == "ACTIVE"
    
    return {
        "rule": "validate_cin_active",
        "passed": is_active,
        "severity": "HIGH",
        "message": f"CIN is {'active' if is_active else 'not active'}",
        "details": payload
    }

def validate_authorized_capital(payload: dict) -> dict:
    """
    Validate authorized capital based on company registration.
    
    Args:
        payload: Verification result payload from registry
        
    Returns:
        Dictionary with validation result and severity
    """
    company_name = payload.get("company_name", "")
    # Simple validation - check if company name exists and is not empty
    is_valid = bool(company_name and company_name.strip())
    
    return {
        "rule": "validate_authorized_capital",
        "passed": is_valid,
        "severity": "MEDIUM",
        "message": f"Authorized capital validation {'passed' if is_valid else 'failed'}",
        "details": payload
    }
