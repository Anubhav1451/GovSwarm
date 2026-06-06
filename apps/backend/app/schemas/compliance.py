from pydantic import BaseModel
from typing import List, Dict

class ComplianceCheck(BaseModel):
    rule: str
    passed: bool
    severity: str
    message: str
    details: Dict

class ComplianceSummary(BaseModel):
    total_checks: int
    passed_checks: int
    failed_checks: int

class ComplianceResult(BaseModel):
    document_id: int
    status: str
    summary: ComplianceSummary
    details: List[ComplianceCheck]
