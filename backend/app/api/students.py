from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import Any, Optional, List

from app.core.dependencies import get_db, get_current_user, require_role
from app.services.student_service import StudentService
from app.services.face_service import FaceService
from app.services.attendance_service import AttendanceService
from app.schemas import student as student_schemas
from app.schemas import face as face_schemas
from app.models.user import User
from app.models import Student

router = APIRouter()

def student_to_dict(s):
    if not s: return None
    return {
        'id': s.id, 'student_id': s.student_id, 'roll_number': s.roll_number,
        'full_name': s.full_name, 'email': s.email, 'phone': getattr(s, 'phone', None),
        'course_id': s.course_id, 'department_id': s.department_id,
        'semester': s.semester, 'section': s.section, 'status': s.status,
        'user_id': s.user_id, 'created_at': str(s.created_at) if s.created_at else None,
        'updated_at': str(s.updated_at) if s.updated_at else None,
    }

@router.get("")
def list_students(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    course_id: Optional[int] = None,
    department_id: Optional[int] = None,
    semester: Optional[int] = None,
    section: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = StudentService(db)
        items, total = service.get_students(
            page=page, per_page=per_page, search=search, sort_by=sort_by,
            sort_order=sort_order, course_id=course_id, department_id=department_id,
            semester=semester, section=section, status=status
        )
        return {"items": [student_to_dict(s) for s in items], "total": total, "page": page, "per_page": per_page}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("", dependencies=[Depends(require_role("admin", "super_admin"))])
def create_student(
    student_in: student_schemas.StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = StudentService(db)
        student = service.create_student(student_in)
        return student_to_dict(student)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Let a student fetch their own profile."""
    try:
        service = StudentService(db)
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        return service.get_student_with_details(student.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/me/face-register")
def register_my_face(
    face_data: face_schemas.FaceRegistrationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Let a student register their own face."""
    try:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        service = FaceService(db)
        return service.register_face(student.id, face_data.images)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/face-status")
def get_my_face_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        service = FaceService(db)
        return service.get_registration_status(student.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/attendance-stats")
def get_my_attendance_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        service = AttendanceService(db)
        return service.get_attendance_stats(student.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{student_id}")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = StudentService(db)
        student = service.get_student_with_details(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{student_id}", dependencies=[Depends(require_role("admin", "super_admin"))])
def update_student(
    student_id: int,
    student_in: student_schemas.StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = StudentService(db)
        updated = service.update_student(student_id, student_in)
        if not updated:
            raise HTTPException(status_code=404, detail="Student not found")
        return student_to_dict(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{student_id}", dependencies=[Depends(require_role("admin", "super_admin"))])
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = StudentService(db)
        success = service.delete_student(student_id)
        if not success:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"message": "Student deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{student_id}/face-register", dependencies=[Depends(require_role("admin", "super_admin"))])
def register_face(
    student_id: int,
    face_data: face_schemas.FaceRegistrationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = FaceService(db)
        return service.register_face(student_id, face_data.images)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{student_id}/face-status")
def get_face_status(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = FaceService(db)
        return service.get_registration_status(student_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{student_id}/face-data", dependencies=[Depends(require_role("admin", "super_admin"))])
def delete_face_data(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = FaceService(db)
        success = service.delete_face_data(student_id)
        if not success:
            raise HTTPException(status_code=404, detail="Face data not found")
        return {"message": "Face data deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{student_id}/attendance")
def get_student_attendance(
    student_id: int,
    subject_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        res = service.get_student_attendance(
            student_id, subject_id, start_date, end_date
        )
        return [
            {
                "id": r.id, "session_id": r.session_id, "student_id": r.student_id,
                "status": r.status, "confidence": r.confidence, 
                "marked_at": str(r.marked_at) if r.marked_at else None,
                "marked_by": r.marked_by, "remarks": r.remarks
            } for r in res
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{student_id}/attendance-stats")
def get_attendance_stats(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        return service.get_attendance_stats(student_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
