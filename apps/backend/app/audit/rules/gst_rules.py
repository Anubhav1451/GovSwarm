def validate_gst_active(payload: dict) -> dict:
    """
    Validate if GST registration is active.
    
    Args:
        payload: Verification result payload from registry
        
    Returns:
        Dictionary with validation result and severity
    """
    status = payload.get("status", "").upper()
    is_active = status == "ACTIVE"
    
    return {
        "rule": "validate_gst_active",
        "passed": is_active,
        "severity": "HIGH",
        "message": f"GST registration is {'active' if is_active else 'not active'}",
        "details": payload
    }

def validate_taxpayer_type(payload: dict) -> dict:
    """
    Validate taxpayer type based on legal name.
    
    Args:
        payload: Verification result payload from registry
        
    Returns:
        Dictionary with validation result and severity
    """
    legal_name = payload.get("legal_name", "")
    # Simple validation - check if legal name exists and is not empty
    is_valid = bool(legal_name and legal_name.strip())
    
    return {
        "rule": "validate_taxpayer_type",
        "passed": is_valid,
        "severity": "MEDIUM",
        "message": f"Taxpayer type validation {'passed' if is_valid else 'failed'}",
        "details": payload
    }

def validate_registration_state(payload: dict) -> dict:
    """
    Validate registration state.
    
    Args:
        payload: Verification result payload from registry
        
    Returns:
        Dictionary with validation result and severity
    """
    state = payload.get("state", "")
    # Simple validation - check if state exists and is not empty
    is_valid = bool(state and state.strip())
    
    return {
        "rule": "validate_registration_state",
        "passed": is_valid,
        "severity": "MEDIUM",
        "message": f"Registration state validation {'passed' if is_valid else 'failed'}",
        "details": payload
    }
