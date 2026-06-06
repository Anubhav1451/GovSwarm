class RetryableError(Exception):
    """
    Exception for transient failures that should trigger task retries.
    
    Use this for network issues, temporary service unavailability, or other
    conditions that may resolve themselves with time and retry attempts.
    """
    pass


class BusinessValidationError(Exception):
    """
    Exception for business logic validation failures that should NOT trigger retries.
    
    Use this for invalid document formats, missing required fields, or other
    conditions that will not resolve with retry attempts. These errors should
    immediately fail the task and mark the document as FAILED.
    """
    pass
