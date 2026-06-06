from enum import Enum

class UserRole(str, Enum):
    """User role enumeration for RBAC"""
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"
    VENDOR = "VENDOR"
