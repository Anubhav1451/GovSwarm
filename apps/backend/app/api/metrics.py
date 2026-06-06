from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint for scraping.
    
    This endpoint provides metrics in Prometheus format for monitoring and alerting.
    Uses in-memory registry for zero database latency overhead.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
