from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.models import Student, User, Course, Department, Subject, AttendanceSession, AttendanceRecord, FaceEmbedding
from app.schemas import StudentCreate, StudentUpdate
from app.core.security import hash_password
from typing import Optional, Tuple, List

class StudentService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_student(self, data: StudentCreate) -> Student:
        """Create a new student. Also creates a user account with 'student' role."""
        existing_student = self.db.query(Student).filter(Student.student_id == data.student_id).first()
        if existing_student:
            raise ValueError(f"Student ID {data.student_id} already exists")
            
        existing_email = self.db.query(User).filter(User.email == data.email).first()
        if existing_email:
            raise ValueError(f"Email {data.email} already registered")
            
        user = User(
            username=data.student_id,
            email=data.email,
            password_hash=hash_password(data.student_id),
            role='student',
            full_name=data.full_name,
            is_active=True
        )
        self.db.add(user)
        self.db.flush()
        
        student = Student(
            user_id=user.id,
            student_id=data.student_id,
            roll_number=data.roll_number,
            full_name=data.full_name,
            email=data.email,
            course_id=data.course_id,
            department_id=data.department_id,
            semester=data.semester,
            section=data.section,
            status=data.status
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student
    
    def get_student(self, student_id: int) -> Optional[Student]:
        return self.db.query(Student).filter(Student.id == student_id).first()
    
    def get_students(self, page: int = 1, per_page: int = 20, 
                     search: Optional[str] = None, course_id: Optional[int] = None,
                     department_id: Optional[int] = None, semester: Optional[int] = None,
                     section: Optional[str] = None, status: Optional[str] = None,
                     sort_by: str = 'full_name', sort_order: str = 'asc') -> Tuple[List[Student], int]:
        """Get paginated, filtered, sorted list of students."""
        query = self.db.query(Student)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Student.student_id.ilike(search_filter),
                    Student.roll_number.ilike(search_filter),
                    Student.full_name.ilike(search_filter),
                    Student.email.ilike(search_filter)
                )
            )
            
        if course_id:
            query = query.filter(Student.course_id == course_id)
        if department_id:
            query = query.filter(Student.department_id == department_id)
        if semester:
            query = query.filter(Student.semester == semester)
        if section:
            query = query.filter(Student.section == section)
        if status:
            query = query.filter(Student.status == status)
            
        sort_column = getattr(Student, sort_by, Student.full_name)
        if sort_order.lower() == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
            
        total_count = query.count()
        students = query.offset((page - 1) * per_page).limit(per_page).all()
        return students, total_count
    
    def update_student(self, student_id: int, data: StudentUpdate) -> Optional[Student]:
        student = self.get_student(student_id)
        if not student:
            return None
            
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(student, key, value)
            if key == 'full_name' or key == 'email':
                if student.user:
                    setattr(student.user, key, value)
                
        self.db.commit()
        self.db.refresh(student)
        return student
    
    def delete_student(self, student_id: int) -> bool:
        """Delete student and associated face embeddings."""
        student = self.get_student(student_id)
        if not student:
            return False
            
        self.db.query(FaceEmbedding).filter(FaceEmbedding.student_id == student_id).delete()
        if student.user:
            self.db.delete(student.user)
        self.db.delete(student)
        self.db.commit()
        return True
    
    def get_attendance_percentage(self, student_id: int, subject_id: Optional[int] = None) -> float:
        """Calculate attendance percentage for a student."""
        student = self.get_student(student_id)
        if not student:
            return 0.0
            
        session_query = self.db.query(AttendanceSession).filter(
            AttendanceSession.status == 'completed'
        )
        if subject_id:
            session_query = session_query.filter(AttendanceSession.subject_id == subject_id)
            
        total_sessions = session_query.count()
        if total_sessions == 0:
            return 0.0
            
        records_query = self.db.query(AttendanceRecord).join(AttendanceSession).filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.status.in_(['present', 'late']),
            AttendanceSession.status == 'completed'
        )
        if subject_id:
            records_query = records_query.filter(AttendanceSession.subject_id == subject_id)
            
        present_count = records_query.count()
        return (present_count / total_sessions) * 100.0
    
    def get_student_with_details(self, student_id: int) -> Optional[dict]:
        """Get student with course name, department name, face registration status, attendance %."""
        student = self.get_student(student_id)
        if not student:
            return None
            
        course = self.db.query(Course).filter(Course.id == student.course_id).first()
        department = self.db.query(Department).filter(Department.id == student.department_id).first()
        face_registered = self.db.query(FaceEmbedding).filter(FaceEmbedding.student_id == student_id).first() is not None
        
        return {
            "id": student.id,
            "student_id": student.student_id,
            "roll_number": student.roll_number,
            "full_name": student.full_name,
            "email": student.email,
            "course_name": course.name if course else None,
            "department_name": department.name if department else None,
            "semester": student.semester,
            "section": student.section,
            "status": student.status,
            "face_registered": face_registered,
            "attendance_percentage": self.get_attendance_percentage(student_id)
        }
