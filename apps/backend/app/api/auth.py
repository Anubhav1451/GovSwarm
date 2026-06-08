from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.audit_service import AuditService
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and issue JWT access token.
    
    Args:
        login_data: User credentials (email and password)
        db: Database session
        
    Returns:
        TokenResponse with access token and user metadata
        
    Raises:
        HTTPException: If authentication fails
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        # Log failed login attempt
        AuditService.log_action(
            db=db,
            actor_id="anonymous",
            action="LOGIN_FAILED",
            resource_type="auth",
            resource_id="",
            log_metadata={
                "email": login_data.email,
                "reason": "user_not_found"
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not user.hashed_password:
        # User has no hashed password set
        AuditService.log_action(
            db=db,
            actor_id=user.id,
            action="LOGIN_FAILED",
            resource_type="auth",
            resource_id="",
            log_metadata={
                "email": login_data.email,
                "reason": "no_password_set"
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        # Log failed login attempt
        AuditService.log_action(
            db=db,
            actor_id=user.id,
            action="LOGIN_FAILED",
            resource_type="auth",
            resource_id="",
            log_metadata={
                "email": login_data.email,
                "reason": "invalid_password"
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "role": user.role.value,
            "organization_id": user.organization_id
        },
        expires_delta=access_token_expires
    )
    
    # Log successful login
    AuditService.log_action(
        db=db,
        actor_id=user.id,
        action="LOGIN_SUCCESS",
        resource_type="auth",
        resource_id="",
        log_metadata={
            "email": user.email,
            "role": user.role.value,
            "organization_id": user.organization_id
        }
    )
    
    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        email=user.email,
        role=user.role,
        organization_id=user.organization_id
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: The authenticated user from JWT token
        
    Returns:
        UserResponse with user details
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        organization_id=current_user.organization_id,
        is_active=current_user.is_active
    )
