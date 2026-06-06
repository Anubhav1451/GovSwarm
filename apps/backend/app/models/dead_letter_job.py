from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.db.session import Base

class DeadLetterJob(Base):
    __tablename__ = "dead_letter_jobs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True)
    task_name = Column(String, index=True)
    task_id = Column(String, index=True)
    error_message = Column(Text)
    traceback_text = Column(Text)
    dlq_reason = Column(String, index=True)
    resolved = Column(Boolean, default=False, index=True)
    resolved_by = Column(String)
    resolved_at = Column(DateTime(timezone=True))
    reprocessed_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
