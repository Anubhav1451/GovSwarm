from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.user_role import UserRole
from app.models.document import Document
from app.models.organization import Organization
from app.services.audit_service import AuditService
from typing import Optional

class TenantGuard:
    """
    Callable dependency guard for tenant isolation and resource ownership validation.
    
    Ensures that users can only access resources belonging to their organization,
    unless they are ADMIN users who have cross-tenant access.
    
    Usage:
        @router.get("/documents/{resource_id}")
        async def get_document(
            resource_id: str,
            _tenant_check: dict = Depends(DocumentTenantGuard),
            ...
        ):
            ...
    """
    
    def __init__(self, resource_type: str):
        self.resource_type = resource_type
    
    def __call__(
        self,
        resource_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> dict:
        """
        Validate tenant isolation for the requested resource.
        
        Args:
            resource_id: The ID of the resource being accessed
            db: Database session
            current_user: The authenticated user
            
        Returns:
            dict with validation result
            
        Raises:
            HTTPException: If tenant isolation check fails
        """
        # Bypass checks for ADMIN users
        if current_user.role == UserRole.ADMIN:
            return {"status": "bypassed", "reason": "admin_user"}
        
        target_org_id: Optional[str] = None
        
        # Look up the entity based on resource_type
        if self.resource_type == "document":
            # For documents, look up by resource_id to get document.organization_id
            document = db.query(Document).filter(Document.id == int(resource_id)).first()
            if document:
                target_org_id = document.organization_id
        elif self.resource_type == "organization":
            # For organizations, look up by resource_id to get organization.id
            organization = db.query(Organization).filter(Organization.id == resource_id).first()
            if organization:
                target_org_id = organization.id
        
        # If resource not found, allow access (will be handled by business logic)
        if target_org_id is None:
            return {"status": "allowed", "reason": "resource_not_found"}
        
        # Security Breach Monitoring: Check if user belongs to the target organization
        if str(current_user.organization_id) != str(target_org_id):
            # Log security breach before raising exception
            try:
                AuditService.log_action(
                    db=db,
                    actor_id=current_user.id,
                    action="SECURITY_VIOLATION_BREACH",
                    resource_type=self.resource_type,
                    resource_id=resource_id,
                    log_metadata={
                        "breach_type": "tenant_isolation_violation",
                        "user_organization_id": str(current_user.organization_id),
                        "target_organization_id": str(target_org_id),
                        "user_email": current_user.email,
                        "username": current_user.username,
                        "user_role": current_user.role.value
                    }
                )
            except Exception:
                # Silently fail if audit logging fails
                pass
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. You do not have permission to access this {self.resource_type}."
            )
        
        return {"status": "allowed", "reason": "tenant_match"}


# Exported convenience instances
DocumentTenantGuard = TenantGuard(resource_type="document")
OrganizationTenantGuard = TenantGuard(resource_type="organization")
