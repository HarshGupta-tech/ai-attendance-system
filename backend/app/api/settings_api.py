from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.core.dependencies import get_db, get_current_user, require_role
from app.services.settings_service import SettingsService
from app.schemas import settings as setting_schemas
from app.models.user import User

router = APIRouter()

def setting_to_dict(s):
    if not s: return None
    return {
        'id': getattr(s, 'id', None), 'key': s.key, 'value': s.value,
        'description': getattr(s, 'description', None), 'is_public': getattr(s, 'is_public', False),
        'created_at': str(s.created_at) if getattr(s, 'created_at', None) else None,
        'updated_at': str(s.updated_at) if getattr(s, 'updated_at', None) else None,
    }

@router.get("", dependencies=[Depends(require_role("admin", "super_admin"))])
def get_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = SettingsService(db)
        settings = service.get_all()
        return [setting_to_dict(s) for s in settings]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{key}")
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = SettingsService(db)
        val = service.get(key)
        if val is None:
            raise HTTPException(status_code=404, detail="Setting not found")
        return {"key": key, "value": val}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{key}", dependencies=[Depends(require_role("super_admin"))])
def update_setting(
    key: str,
    setting_in: setting_schemas.SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = SettingsService(db)
        # Note: setting_in might have only value, but set takes key, value, description...
        # Wait, the original code passes setting_in.value
        updated = service.set(key, setting_in.value)
        if not updated:
            raise HTTPException(status_code=404, detail="Setting not found")
        return setting_to_dict(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
