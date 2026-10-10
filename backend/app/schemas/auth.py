from pydantic import BaseModel, Field
from .user import UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse  # forward ref

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

class StudentRegisterRequest(BaseModel):
    student_id: str
    roll_number: str
    full_name: str
    email: str
    password: str
    course_id: int = 1
    department_id: int = 1
    semester: int = 1
    section: str = "A"
