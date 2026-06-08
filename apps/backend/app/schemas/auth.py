from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user_role import UserRole


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: UserRole
    organization_id: Optional[str]


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: UserRole
    organization_id: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True
