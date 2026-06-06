from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.document import UploadStatus, ProcessingStatus

class DocumentCreate(BaseModel):
    organization_id: str = Field(..., description="Organization ID")
    uploaded_by: Optional[str] = Field(None, description="User who uploaded the document")

class DocumentResponse(BaseModel):
    id: int
    organization_id: str
    uploaded_by: Optional[str]
    file_name: str
    original_file_name: str
    storage_path: Optional[str]
    mime_type: str
    file_size: int
    sha256_hash: str
    document_type: Optional[str]
    upload_status: UploadStatus
    processing_status: ProcessingStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
