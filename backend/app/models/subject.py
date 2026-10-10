from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    semester = Column(Integer)
    credits = Column(Integer, default=3)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course")
    department = relationship("Department")
    teacher = relationship("User")
