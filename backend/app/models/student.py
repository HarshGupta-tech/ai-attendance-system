from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    student_id = Column(String(20), unique=True, nullable=False, index=True)
    roll_number = Column(String(20), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(15))
    course_id = Column(Integer, ForeignKey("courses.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    semester = Column(Integer, nullable=False)
    section = Column(String(10))
    date_of_admission = Column(Date)
    status = Column(String(20), default="active")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    course = relationship("Course")
    department = relationship("Department")
    user = relationship("User")
