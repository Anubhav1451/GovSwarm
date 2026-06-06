from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

class AuditService:
    """Centralized audit logging service with resilient error handling"""
    
    @staticmethod
    def log_action(
        db: Session,
        actor_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        metadata: dict = None
    ):
        """
        Log an audit action with resilient error handling.
        
        Args:
            db: Database session
            actor_id: ID of the actor performing the action
            action: Action being performed
            resource_type: Type of resource being acted upon
            resource_id: ID of the resource
            metadata: Additional metadata to store
        """
        try:
            audit_log = AuditLog(
                actor_id=actor_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                metadata=metadata or {}
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            # Absolute strict rule: Audit logging failures NEVER crash main business API workflows
            db.rollback()
            # Pass silently
            pass
