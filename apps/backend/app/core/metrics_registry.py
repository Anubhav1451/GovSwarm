from prometheus_client import Counter, Gauge, Histogram

# Counter configurations for processed vs failed logs
DOCUMENTS_PROCESSED_TOTAL = Counter(
    'documents_processed_total',
    'Total number of documents successfully processed',
    ['document_type']
)

DOCUMENTS_FAILED_TOTAL = Counter(
    'documents_failed_total',
    'Total number of documents that failed processing',
    ['document_type', 'error_type']
)

# Gauge structures for active documents and unresolved DLQ counts
ACTIVE_PROCESSING_DOCUMENTS = Gauge(
    'active_processing_documents',
    'Number of documents currently being processed'
)

UNRESOLVED_DLQ_JOBS = Gauge(
    'unresolved_dlq_jobs',
    'Number of unresolved dead letter queue jobs'
)

# Histogram buckets for processing durations and queue latencies
PROCESSING_DURATION_SECONDS = Histogram(
    'processing_duration_seconds',
    'Document processing duration in seconds',
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

QUEUE_LATENCY_SECONDS = Histogram(
    'queue_latency_seconds',
    'Document queue latency in seconds',
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)
