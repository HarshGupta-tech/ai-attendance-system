from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class CourseBase(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=100)
    department_id: int
    duration_years: int = 2

class CourseCreate(CourseBase): pass
class CourseUpdate(BaseModel):
    name: str | None = None
    department_id: int | None = None
    duration_years: int | None = None

class CourseResponse(CourseBase):
    id: int
    department_name: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
