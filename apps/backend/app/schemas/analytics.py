from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class TimelinePoint(BaseModel):
    """Represents a single data point in the compliance timeline"""
    month: str = Field(..., description="Month in YYYY-MM format")
    passed_checks: int = Field(default=0, description="Number of passed checks in this month")
    failed_checks: int = Field(default=0, description="Number of failed checks in this month")

class OrganizationAnalyticsResponse(BaseModel):
    """Complete organization compliance profile analytics response"""
    organization_id: str = Field(..., description="Organization UUID")
    organization_name: str = Field(..., description="Organization name")
    total_documents: int = Field(default=0, description="Total number of documents")
    total_audit_runs: int = Field(default=0, description="Total number of audit runs")
    total_findings: int = Field(default=0, description="Total number of audit findings")
    findings_by_severity: Dict[str, int] = Field(default_factory=dict, description="Findings grouped by severity")
    findings_by_rule: Dict[str, int] = Field(default_factory=dict, description="Findings grouped by rule")
    compliance_timeline: List[TimelinePoint] = Field(default_factory=list, description="Monthly compliance trend data")
    risk_distribution: Dict[str, int] = Field(default_factory=dict, description="Risk rating distribution")
    average_risk_score: Optional[float] = Field(default=None, description="Average risk score across all findings")
