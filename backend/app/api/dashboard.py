from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.core.dependencies import get_db, get_current_user
from app.services.dashboard_service import DashboardService
from app.models.user import User

router = APIRouter()

@router.get("/statistics")
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = DashboardService(db)
        return {
            "stats": service.get_statistics(),
            "daily_trend": service.get_daily_trend(),
            "weekly_trend": service.get_weekly_trend(),
            "subject_attendance": service.get_subject_attendance(),
            "low_attendance_students": service.get_low_attendance_students(),
            "recent_sessions": service.get_recent_sessions()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
