from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.db.session import Base

class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True)
    verification_type = Column(String, index=True)
    verification_status = Column(String, index=True)
    response_payload = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
