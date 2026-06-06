from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.sql import func
from app.db.session import Base

class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True)
    severity = Column(String, index=True)
    rule = Column(String, index=True)
    message = Column(String)
    risk_score_snapshot = Column(Float)
    risk_rating_snapshot = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
