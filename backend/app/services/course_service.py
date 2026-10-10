from sqlalchemy.orm import Session
from app.models import Course, Department
from app.schemas import CourseCreate, CourseUpdate
from typing import Optional, List

class CourseService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_course(self, data: CourseCreate) -> Course:
        course = Course(**data.dict())
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course
        
    def get_course(self, course_id: int) -> Optional[Course]:
        return self.db.query(Course).filter(Course.id == course_id).first()
        
    def get_courses(self, department_id: Optional[int] = None) -> List[Course]:
        query = self.db.query(Course)
        if department_id:
            query = query.filter(Course.department_id == department_id)
        return query.all()
        
    def update_course(self, course_id: int, data: CourseUpdate) -> Optional[Course]:
        course = self.get_course(course_id)
        if not course:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(course, key, value)
        self.db.commit()
        self.db.refresh(course)
        return course
        
    def delete_course(self, course_id: int) -> bool:
        course = self.get_course(course_id)
        if not course:
            return False
        self.db.delete(course)
        self.db.commit()
        return True
    
    def create_department(self, data) -> Department:
        dept = Department(**data.dict())
        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)
        return dept
        
    def get_departments(self) -> List[Department]:
        return self.db.query(Department).all()
        
    def get_department(self, dept_id: int) -> Optional[Department]:
        return self.db.query(Department).filter(Department.id == dept_id).first()
        
    def update_department(self, dept_id: int, data) -> Optional[Department]:
        dept = self.get_department(dept_id)
        if not dept:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(dept, key, value)
        self.db.commit()
        self.db.refresh(dept)
        return dept
        
    def delete_department(self, dept_id: int) -> bool:
        dept = self.get_department(dept_id)
        if not dept:
            return False
        self.db.delete(dept)
        self.db.commit()
        return True
