from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime, date

class StudentBase(BaseModel):
    student_id: str = Field(max_length=20)
    roll_number: str = Field(max_length=20)
    full_name: str = Field(max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=15)
    course_id: int
    department_id: int
    semester: int = Field(ge=1, le=10)
    section: str | None = Field(None, max_length=10)
    date_of_admission: date | None = None
    status: str = "active"

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    # All fields optional
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    course_id: int | None = None
    department_id: int | None = None
    semester: int | None = None
    section: str | None = None
    status: str | None = None

class StudentResponse(StudentBase):
    id: int
    user_id: int | None = None
    face_registered: bool = False
    created_at: datetime
    updated_at: datetime | None = None
    course_name: str | None = None
    department_name: str | None = None
    attendance_percentage: float | None = None
    model_config = ConfigDict(from_attributes=True)

class StudentListResponse(BaseModel):
    students: list[StudentResponse]
    total: int
    page: int
    per_page: int
