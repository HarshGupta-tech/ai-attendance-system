from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class DepartmentBase(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=100)

class DepartmentCreate(DepartmentBase): pass
class DepartmentUpdate(BaseModel):
    name: str | None = None

class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
