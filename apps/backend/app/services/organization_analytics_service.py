from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.organization import Organization
from app.models.document import Document
from app.models.audit_run import AuditRun
from app.models.audit_finding import AuditFinding
from typing import Dict, List, Optional

class OrganizationAnalyticsService:
    """Service for organization-level compliance analytics and risk aggregation"""
    
    @staticmethod
    def get_organization_compliance_profile(db: Session, organization_name: str) -> dict:
        """
        Get comprehensive compliance profile for an organization by name.
        
        Args:
            db: Database session
            organization_name: Organization name to look up
            
        Returns:
            Dictionary containing organization compliance analytics
        """
        # UUID Resolution Gate: Look up Organization by name first
        organization = db.query(Organization).filter(
            Organization.name == organization_name
        ).first()
        
        if not organization:
            return {
                "organization_id": "",
                "organization_name": organization_name,
                "total_documents": 0,
                "total_audit_runs": 0,
                "total_findings": 0,
                "findings_by_severity": {},
                "findings_by_rule": {},
                "compliance_timeline": [],
                "risk_distribution": {},
                "average_risk_score": None
            }
        
        organization_id = organization.id
        
        # Fetch documents for this organization
        total_documents = db.query(func.count(Document.id)).filter(
            Document.organization_id == organization_id
        ).scalar() or 0
        
        # Fetch historical AuditRun snapshots
        total_audit_runs = db.query(func.count(AuditRun.id)).filter(
            AuditRun.organization_id == organization_id
        ).scalar() or 0
        
        # Fetch AuditFinding items for this organization
        # First get all document IDs for this organization
        document_ids = db.query(Document.id).filter(
            Document.organization_id == organization_id
        ).all()
        document_ids_list = [doc_id[0] for doc_id in document_ids] if document_ids else []
        
        total_findings = 0
        findings_by_severity: Dict[str, int] = {}
        findings_by_rule: Dict[str, int] = {}
        risk_distribution: Dict[str, int] = {}
        average_risk_score: Optional[float] = None
        
        if document_ids_list:
            # Total findings count
            total_findings = db.query(func.count(AuditFinding.id)).filter(
                AuditFinding.document_id.in_(document_ids_list)
            ).scalar() or 0
            
            # Findings by severity
            severity_stats = db.query(
                AuditFinding.severity,
                func.count(AuditFinding.id)
            ).filter(
                AuditFinding.document_id.in_(document_ids_list)
            ).group_by(AuditFinding.severity).all()
            findings_by_severity = {severity: count for severity, count in severity_stats}
            
            # Findings by rule
            rule_stats = db.query(
                AuditFinding.rule,
                func.count(AuditFinding.id)
            ).filter(
                AuditFinding.document_id.in_(document_ids_list)
            ).group_by(AuditFinding.rule).all()
            findings_by_rule = {rule: count for rule, count in rule_stats}
            
            # Risk distribution
            risk_stats = db.query(
                AuditFinding.risk_rating_snapshot,
                func.count(AuditFinding.id)
            ).filter(
                AuditFinding.document_id.in_(document_ids_list)
            ).group_by(AuditFinding.risk_rating_snapshot).all()
            risk_distribution = {rating: count for rating, count in risk_stats}
            
            # Average risk score
            avg_score = db.query(func.avg(AuditFinding.risk_score_snapshot)).filter(
                AuditFinding.document_id.in_(document_ids_list)
            ).scalar()
            average_risk_score = float(avg_score) if avg_score else None
        
        # Production Upgrade Implementation: Timeline aggregation with both passed and failed checks
        compliance_timeline = []
        if document_ids_list:
            # Group audit runs by month and aggregate both passed and failed checks
            timeline_data = db.query(
                func.date_trunc('month', AuditRun.created_at).label('month'),
                func.sum(AuditRun.passed_checks).label('total_passed'),
                func.sum(AuditRun.failed_checks).label('total_failed')
            ).filter(
                AuditRun.organization_id == organization_id
            ).group_by(
                func.date_trunc('month', AuditRun.created_at)
            ).order_by(
                func.date_trunc('month', AuditRun.created_at)
            ).all()
            
            for month, passed, failed in timeline_data:
                month_str = month.strftime('%Y-%m') if month else ''
                compliance_timeline.append({
                    "month": month_str,
                    "passed_checks": int(passed) if passed else 0,
                    "failed_checks": int(failed) if failed else 0
                })
        
        return {
            "organization_id": organization_id,
            "organization_name": organization.name,
            "total_documents": total_documents,
            "total_audit_runs": total_audit_runs,
            "total_findings": total_findings,
            "findings_by_severity": findings_by_severity,
            "findings_by_rule": findings_by_rule,
            "compliance_timeline": compliance_timeline,
            "risk_distribution": risk_distribution,
            "average_risk_score": average_risk_score
        }
