from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardStatsResponse

router = APIRouter()

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics including document counts, verifications, findings, and risk distribution.
    """
    stats = DashboardService.get_stats(db)
    return stats
