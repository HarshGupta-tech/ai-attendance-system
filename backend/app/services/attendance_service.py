from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.models import AttendanceSession, AttendanceRecord, Student, Subject, Course
from app.schemas import AttendanceSessionCreate, AttendanceSessionUpdate
from typing import Optional, Tuple, List
from datetime import datetime, date, timedelta

class AttendanceService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, data: AttendanceSessionCreate, created_by: int) -> AttendanceSession:
        """Create a new attendance session."""
        subject = self.db.query(Subject).filter(Subject.id == data.subject_id).first()
        if not subject:
            raise ValueError(f"Subject {data.subject_id} not found")
            
        existing = self.db.query(AttendanceSession).filter(
            AttendanceSession.subject_id == data.subject_id,
            AttendanceSession.date == data.date,
            AttendanceSession.start_time == data.start_time
        ).first()
        
        if existing:
            raise ValueError("Session already exists for this subject, date and time")
            
        session = AttendanceSession(
            **data.dict(),
            created_by=created_by,
            status='scheduled'
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session(self, session_id: int) -> Optional[AttendanceSession]:
        return self.db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    
    def get_sessions(self, page: int = 1, per_page: int = 20,
                     subject_id: Optional[int] = None, date_val: Optional[date] = None,
                     status: Optional[str] = None) -> Tuple[List[AttendanceSession], int]:
        query = self.db.query(AttendanceSession)
        if subject_id:
            query = query.filter(AttendanceSession.subject_id == subject_id)
        if date_val:
            query = query.filter(AttendanceSession.date == date_val)
        if status:
            query = query.filter(AttendanceSession.status == status)
            
        total = query.count()
        sessions = query.order_by(AttendanceSession.date.desc(), AttendanceSession.start_time.desc())\
                        .offset((page - 1) * per_page).limit(per_page).all()
        return sessions, total
    
    def update_session(self, session_id: int, data: AttendanceSessionUpdate) -> Optional[AttendanceSession]:
        session = self.get_session(session_id)
        if not session:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(session, key, value)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def activate_session(self, session_id: int) -> AttendanceSession:
        """Set session status to 'active'."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        session.status = 'active'
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def complete_session(self, session_id: int) -> AttendanceSession:
        """
        Complete a session:
        1. Set status to 'completed'
        2. Mark all students not yet recorded as 'absent'
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
            
        subject = self.db.query(Subject).filter(Subject.id == session.subject_id).first()
        
        # Get all students for this subject's course and semester
        students = self.db.query(Student).filter(
            Student.course_id == subject.course_id,
            Student.semester == subject.semester
        ).all()
        
        # Get already recorded students
        recorded_student_ids = [r.student_id for r in self.db.query(AttendanceRecord.student_id).filter(
            AttendanceRecord.session_id == session_id
        ).all()]
        
        # Mark remaining as absent
        for student in students:
            if student.id not in recorded_student_ids:
                record = AttendanceRecord(
                    session_id=session_id,
                    student_id=student.id,
                    status='absent',
                    verification_method='system'
                )
                self.db.add(record)
                
        session.status = 'completed'
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def mark_attendance(self, session_id: int, student_db_id: int, 
                        confidence: float = 0.0, 
                        verification_method: str = 'face_recognition',
                        device_info: Optional[str] = None) -> Optional[AttendanceRecord]:
        """
        Mark attendance for a student in a session.
        """
        session = self.get_session(session_id)
        if not session or session.status != 'active':
            return None
            
        existing = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == session_id,
            AttendanceRecord.student_id == student_db_id
        ).first()
        
        if existing:
            return None # Already marked
            
        now = datetime.utcnow()
        session_dt = datetime.combine(session.date, session.start_time)
        
        # Check SystemSettings for late threshold, assuming 15 min default here
        late_threshold = timedelta(minutes=15)
        
        status = 'present'
        if now > session_dt + late_threshold:
            status = 'late'
            
        record = AttendanceRecord(
            session_id=session_id,
            student_id=student_db_id,
            status=status,
            confidence=confidence,
            verification_method=verification_method,
            device_info=device_info
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def get_all_records(self) -> List[AttendanceRecord]:
        return self.db.query(AttendanceRecord).all()

    def get_attendance_records(self, session_id: int) -> List[AttendanceRecord]:
        return self.db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).all()
    
    def get_student_attendance(self, student_id: int, 
                                subject_id: Optional[int] = None,
                                start_date: Optional[date] = None,
                                end_date: Optional[date] = None) -> List[dict]:
        """Get attendance history for a student."""
        query = self.db.query(AttendanceRecord, AttendanceSession, Subject)\
            .join(AttendanceSession)\
            .join(Subject)\
            .filter(AttendanceRecord.student_id == student_id)
            
        if subject_id:
            query = query.filter(AttendanceSession.subject_id == subject_id)
        if start_date:
            query = query.filter(AttendanceSession.date >= start_date)
        if end_date:
            query = query.filter(AttendanceSession.date <= end_date)
            
        results = query.order_by(AttendanceSession.date.desc(), AttendanceSession.start_time.desc()).all()
        
        history = []
        for record, session, subject in results:
            history.append({
                "record_id": record.id,
                "session_id": session.id,
                "subject_code": subject.code,
                "subject_name": subject.name,
                "date": session.date.isoformat(),
                "time": session.start_time.isoformat(),
                "status": record.status,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None
            })
        return history
    
    def get_attendance_stats(self, student_id: int, subject_id: Optional[int] = None) -> dict:
        """
        Get attendance statistics for a student.
        """
        query = self.db.query(AttendanceRecord.status, func.count(AttendanceRecord.id))\
            .join(AttendanceSession)\
            .filter(AttendanceRecord.student_id == student_id)
            
        if subject_id:
            query = query.filter(AttendanceSession.subject_id == subject_id)
            
        stats = query.group_by(AttendanceRecord.status).all()
        
        result = {'total_classes': 0, 'present': 0, 'late': 0, 'absent': 0, 'excused': 0}
        for status, count in stats:
            if status in result:
                result[status] = count
                result['total_classes'] += count
                
        present_late = result['present'] + result['late']
        result['attendance_percentage'] = (present_late / result['total_classes'] * 100) if result['total_classes'] > 0 else 0.0
        return result
    
    def process_recognition(self, session_id: int, base64_image: str,
                           device_info: Optional[str] = None) -> List[dict]:
        """
        Process a camera frame for attendance recognition.
        """
        from app.ml.recognition_pipeline import get_pipeline
        pipeline = get_pipeline()
        
        result = pipeline.process_base64_frame(base64_image)
        
        recognition_results = []
        for face_output in result.faces:
            if face_output.match.matched:
                record = self.mark_attendance(
                    session_id=session_id,
                    student_db_id=face_output.match.student_db_id,
                    confidence=face_output.match.confidence,
                    verification_method='face_recognition',
                    device_info=device_info
                )
                if record:
                    recognition_results.append({
                        'student_id': face_output.match.student_id,
                        'student_name': face_output.match.student_name,
                        'confidence': face_output.match.confidence,
                        'status': 'recognized',
                        'attendance_status': record.status,
                        'message': f'{face_output.match.student_name} marked {record.status}',
                        'bounding_box': list(face_output.bbox)
                    })
                else:
                    recognition_results.append({
                        'student_id': face_output.match.student_id,
                        'student_name': face_output.match.student_name,
                        'confidence': face_output.match.confidence,
                        'status': 'already_marked',
                        'message': f'{face_output.match.student_name} already marked',
                        'bounding_box': list(face_output.bbox)
                    })
            else:
                recognition_results.append({
                    'student_id': None,
                    'student_name': None,
                    'confidence': 1.0 - face_output.match.distance if face_output.match.distance < float('inf') else 0,
                    'status': 'unknown',
                    'message': 'Unknown face',
                    'bounding_box': list(face_output.bbox)
                })
        
        return recognition_results
