from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.services.audit_service import AuditService
from typing import List

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from the Authorization header.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        User object if authenticated
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    # For now, we'll use a simple token-based authentication
    # In production, this would validate JWT tokens
    user = db.query(User).filter(User.id == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


class RoleChecker:
    """
    Callable dependency guard for role-based access control.
    
    Usage:
        @router.get("/endpoint")
        async def protected_endpoint(
            current_user: User = Depends(AdminOnly)
        ):
            ...
    """
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        """
        Check if the current user has one of the allowed roles.
        
        Args:
            current_user: The authenticated user
            db: Database session for audit logging
            
        Returns:
            The user if role check passes
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        if current_user.role not in self.allowed_roles:
            # Enterprise Logging Integration: Log access denied event
            AuditService.log_action(
                db=db,
                actor_id=current_user.id,
                action="ACCESS_DENIED",
                resource_type="rbac",
                resource_id="",
                metadata={
                    "required_roles": [role.value for role in self.allowed_roles],
                    "actual_role": current_user.role.value,
                    "user_email": current_user.email,
                    "username": current_user.username
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join([role.value for role in self.allowed_roles])}"
            )
        
        return current_user


# Reusable role checker instances
AdminOnly = RoleChecker(allowed_roles=[UserRole.ADMIN])
AuditorOrAdmin = RoleChecker(allowed_roles=[UserRole.AUDITOR, UserRole.ADMIN])
VendorAccess = RoleChecker(allowed_roles=[UserRole.VENDOR, UserRole.AUDITOR, UserRole.ADMIN])
