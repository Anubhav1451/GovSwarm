from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.dead_letter_job import DeadLetterJob
from app.models.document import Document
from app.models.document_status import ProcessingStatus
from app.services.audit_service import AuditService
from app.services.metrics_service import MetricsService
from app.workers.compliance_worker import process_document_async
from app.api.deps import AdminOnly
from app.models.user import User
from datetime import datetime

router = APIRouter()

@router.post("/dlq/reprocess/{job_id}")
async def reprocess_dead_letter_job(
    job_id: str,
    current_user: User = Depends(AdminOnly),
    db: Session = Depends(get_db)
):
    """
    Reprocess a dead letter job by triggering the document processing pipeline again.
    
    This endpoint allows operators to manually retry failed documents from the DLQ.
    """
    # Validation for non-existent DLQ entries
    dlq_job = db.query(DeadLetterJob).filter(DeadLetterJob.id == int(job_id)).first()
    if not dlq_job:
        raise HTTPException(status_code=404, detail="Dead letter job not found")
    
    # Check dlq_job.resolved to prevent duplicate concurrent triggers
    if dlq_job.resolved:
        raise HTTPException(
            status_code=400,
            detail="This dead letter job has already been resolved and reprocessed"
        )
    
    # Fetch the associated document
    document = db.query(Document).filter(Document.id == dlq_job.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Associated document not found")
    
    # Update metadata states
    dlq_job.resolved = True
    dlq_job.resolved_by = current_user.email
    dlq_job.resolved_at = datetime.utcnow()
    dlq_job.reprocessed_count += 1
    
    # Reset document processing status to QUEUED
    document.processing_status = ProcessingStatus.QUEUED
    
    db.commit()
    
    # Log telemetry using AuditService
    AuditService.log_action(
        db=db,
        actor_id=current_user.id,
        action="DLQ_REPROCESS_TRIGGERED",
        resource_type="dead_letter_job",
        resource_id=str(dlq_job.id),
        metadata={
            "dlq_job_id": dlq_job.id,
            "document_id": document.id,
            "task_name": dlq_job.task_name,
            "task_id": dlq_job.task_id,
            "dlq_reason": dlq_job.dlq_reason,
            "reprocessed_count": dlq_job.reprocessed_count,
            "resolved_by": current_user.email
        }
    )
    
    # Trigger the background pipeline decoupling safely
    process_document_async.delay(str(document.id))
    
    return {
        "status": "success",
        "message": "Dead letter job reprocessing triggered successfully",
        "document_id": document.id,
        "dlq_job_id": dlq_job.id
    }


@router.get("/health", dependencies=[Depends(AdminOnly)])
async def get_system_health(db: Session = Depends(get_db)):
    """
    Get comprehensive system health metrics.
    
    This endpoint provides operational health statistics including:
    - Document processing status distribution
    - Dead letter queue status
    - Success and failure rates
    """
    health_metrics = MetricsService.get_operational_health(db)
    return health_metrics


@router.get("/sla-breaches")
async def get_sla_breaches(
    current_user: User = Depends(AdminOnly),
    db: Session = Depends(get_db)
):
    """
    Get SLA breach violations for documents exceeding processing thresholds.
    
    This endpoint identifies documents that have exceeded the SLA threshold
    for queue time or processing time, enabling operators to take corrective action.
    """
    violations = MetricsService.check_sla_violations(db)
    
    # Telemetry Capture Execution: Log high-priority system telemetry event if breaches exist
    if violations:
        # Slice array safely (top 10 violations)
        top_violations = violations[:10]
        
        # Log SLA breach alert with violation counters in metadata
        AuditService.log_action(
            db=db,
            actor_id=current_user.id,
            action="SLA_BREACH_ALERT_DETECTED",
            resource_type="system",
            resource_id="",
            metadata={
                "total_violations": len(violations),
                "queue_delay_count": len([v for v in violations if v["violation_type"] == "QUEUE_DELAY"]),
                "processing_delay_count": len([v for v in violations if v["violation_type"] == "PROCESSING_DELAY"]),
                "top_violations": top_violations,
                "threshold_seconds": 30.0
            }
        )
    
    return {
        "total_violations": len(violations),
        "violations": violations
    }
