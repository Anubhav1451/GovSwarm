from sqlalchemy.orm import Session
from app.models.dead_letter_job import DeadLetterJob

class DeadLetterService:
    """Service for managing dead letter queue operations"""
    
    @staticmethod
    def store_failed_job(
        db: Session,
        document_id: int,
        task_name: str,
        task_id: str,
        error: Exception,
        traceback_text: str,
        dlq_reason: str
    ):
        """
        Store a failed job in the dead letter queue tracking table.
        
        Args:
            db: Database session
            document_id: ID of the document being processed
            task_name: Name of the failed task
            task_id: Celery task ID
            error: The exception that caused the failure
            traceback_text: Full traceback of the error
            dlq_reason: Reason for DLQ entry (e.g., "MAX_RETRIES_EXCEEDED", "TASK_FAILURE")
        """
        try:
            dead_letter_job = DeadLetterJob(
                document_id=document_id,
                task_name=task_name,
                task_id=task_id,
                error_message=str(error),
                traceback_text=traceback_text,
                dlq_reason=dlq_reason
            )
            db.add(dead_letter_job)
            db.commit()
        except Exception as e:
            # Silently fail if DLQ storage fails to avoid cascading failures
            db.rollback()
            pass
