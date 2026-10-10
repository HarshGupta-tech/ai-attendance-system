from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.core.dependencies import get_db, get_current_user, require_role
from app.services.audit_service import AuditService
from app.schemas import audit_log as audit_schemas
from app.models.user import User

router = APIRouter()

def audit_to_dict(a):
    if not a: return None
    return {
        'id': a.id, 'user_id': a.user_id, 'action': a.action,
        'resource_type': a.resource_type, 'resource_id': a.resource_id,
        'details': a.details, 'ip_address': a.ip_address,
        'created_at': str(a.created_at) if a.created_at else None
    }

@router.get("", dependencies=[Depends(require_role("admin", "super_admin"))])
def get_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AuditService(db)
        items, total = service.get_logs(
            page=page, per_page=per_page, user_id=user_id,
            action=action, resource_type=resource_type,
            start_date=start_date, end_date=end_date
        )
        return {"items": [audit_to_dict(a) for a in items], "total": total, "page": page, "per_page": per_page}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
