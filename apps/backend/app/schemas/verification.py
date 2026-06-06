from pydantic import BaseModel
from typing import Dict

class VerificationResult(BaseModel):
    identifier: str
    verification_type: str
    found: bool
    status: str
    payload: Dict
