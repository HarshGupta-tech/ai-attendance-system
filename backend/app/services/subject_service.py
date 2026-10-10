from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Subject
from app.schemas import SubjectCreate, SubjectUpdate
from typing import Optional, Tuple, List

class SubjectService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_subject(self, data: SubjectCreate) -> Subject:
        existing = self.db.query(Subject).filter(Subject.code == data.code).first()
        if existing:
            raise ValueError(f"Subject code {data.code} already exists")
            
        subject = Subject(**data.dict())
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject
    
    def get_subject(self, subject_id: int) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.id == subject_id).first()
    
    def get_subjects(self, page: int = 1, per_page: int = 20,
                     search: Optional[str] = None, course_id: Optional[int] = None,
                     semester: Optional[int] = None, status: Optional[str] = None) -> Tuple[List[Subject], int]:
        query = self.db.query(Subject)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Subject.code.ilike(search_filter),
                    Subject.name.ilike(search_filter)
                )
            )
            
        if course_id:
            query = query.filter(Subject.course_id == course_id)
        if semester:
            query = query.filter(Subject.semester == semester)
        if status:
            query = query.filter(Subject.status == status)
            
        total = query.count()
        subjects = query.offset((page - 1) * per_page).limit(per_page).all()
        return subjects, total
    
    def update_subject(self, subject_id: int, data: SubjectUpdate) -> Optional[Subject]:
        subject = self.get_subject(subject_id)
        if not subject:
            return None
            
        for key, value in data.dict(exclude_unset=True).items():
            setattr(subject, key, value)
            
        self.db.commit()
        self.db.refresh(subject)
        return subject
    
    def delete_subject(self, subject_id: int) -> bool:
        subject = self.get_subject(subject_id)
        if not subject:
            return False
        self.db.delete(subject)
        self.db.commit()
        return True
