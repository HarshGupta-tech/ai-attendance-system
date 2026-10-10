from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class SubjectBase(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=100)
    course_id: int
    department_id: int
    semester: int | None = None
    credits: int = 3
    teacher_id: int | None = None
    status: str = "active"

class SubjectCreate(SubjectBase): pass

class SubjectUpdate(BaseModel):
    name: str | None = None
    course_id: int | None = None
    department_id: int | None = None
    semester: int | None = None
    credits: int | None = None
    teacher_id: int | None = None
    status: str | None = None

class SubjectResponse(SubjectBase):
    id: int
    teacher_name: str | None = None
    course_name: str | None = None
    department_name: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
