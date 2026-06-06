from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.document import Document
from app.models.document_status import ProcessingStatus
from app.models.dead_letter_job import DeadLetterJob
from datetime import datetime, timezone

class MetricsService:
    """Service for calculating system health and operational metrics"""
    
    @staticmethod
    def _processing_durations(documents):
        """
        Calculate processing durations for completed documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of processing durations in seconds
        """
        durations = []
        for doc in documents:
            if doc.processing_started_at and doc.processing_completed_at:
                duration = (doc.processing_completed_at - doc.processing_started_at).total_seconds()
                durations.append(duration)
        return durations
    
    @staticmethod
    def _queue_latencies(documents):
        """
        Calculate queue latencies for completed documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of queue latencies in seconds
        """
        latencies = []
        for doc in documents:
            if doc.processing_started_at and doc.created_at:
                latency = (doc.processing_started_at - doc.created_at).total_seconds()
                latencies.append(latency)
        return latencies
    
    @staticmethod
    def _p95(values):
        """
        Calculate the 95th percentile of a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            95th percentile value or 0 if list is empty
        """
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * 0.95)
        if index >= len(sorted_values):
            index = len(sorted_values) - 1
        return sorted_values[index]
    
    @staticmethod
    def get_operational_health(db: Session) -> dict:
        """
        Get comprehensive operational health metrics for the system.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary containing system health metrics
        """
        # High-performance query counts for documents by status
        total_documents = db.query(func.count(Document.id)).scalar() or 0
        queued_documents = db.query(func.count(Document.id)).filter(
            Document.processing_status == ProcessingStatus.QUEUED
        ).scalar() or 0
        processing_documents = db.query(func.count(Document.id)).filter(
            Document.processing_status == ProcessingStatus.PROCESSING
        ).scalar() or 0
        completed_documents = db.query(func.count(Document.id)).filter(
            Document.processing_status == ProcessingStatus.COMPLETED
        ).scalar() or 0
        failed_documents = db.query(func.count(Document.id)).filter(
            Document.processing_status == ProcessingStatus.FAILED
        ).scalar() or 0
        
        # Active unresolved dead_letter_jobs count
        unresolved_dlq_jobs = db.query(func.count(DeadLetterJob.id)).filter(
            DeadLetterJob.resolved == False
        ).scalar() or 0
        
        # Calculate success_rate and failure_rate with zero-division protection
        total_processed = completed_documents + failed_documents
        if total_processed > 0:
            success_rate = (completed_documents / total_processed) * 100
            failure_rate = (failed_documents / total_processed) * 100
        else:
            success_rate = 0.0
            failure_rate = 0.0
        
        # Query completed documents for performance metrics
        completed_docs = db.query(Document).filter(
            Document.processing_status == ProcessingStatus.COMPLETED
        ).all()
        
        # Calculate performance metrics
        processing_durations = MetricsService._processing_durations(completed_docs)
        queue_latencies = MetricsService._queue_latencies(completed_docs)
        
        avg_processing_time = sum(processing_durations) / len(processing_durations) if processing_durations else 0.0
        p95_processing_time = MetricsService._p95(processing_durations)
        
        avg_queue_latency = sum(queue_latencies) / len(queue_latencies) if queue_latencies else 0.0
        p95_queue_latency = MetricsService._p95(queue_latencies)
        
        return {
            "documents": {
                "total": total_documents,
                "queued": queued_documents,
                "processing": processing_documents,
                "completed": completed_documents,
                "failed": failed_documents
            },
            "dead_letter_queue": {
                "unresolved_jobs": unresolved_dlq_jobs
            },
            "rates": {
                "success_rate": round(success_rate, 2),
                "failure_rate": round(failure_rate, 2)
            },
            "performance": {
                "avg_processing_time": round(avg_processing_time, 2),
                "p95_processing_time": round(p95_processing_time, 2),
                "avg_queue_latency": round(avg_queue_latency, 2),
                "p95_queue_latency": round(p95_queue_latency, 2)
            }
        }
    
    @staticmethod
    def check_sla_violations(db: Session, threshold_seconds: float = 30.0) -> list[dict]:
        """
        Check for SLA violations in document processing.
        
        Args:
            db: Database session
            threshold_seconds: SLA threshold in seconds (default: 30.0)
            
        Returns:
            List of violation dictionaries with document details and delay information
        """
        violations = []
        current_time = datetime.now(timezone.utc)
        
        # Check for QUEUED documents exceeding threshold
        queued_documents = db.query(Document).filter(
            Document.processing_status == ProcessingStatus.QUEUED
        ).all()
        
        for doc in queued_documents:
            if doc.created_at:
                delay_seconds = (current_time - doc.created_at).total_seconds()
                if delay_seconds > threshold_seconds:
                    violations.append({
                        "document_id": doc.id,
                        "file_name": doc.file_name,
                        "organization_id": doc.organization_id,
                        "violation_type": "QUEUE_DELAY",
                        "delay_seconds": round(delay_seconds, 2),
                        "threshold_seconds": threshold_seconds,
                        "created_at": doc.created_at.isoformat() if doc.created_at else None
                    })
        
        # Check for PROCESSING documents exceeding threshold
        processing_documents = db.query(Document).filter(
            Document.processing_status == ProcessingStatus.PROCESSING
        ).all()
        
        for doc in processing_documents:
            if doc.processing_started_at:
                delay_seconds = (current_time - doc.processing_started_at).total_seconds()
                if delay_seconds > threshold_seconds:
                    violations.append({
                        "document_id": doc.id,
                        "file_name": doc.file_name,
                        "organization_id": doc.organization_id,
                        "violation_type": "PROCESSING_DELAY",
                        "delay_seconds": round(delay_seconds, 2),
                        "threshold_seconds": threshold_seconds,
                        "processing_started_at": doc.processing_started_at.isoformat() if doc.processing_started_at else None
                    })
        
        # Sort violations by delay_seconds descending
        violations.sort(key=lambda x: x["delay_seconds"], reverse=True)
        
        return violations
