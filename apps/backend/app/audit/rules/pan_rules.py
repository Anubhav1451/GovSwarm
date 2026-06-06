def validate_pan_active(payload: dict) -> dict:
    """
    Validate if PAN is active.
    
    Args:
        payload: Verification result payload from registry
        
    Returns:
        Dictionary with validation result and severity
    """
    status = payload.get("status", "").upper()
    is_active = status == "ACTIVE"
    
    return {
        "rule": "validate_pan_active",
        "passed": is_active,
        "severity": "HIGH",
        "message": f"PAN is {'active' if is_active else 'not active'}",
        "details": payload
    }

def validate_holder_type(payload: dict) -> dict:
    """
    Validate PAN holder type based on name.
    
    Args:
        payload: Verification result payload from registry
        
    Returns:
        Dictionary with validation result and severity
    """
    name = payload.get("name", "")
    # Simple validation - check if name exists and is not empty
    is_valid = bool(name and name.strip())
    
    return {
        "rule": "validate_holder_type",
        "passed": is_valid,
        "severity": "MEDIUM",
        "message": f"PAN holder type validation {'passed' if is_valid else 'failed'}",
        "details": payload
    }
