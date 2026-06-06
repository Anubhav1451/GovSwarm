from pydantic import BaseModel
from typing import Dict

class DocumentStats(BaseModel):
    total: int
    processed: int
    pending: int

class SummaryStats(BaseModel):
    failed_findings: int

class DashboardStatsResponse(BaseModel):
    documents: DocumentStats
    verifications: Dict[str, int]
    findings: Dict[str, int]
    risk_distribution: Dict[str, int]
    summary: SummaryStats
