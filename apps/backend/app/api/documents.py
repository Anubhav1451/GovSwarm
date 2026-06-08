from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.document import Document
from app.models.document_status import ProcessingStatus
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services.document_processor import document_processor
from app.services.audit_service import AuditService
from app.ingestion.pdf_parser import PDFParserError
from app.workers.compliance_worker import process_document_async
import hashlib
import os
from typing import Optional

router = APIRouter()

# Security Guardrail 2: Allowed MIME types
ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/jpg"}

# Security Guardrail 1: Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    organization_id: str = Form(...),
    uploaded_by: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a document with security guardrails and duplicate detection.
    """
    try:
        # Security Guardrail 1: Validate file size
        file_size = 0
        file_content = b""
        
        # Read file content and calculate size
        for chunk in file.file:
            file_size += len(chunk)
            file_content += chunk
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds maximum limit of 10MB. Current size: {file_size / (1024 * 1024):.2f}MB"
                )
        
        # Security Guardrail 2: Validate MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"File type '{file.content_type}' is not allowed. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
            )
        
        # Hash Engine: Calculate SHA256 hash
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        
        # Check for duplicate file in database
        existing_document = db.query(Document).filter(Document.sha256_hash == sha256_hash).first()
        if existing_document:
            # Scenario B: Duplicate Detected - Log audit before throwing exception
            AuditService.log_action(
                db=db,
                actor_id=uploaded_by or "anonymous",
                action="DUPLICATE_DOCUMENT_DETECTED",
                resource_type="document",
                resource_id=sha256_hash,
                log_metadata={
                    "file_name": file.filename,
                    "file_size": file_size,
                    "mime_type": file.content_type,
                    "existing_document_id": existing_document.id
                }
            )
            raise HTTPException(
                status_code=400,
                detail="Duplicate file detected. This document has already been audited."
            )
        
        # Determine document type from MIME type
        document_type = file.content_type.split("/")[-1] if file.content_type else "unknown"
        
        # Save file to disk
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{sha256_hash}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Save Metadata: Create new document record with QUEUED status
        new_document = Document(
            organization_id=organization_id,
            uploaded_by=uploaded_by,
            file_name=file.filename,
            original_file_name=file.filename,
            storage_path=file_path,
            mime_type=file.content_type,
            file_size=file_size,
            sha256_hash=sha256_hash,
            document_type=document_type,
            upload_status="uploaded",
            processing_status=ProcessingStatus.QUEUED
        )
        
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        
        # Scenario A: Success Upload - Log audit after successful commit
        AuditService.log_action(
            db=db,
            actor_id=uploaded_by or "anonymous",
            action="UPLOAD_DOCUMENT",
            resource_type="document",
            resource_id=str(new_document.id),
            log_metadata={
                "file_name": file.filename,
                "file_size": file_size,
                "mime_type": file.content_type,
                "sha256_hash": sha256_hash,
                "organization_id": organization_id,
                "storage_path": file_path,
                "processing_status": "QUEUED"
            }
        )
        
        # Fire background task for async processing
        process_document_async.delay(str(new_document.id))
        
        # Return 202 Accepted with document ID and QUEUED status
        return {
            "document_id": new_document.id,
            "status": "QUEUED"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during file upload: {str(e)}"
        )


@router.get("/{document_id}/status")
async def get_document_status(document_id: str, db: Session = Depends(get_db)):
    """
    Get the current processing status of a document.
    
    This endpoint enables frontend polling to check document processing progress.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document.id,
        "status": document.processing_status,
        "upload_status": document.upload_status,
        "file_name": document.file_name
    }
