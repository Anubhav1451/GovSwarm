from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.services.audit_service import AuditService
from app.core.security import decode_access_token
from typing import List

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from the JWT Bearer token.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        User object if authenticated
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    # Decode and verify JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_auditor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user and verify they are an active auditor.
    
    Args:
        current_user: The authenticated user
        db: Database session for audit logging
        
    Returns:
        User object if authenticated and is an auditor
        
    Raises:
        HTTPException: If user is not an auditor
    """
    if current_user.role != UserRole.AUDITOR and current_user.role != UserRole.ADMIN:
        # Log unauthorized access attempt
        AuditService.log_action(
            db=db,
            actor_id=current_user.id,
            action="ACCESS_DENIED",
            resource_type="auditor_only",
            resource_id="",
            metadata={
                "required_role": "AUDITOR",
                "actual_role": current_user.role.value,
                "user_email": current_user.email,
                "username": current_user.username
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Auditor role required."
        )
    
    return current_user


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
