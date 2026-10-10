from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.core.dependencies import get_db, get_current_user
from app.services.notification_service import NotificationService
from app.schemas import notification as notification_schemas
from app.models.user import User

router = APIRouter()

def notif_to_dict(n):
    if not n: return None
    return {
        'id': n.id, 'user_id': n.user_id, 'title': n.title,
        'message': n.message, 'type': n.type, 'is_read': n.is_read,
        'created_at': str(n.created_at) if n.created_at else None
    }

@router.get("")
def get_notifications(
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = NotificationService(db)
        notifs = service.get_notifications(user_id=current_user.id, unread_only=unread_only)
        return [notif_to_dict(n) for n in notifs]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = NotificationService(db)
        count = service.get_unread_count(user_id=current_user.id)
        return {"unread_count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = NotificationService(db)
        success = service.mark_read(notification_id=notification_id, user_id=current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = NotificationService(db)
        service.mark_all_read(user_id=current_user.id)
        return {"message": "All notifications marked as read"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
