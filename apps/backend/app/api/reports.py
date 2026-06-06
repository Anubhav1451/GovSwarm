from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.report_service import ReportService
from app.api.deps import AuditorOrAdmin
from app.api.tenant_guard import DocumentTenantGuard
from app.models.user import User

router = APIRouter()

@router.get("/export/{resource_id}")
async def generate_executive_report(
    resource_id: str,
    current_user: User = Depends(AuditorOrAdmin),
    _tenant_check: dict = Depends(DocumentTenantGuard),
    db: Session = Depends(get_db)
):
    """
    Generate executive summary report for a document as PDF.
    """
    try:
        pdf_bytes = ReportService.generate_executive_report(db, int(resource_id))
        
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_{resource_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
