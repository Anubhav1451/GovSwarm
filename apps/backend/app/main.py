from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.documents import router as documents_router
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router
from app.api.analytics import router as analytics_router
from app.api.operator import router as operator_router
from app.api.metrics import router as metrics_router
from app.api.auth import router as auth_router
from app.db.session import engine
import redis

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(documents_router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])
app.include_router(dashboard_router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(reports_router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])
app.include_router(analytics_router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(operator_router, prefix=f"{settings.API_V1_STR}/operator", tags=["operator"])
app.include_router(metrics_router, tags=["metrics"])

@app.get("/")
async def root():
    return {
        "message": "GovSwarm AI API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "components": {}
    }
    
    # Check database connectivity
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["components"]["database"] = "up"
    except Exception as e:
        health_status["components"]["database"] = f"down: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis connectivity
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        health_status["components"]["redis"] = "up"
    except Exception as e:
        health_status["components"]["redis"] = f"down: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status
