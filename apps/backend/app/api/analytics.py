from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.organization_analytics_service import OrganizationAnalyticsService
from app.schemas.analytics import OrganizationAnalyticsResponse
from app.api.deps import AuditorOrAdmin
from app.api.tenant_guard import OrganizationTenantGuard
from app.models.user import User

router = APIRouter()

@router.get("/organization/{resource_id}", response_model=OrganizationAnalyticsResponse)
async def get_organization_analytics(
    resource_id: str,
    current_user: User = Depends(AuditorOrAdmin),
    _tenant_check: dict = Depends(OrganizationTenantGuard),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive compliance analytics for a specific organization.
    
    This endpoint provides organization-level risk aggregation including:
    - Total documents and audit runs
    - Findings breakdown by severity and rule
    - Monthly compliance timeline with passed/failed checks
    - Risk distribution and average risk score
    """
    analytics_data = OrganizationAnalyticsService.get_organization_compliance_profile(
        db=db,
        organization_name=resource_id
    )
    return analytics_data
