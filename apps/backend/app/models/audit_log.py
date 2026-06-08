from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.db.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(String, index=True)
    action = Column(String, index=True)
    resource_type = Column(String, index=True)
    resource_id = Column(String, index=True)
    log_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
