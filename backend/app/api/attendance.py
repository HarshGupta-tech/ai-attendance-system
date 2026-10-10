from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_role
from app.models import Student
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.user import User
from app.schemas import attendance as attendance_schemas
from app.services.attendance_service import AttendanceService
from app.services.face_service import FaceService

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: int):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: int):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)

    async def broadcast_to_session(self, message: str, session_id: int):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_text(message)

manager = ConnectionManager()

def session_to_dict(s):
    if not s: return None
    return {
        'id': s.id, 'subject_id': s.subject_id, 'date': str(s.date) if s.date else None,
        'start_time': str(s.start_time) if s.start_time else None,
        'end_time': str(s.end_time) if s.end_time else None,
        'status': s.status, 'session_code': getattr(s, 'session_code', None),
        'created_by': s.created_by,
        'created_at': str(s.created_at) if s.created_at else None,
        'updated_at': str(s.updated_at) if getattr(s, 'updated_at', None) else None
    }

def record_to_dict(r):
    if not r: return None
    return {
        'id': r.id, 'session_id': r.session_id, 'student_id': r.student_id,
        'status': r.status, 'verification_method': getattr(r, 'verification_method', None),
        'confidence': r.confidence, 'check_in_time': str(r.check_in_time) if r.check_in_time else None

    }

@router.post("/session", dependencies=[Depends(require_role("teacher", "admin", "super_admin"))])
def create_session(
    session_in: attendance_schemas.AttendanceSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        session = service.create_session(data=session_in, created_by=current_user.id)
        return session_to_dict(session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions")
def list_sessions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    subject_id: int | None = None,
    date: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        parsed_date = None
        if date:
            from datetime import datetime
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            
        items, total = service.get_sessions(
            page=page, per_page=per_page, subject_id=subject_id, 
            date_val=parsed_date, status=status
        )
        return {"items": [session_to_dict(s) for s in items], "total": total, "page": page, "per_page": per_page}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/session/{session_id}")
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        session = service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_to_dict(session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/session/{session_id}")
def update_session(
    session_id: int,
    session_in: attendance_schemas.AttendanceSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        updated = service.update_session(session_id, session_in)
        if not updated:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_to_dict(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/{session_id}/activate")
def activate_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        session = service.activate_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session activated", "session": session_to_dict(session)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/{session_id}/complete")
def complete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        session = service.complete_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session completed", "session": session_to_dict(session)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/recognize")
def recognize_face(
    data: attendance_schemas.RecognitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        result = service.process_recognition(
            session_id=data.session_id,
            base64_image=data.image_data,
            device_id=getattr(data, 'device_info', None)
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/records")
def get_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        records = service.get_all_records()
        return [record_to_dict(r) for r in records]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/{session_id}/manual", dependencies=[Depends(require_role("admin", "super_admin", "teacher"))])
def manual_attendance(
    session_id: int,
    data: attendance_schemas.ManualAttendanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = AttendanceService(db)
        result = service.mark_attendance(session_id, data.student_id, verification_method='manual')
        return record_to_dict(result) if result else {"message": "Attendance marked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/self-mark")
def self_mark_attendance(
    data: attendance_schemas.SelfAttendanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Student marks their own attendance using session code + face verification.
    Anti-proxy: verifies session code is valid AND face matches the logged-in student.
    """
    try:
        # 1. Verify the student exists
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        # 2. Find the session by code
        session = db.query(AttendanceSession).filter(
            AttendanceSession.session_code == data.session_code,
            AttendanceSession.status == 'active'
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Invalid or expired session code. Please check with your teacher.")

        # 3. Check if already marked
        existing = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == session.id,
            AttendanceRecord.student_id == student.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Your attendance is already marked for this session.")

        # 4. Verify face matches this student (anti-proxy)
        face_service = FaceService(db)
        verification = face_service.verify_face(student.id, data.image_data)

        if not verification['verified']:
            raise HTTPException(status_code=403, detail=verification['message'])

        # 5. Mark attendance
        service = AttendanceService(db)
        record = service.mark_attendance(
            session_id=session.id,
            student_db_id=student.id,
            confidence=verification['confidence'],
            verification_method='self_face_scan',
            device_info='student_portal'
        )

        return {
            "success": True,
            "message": f"Attendance marked successfully for session #{session.id}",
            "status": record.status if record else "present",
            "confidence": verification['confidence']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
