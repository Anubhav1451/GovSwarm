from enum import Enum

class ProcessingStatus(str, Enum):
    """Processing status enumeration for document processing pipeline"""
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
