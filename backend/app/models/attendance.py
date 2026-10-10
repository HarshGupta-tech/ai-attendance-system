from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import random
import string
from app.database.session import Base

def generate_session_code():
    """Generate a random 6-digit numeric code."""
    return ''.join(random.choices(string.digits, k=6))

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))
    semester = Column(Integer)
    section = Column(String(10))
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    late_threshold_minutes = Column(Integer, default=15)
    status = Column(String(20), default="scheduled")
    session_code = Column(String(6), default=generate_session_code)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint("subject_id", "date", "start_time", name="_subject_date_time_uc"),)
    
    subject = relationship("Subject")
    course = relationship("Course")
    creator = relationship("User")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    check_in_time = Column(DateTime)
    status = Column(String(20), nullable=False)
    confidence = Column(Float)
    verification_method = Column(String(50), default="face_recognition")
    device_info = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint("session_id", "student_id", name="_session_student_uc"),)
    
    session = relationship("AttendanceSession")
    student = relationship("Student")
