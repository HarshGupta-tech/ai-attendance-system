from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.core.dependencies import get_db, get_current_user, require_role
from app.services.user_service import UserService
from app.schemas import user as user_schemas
from app.models.user import User

router = APIRouter()

def user_to_dict(u):
    if not u: return None
    return {
        'id': u.id, 'username': u.username, 'email': u.email,
        'role': u.role, 'is_active': u.is_active,
        'created_at': str(u.created_at) if u.created_at else None,
        'updated_at': str(u.updated_at) if u.updated_at else None,
    }

@router.get("", dependencies=[Depends(require_role("admin", "super_admin"))])
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = UserService(db)
        items, total = service.get_users(page=page, per_page=per_page, role=role, search=search)
        return {"items": [user_to_dict(u) for u in items], "total": total, "page": page, "per_page": per_page}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("", dependencies=[Depends(require_role("super_admin"))])
def create_user(
    user_in: user_schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = UserService(db)
        user = service.create_user(user_in)
        return user_to_dict(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", dependencies=[Depends(require_role("admin", "super_admin"))])
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = UserService(db)
        user = service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user_to_dict(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}", dependencies=[Depends(require_role("admin", "super_admin"))])
def update_user(
    user_id: int,
    user_in: user_schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = UserService(db)
        updated = service.update_user(user_id, user_in)
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        return user_to_dict(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}", dependencies=[Depends(require_role("super_admin"))])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = UserService(db)
        success = service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}/toggle-active", dependencies=[Depends(require_role("admin", "super_admin"))])
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = UserService(db)
        result = service.toggle_active(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return user_to_dict(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
