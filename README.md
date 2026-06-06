# GovSwarm AI - Enterprise Document Compliance Platform

A production-ready, multi-tenant document compliance platform with asynchronous processing, real-time observability, and comprehensive SLA monitoring. Built with FastAPI, Next.js, Celery, Redis, and Prometheus metrics.

## 🏗️ Architecture Overview

GovSwarm AI implements a distributed microservices architecture designed for high-throughput document ingestion and compliance verification:

### Multi-Tenant Architecture Topography

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend Layer (Next.js)                    │
│  - Real-time status polling hooks                              │
│  - SLA breach monitoring dashboard                             │
│  - Dynamic progress indicators                                 │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────────────┐
│                  API Gateway (FastAPI)                          │
│  - Document upload endpoint (202 Accepted)                      │
│  - Status polling endpoint                                     │
│  - Operator SLA diagnostics                                    │
│  - Prometheus metrics endpoint                                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼──────────┐
│  Redis Broker  │      │  Celery Workers   │
│  - Task Queue  │◄────►│  - Async Processing│
│  - Result Store│      │  - Compliance Engine│
└────────────────┘      │  - DLQ Management   │
                        │  - Sentry Logging   │
                        └─────────────────────┘
```

### Core Components

- **API Gateway**: FastAPI-based REST API with async task queuing
- **Message Broker**: Redis 7-alpine for Celery task orchestration
- **Worker Pool**: Celery workers with retry policies and dead letter queues
- **Observability Stack**: Prometheus metrics, Sentry error tracking, SLA monitoring
- **Frontend Dashboard**: Next.js with real-time status polling and SLA breach visualization

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Async Processing**: Celery 5.3+ with Redis broker
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Metrics**: Prometheus Client for Python
- **Error Tracking**: Sentry SDK with tenant context enrichment
- **PDF Processing**: Custom parser with entity extraction
- **Compliance Engine**: Rule-based CIN, GST, PAN validation

### Frontend
- **Framework**: Next.js 16.2+ with App Router
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS v4
- **State Management**: React Hooks with custom polling logic
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose with health checks
- **Message Broker**: Redis 7-alpine
- **Monitoring**: Prometheus metrics endpoint
- **Logging**: Structured audit logs with tenant isolation

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Docker Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd GovSwarm
```

2. Configure environment variables:
```bash
cp apps/backend/.env.example apps/backend/.env
# Edit apps/backend/.env with your configuration
```

3. Start the services:
```bash
docker-compose up -d
```

4. Verify services are running:
```bash
docker-compose ps
```

Services will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics
- Redis: localhost:6379

### Local Development

#### Backend Setup
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd apps/frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

## 📊 Testing

### Traffic Simulation Script

Run the automated traffic simulation to test the complete ingestion pipeline:

```bash
cd apps/backend
python simulate_traffic.py
```

This script:
1. Uploads a test document to the API
2. Captures the 202 Accepted response with document ID
3. Polls the status endpoint every 2.5 seconds until terminal state
4. Fetches Prometheus metrics to verify counter updates
5. Cleans up test artifacts

### Manual API Testing

#### Upload Document
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@test.pdf" \
  -F "organization_id=test-org-123" \
  -F "uploaded_by=manual-test"
```

#### Check Document Status
```bash
curl http://localhost:8000/api/v1/documents/{document_id}/status
```

#### Fetch Metrics
```bash
curl http://localhost:8000/metrics
```

#### Check SLA Breaches (Admin Only)
```bash
curl http://localhost:8000/api/v1/operator/sla-breaches
```

## 🔧 Configuration

### Environment Variables

Key environment variables for `apps/backend/.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/govswarm
REDIS_URL=redis://localhost:6379/0
API_V1_STR=/api/v1
PROJECT_NAME=GovSwarm AI
VERSION=1.0.0
SENTRY_DSN=your-sentry-dsn-here
```

### Celery Configuration

Celery worker configuration in `app/core/celery_app.py`:
- Broker: Redis at `redis://redis:6379/0`
- Backend: Redis at `redis://redis:6379/0`
- Serialization: JSON
- Timezone: UTC
- Retry backoff: Exponential with jitter
- Max retries: 3
- Task time limit: 30 minutes

### Prometheus Metrics

Available metrics at `/metrics`:
- `documents_processed_total`: Counter for successfully processed documents
- `documents_failed_total`: Counter for failed documents
- `active_processing_documents`: Gauge for currently processing documents
- `unresolved_dlq_jobs`: Gauge for unresolved dead letter queue jobs
- `processing_duration_seconds`: Histogram for processing times
- `queue_latency_seconds`: Histogram for queue wait times

## 📋 API Endpoints

### Public Endpoints

- `POST /api/v1/documents/upload` - Upload document for processing
- `GET /api/v1/documents/{document_id}/status` - Check document processing status
- `GET /metrics` - Prometheus metrics endpoint

### Admin Endpoints (Requires Admin Role)

- `GET /api/v1/operator/health` - System health metrics
- `GET /api/v1/operator/sla-breaches` - SLA breach violations
- `POST /api/v1/operator/dlq/reprocess/{job_id}` - Reprocess dead letter job

## 🔒 Security Features

- **RBAC**: Role-based access control (Admin, Auditor, Vendor)
- **Tenant Isolation**: Multi-tenant data separation with guard classes
- **Audit Logging**: Comprehensive audit trail for all operations
- **Input Validation**: File type, size, and content validation
- **Duplicate Detection**: SHA256 hash-based duplicate prevention
- **Sentry Integration**: Error tracking with tenant context enrichment

## 📈 Monitoring & Observability

### SLA Monitoring

The system monitors SLA violations for:
- **Queue Delay**: Documents stuck in QUEUED state > 30 seconds
- **Processing Delay**: Documents stuck in PROCESSING state > 30 seconds

SLA breaches are displayed in the frontend dashboard with:
- Amber/Yellow badges for QUEUE_DELAY
- Red flashing badges for PROCESSING_DELAY

### Dead Letter Queue

Failed tasks are automatically recorded in the dead letter queue with:
- Document ID and task information
- Error messages and tracebacks
- DLQ reason (MAX_RETRIES_EXCEEDED or TASK_FAILURE)
- Resolution tracking (resolved_by, resolved_at, reprocessed_count)

### Sentry Integration

All task failures are captured by Sentry with:
- Document ID and organization ID tags
- Task ID and service tags
- Task name and retry count context
- Full exception tracebacks

## 🐳 Docker Services

### API Service
- Build context: `./apps/backend`
- Port mapping: `8000:8000`
- Depends on: Redis (health check)
- Volumes: Backend code, uploads directory

### Worker Service
- Build context: `./apps/backend`
- Command: `python -m celery -A app.core.celery_app worker --loglevel=info`
- Depends on: Redis (health check)
- Volumes: Backend code, uploads directory

### Redis Service
- Image: `redis:7-alpine`
- Port mapping: `6379:6379`
- Health check: `redis-cli ping`

## 📝 Development Guidelines

### Backend Development
- Follow FastAPI best practices
- Use type hints for all functions
- Implement proper error handling
- Add audit logging for all operations
- Write unit tests for new features

### Frontend Development
- Use TypeScript strict mode
- Follow React Hooks best practices
- Implement proper error boundaries
- Use Tailwind CSS for styling
- Test responsive design

### Commit Conventions
- Use conventional commit messages
- Prefix with type: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Include issue references when applicable
- Keep commits atomic and focused

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new functionality
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Support

For technical support or questions, please contact the development team.
