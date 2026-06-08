from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.db.session import Base

class AuditRun(Base):
    __tablename__ = "audit_runs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, index=True)
    document_id = Column(Integer, index=True)
    passed_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    total_checks = Column(Integer, default=0)
    run_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
