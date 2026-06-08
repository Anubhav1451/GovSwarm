from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.document_status import ProcessingStatus
from app.services.document_processor import document_processor
from app.services.audit_service import AuditService
from app.services.dlq_service import DeadLetterService
from app.core.exceptions import RetryableError, BusinessValidationError
from app.core.metrics_registry import (
    DOCUMENTS_PROCESSED_TOTAL,
    DOCUMENTS_FAILED_TOTAL,
    ACTIVE_PROCESSING_DOCUMENTS,
    PROCESSING_DURATION_SECONDS,
    QUEUE_LATENCY_SECONDS
)
from app.ingestion.pdf_parser import PDFParserError
from celery import Task
from celery.exceptions import MaxRetriesExceededError
from datetime import datetime
import traceback
import sentry_sdk


class ComplianceTask(Task):
    """
    Custom base task class for compliance processing with centralized failure handling.
    
    This class overrides the on_failure method to provide:
    - Automatic DLQ recording for failed tasks
    - Audit logging for all failures
    - Distinction between max retries exceeded and task failures
    """
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Handle task failure with DLQ recording, audit logging, and Sentry context enrichment.
        
        Args:
            exc: The exception that caused the failure
            task_id: Celery task ID
            args: Task arguments
            kwargs: Task keyword arguments
            einfo: Exception info object
        """
        # Parse document_id from first argument
        document_id = None
        if args and len(args) > 0:
            document_id = args[0]
        
        # Determine DLQ reason
        if isinstance(exc, MaxRetriesExceededError):
            dlq_reason = "MAX_RETRIES_EXCEEDED"
        else:
            dlq_reason = "TASK_FAILURE"
        
        # Use isolated DB session for failure handling
        db = SessionLocal()
        organization_id = None
        try:
            # Query document object to grab organization_id for Sentry enrichment
            if document_id:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    organization_id = document.organization_id
            
            # Log the failure event via AuditService
            AuditService.log_action(
                db=db,
                actor_id="celery_worker",
                action="TASK_FAILURE",
                resource_type="document",
                resource_id=str(document_id) if document_id else task_id,
                log_metadata={
                    "task_name": self.name,
                    "task_id": task_id,
                    "dlq_reason": dlq_reason,
                    "error_message": str(exc),
                    "document_id": document_id,
                    "organization_id": organization_id
                }
            )
            
            # Record the payload in dead_letter_jobs table
            if document_id:
                DeadLetterService.store_failed_job(
                    db=db,
                    document_id=document_id,
                    task_name=self.name,
                    task_id=task_id,
                    error=exc,
                    traceback_text=einfo.traceback,
                    dlq_reason=dlq_reason
                )
        except Exception:
            # Silently fail if DLQ/audit logging fails
            pass
        finally:
            db.close()
        
        # Sentry Context Enrichment: Wrap failure payload with secure scope
        with sentry_sdk.push_scope() as scope:
            # Set distinct tags for document_id, task_id, service, and tenant_id
            scope.set_tag("document_id", str(document_id) if document_id else "unknown")
            scope.set_tag("task_id", task_id)
            scope.set_tag("service", "govswarm-compliance-worker")
            scope.set_tag("tenant_id", str(organization_id) if organization_id else "unknown")
            
            # Set structural environment context maps
            scope.set_context("task", {
                "task_name": self.name,
                "retry_count": self.request.retries
            })
            
            # Invoke sentry_sdk.capture_exception(exc)
            sentry_sdk.capture_exception(exc)


@celery_app.task(base=ComplianceTask, bind=True, name="process_document_async", autoretry_for=(RetryableError,), retry_backoff=True, retry_backoff_max=600, retry_jitter=True, max_retries=3)
def process_document_async(self, document_id: str):
    """
    Asynchronous Celery task for processing documents in the background.
    
    This task handles the complete document processing pipeline including:
    - PDF parsing and text extraction
    - Entity extraction
    - Compliance checking
    - Audit logging
    
    Args:
        document_id: The ID of the document to process (as string for Celery)
    """
    db = SessionLocal()
    try:
        # Fetch the document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Update status to PROCESSING and capture start timestamp
        document.processing_status = ProcessingStatus.PROCESSING
        document.processing_started_at = datetime.utcnow()
        db.commit()
        
        # Worker State Telemetry: Increment active processing counter
        ACTIVE_PROCESSING_DOCUMENTS.inc()
        
        # Compute queue delay and record it
        if document.created_at and document.processing_started_at:
            queue_delay = (document.processing_started_at - document.created_at).total_seconds()
            QUEUE_LATENCY_SECONDS.observe(queue_delay)
        
        # Process the document with exception handling for retry logic
        try:
            if document.mime_type == "application/pdf":
                processed_document = document_processor.process_document(db, document.id, document.storage_path)
                
                # Update status to COMPLETED and capture completion timestamp
                document.processing_status = ProcessingStatus.COMPLETED
                document.processing_completed_at = datetime.utcnow()
                db.commit()
                
                # Upon graceful exit: increment processed counter
                DOCUMENTS_PROCESSED_TOTAL.labels(document_type=document.document_type or 'unknown').inc()
                
                # Capture full run latency and record it
                if document.processing_started_at and document.processing_completed_at:
                    processing_duration = (document.processing_completed_at - document.processing_started_at).total_seconds()
                    PROCESSING_DURATION_SECONDS.observe(processing_duration)
                
                # Decrement active processing counter
                ACTIVE_PROCESSING_DOCUMENTS.dec()
                
                # Log successful completion
                AuditService.log_action(
                    db=db,
                    actor_id="system_worker",
                    action="DOCUMENT_PROCESSING_COMPLETED",
                    resource_type="document",
                    resource_id=str(document.id),
                    log_metadata={
                        "document_id": document.id,
                        "file_name": document.file_name,
                        "organization_id": document.organization_id,
                        "processing_status": "COMPLETED"
                    }
                )
            else:
                # For non-PDF files, mark as completed without parsing
                document.processing_status = ProcessingStatus.COMPLETED
                document.processing_completed_at = datetime.utcnow()
                db.commit()
                
                # Upon graceful exit: increment processed counter
                DOCUMENTS_PROCESSED_TOTAL.labels(document_type=document.document_type or 'unknown').inc()
                
                # Capture full run latency and record it
                if document.processing_started_at and document.processing_completed_at:
                    processing_duration = (document.processing_completed_at - document.processing_started_at).total_seconds()
                    PROCESSING_DURATION_SECONDS.observe(processing_duration)
                
                # Decrement active processing counter
                ACTIVE_PROCESSING_DOCUMENTS.dec()
                
                AuditService.log_action(
                    db=db,
                    actor_id="system_worker",
                    action="DOCUMENT_PROCESSING_COMPLETED",
                    resource_type="document",
                    resource_id=str(document.id),
                    log_metadata={
                        "document_id": document.id,
                        "file_name": document.file_name,
                        "organization_id": document.organization_id,
                        "processing_status": "COMPLETED",
                        "note": "Non-PDF file, skipped parsing"
                    }
                )
        except RetryableError as e:
            # Transient error - trigger retry
            raise self.retry(exc=e)
        except BusinessValidationError as e:
            # Business validation error - fail immediately without retry
            document.processing_status = ProcessingStatus.FAILED
            document.processing_completed_at = datetime.utcnow()
            db.commit()
            
            # Upon failures: increment failed counter and decrement active counter
            DOCUMENTS_FAILED_TOTAL.labels(
                document_type=document.document_type or 'unknown',
                error_type='BusinessValidationError'
            ).inc()
            ACTIVE_PROCESSING_DOCUMENTS.dec()
            
            AuditService.log_action(
                db=db,
                actor_id="system_worker",
                action="DOCUMENT_PROCESSING_FAILED",
                resource_type="document",
                resource_id=str(document.id),
                log_metadata={
                    "document_id": document.id,
                    "file_name": document.file_name,
                    "organization_id": document.organization_id,
                    "error": str(e),
                    "error_type": "BusinessValidationError",
                    "traceback": traceback.format_exc()
                }
            )
            raise
        except PDFParserError as e:
            # PDF parsing failed - treat as business validation error
            document.processing_status = ProcessingStatus.FAILED
            document.processing_completed_at = datetime.utcnow()
            db.commit()
            
            # Upon failures: increment failed counter and decrement active counter
            DOCUMENTS_FAILED_TOTAL.labels(
                document_type=document.document_type or 'unknown',
                error_type='PDFParserError'
            ).inc()
            ACTIVE_PROCESSING_DOCUMENTS.dec()
            
            AuditService.log_action(
                db=db,
                actor_id="system_worker",
                action="DOCUMENT_PROCESSING_FAILED",
                resource_type="document",
                resource_id=str(document.id),
                log_metadata={
                    "document_id": document.id,
                    "file_name": document.file_name,
                    "organization_id": document.organization_id,
                    "error": str(e),
                    "error_type": "PDFParserError",
                    "traceback": traceback.format_exc()
                }
            )
            raise
        except Exception as e:
            # Unexpected error - wrap as RetryableError for retry
            raise RetryableError(str(e))
            
    except Exception as e:
        # Outer exception handler for document fetch or other errors
        try:
            if document:
                document.processing_status = ProcessingStatus.FAILED
                document.processing_completed_at = datetime.utcnow()
                db.commit()
                
                # Upon failures: increment failed counter and decrement active counter
                DOCUMENTS_FAILED_TOTAL.labels(
                    document_type=document.document_type or 'unknown',
                    error_type=type(e).__name__
                ).inc()
                ACTIVE_PROCESSING_DOCUMENTS.dec()
                
                AuditService.log_action(
                    db=db,
                    actor_id="system_worker",
                    action="DOCUMENT_PROCESSING_FAILED",
                    resource_type="document",
                    resource_id=str(document.id),
                    log_metadata={
                        "document_id": document.id,
                        "file_name": document.file_name if document else "unknown",
                        "organization_id": document.organization_id if document else "unknown",
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    }
                )
        except Exception:
            # Silently fail if audit logging fails
            pass
        raise
    finally:
        db.close()
