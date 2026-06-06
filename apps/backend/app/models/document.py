from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, Text, JSON
from sqlalchemy.sql import func
from app.db.session import Base
from app.models.document_status import ProcessingStatus
import enum

class UploadStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    FAILED = "failed"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, index=True)
    uploaded_by = Column(String)
    file_name = Column(String)
    original_file_name = Column(String)
    storage_path = Column(String)
    mime_type = Column(String)
    file_size = Column(Integer)
    sha256_hash = Column(String, unique=True, index=True)
    document_type = Column(String)
    upload_status = Column(SQLEnum(UploadStatus), default=UploadStatus.UPLOADED)
    processing_status = Column(SQLEnum(ProcessingStatus, name="processing_status_enum"), nullable=False, default=ProcessingStatus.QUEUED)
    
    # Performance tracking fields
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Ingestion pipeline fields
    page_count = Column(Integer, default=0)
    author = Column(String, default="")
    title = Column(String, default="")
    extracted_text = Column(Text, default="")
    extracted_entities = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
