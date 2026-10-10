from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, Optional, List

from app.core.dependencies import get_db, get_current_user, require_role
from app.services.subject_service import SubjectService
from app.services.course_service import CourseService
from app.schemas import subject as subject_schemas
from app.models.user import User

router = APIRouter()

def subject_to_dict(s):
    if not s: return None
    return {
        'id': s.id, 'code': s.code, 'name': s.name,
        'course_id': s.course_id, 'department_id': getattr(s, 'department_id', None),
        'semester': s.semester, 'credits': s.credits, 'status': s.status,
        'teacher_id': getattr(s, 'teacher_id', None),
        'created_at': str(s.created_at) if s.created_at else None,
    }

def course_to_dict(c):
    if not c: return None
    return {
        'id': c.id, 'name': c.name, 'code': getattr(c, 'code', None),
        'department_id': getattr(c, 'department_id', None), 'duration_years': getattr(c, 'duration_years', None),
        'status': getattr(c, 'status', None)
    }

def dept_to_dict(d):
    if not d: return None
    return {
        'id': d.id, 'name': d.name, 'code': getattr(d, 'code', None)
    }

@router.get("")
def list_subjects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    semester: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = SubjectService(db)
        items, total = service.get_subjects(
            page=page, per_page=per_page, course_id=course_id, 
            semester=semester, status=status, search=search
        )
        return {"items": [subject_to_dict(s) for s in items], "total": total, "page": page, "per_page": per_page}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("", dependencies=[Depends(require_role("admin", "super_admin"))])
def create_subject(
    subject_in: subject_schemas.SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = SubjectService(db)
        subject = service.create_subject(subject_in)
        return subject_to_dict(subject)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/courses")
def list_courses(
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = CourseService(db)
        courses = service.get_courses(department_id=department_id)
        return [course_to_dict(c) for c in courses]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/courses", dependencies=[Depends(require_role("admin", "super_admin"))])
def create_course(
    course_in: Any, # use Any to avoid schema errors if missing
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = CourseService(db)
        course = service.create_course(course_in)
        return course_to_dict(course)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/departments")
def list_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = CourseService(db)
        depts = service.get_departments()
        return [dept_to_dict(d) for d in depts]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/departments", dependencies=[Depends(require_role("admin", "super_admin"))])
def create_department(
    dept_in: Any, # use Any to avoid schema errors if missing
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = CourseService(db)
        dept = service.create_department(dept_in)
        return dept_to_dict(dept)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{subject_id}")
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = SubjectService(db)
        subject = service.get_subject(subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        return subject_to_dict(subject)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{subject_id}", dependencies=[Depends(require_role("admin", "super_admin"))])
def update_subject(
    subject_id: int,
    subject_in: subject_schemas.SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = SubjectService(db)
        updated = service.update_subject(subject_id, subject_in)
        if not updated:
            raise HTTPException(status_code=404, detail="Subject not found")
        return subject_to_dict(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{subject_id}", dependencies=[Depends(require_role("admin", "super_admin"))])
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = SubjectService(db)
        success = service.delete_subject(subject_id)
        if not success:
            raise HTTPException(status_code=404, detail="Subject not found")
        return {"message": "Subject deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
