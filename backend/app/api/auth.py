"""Authentication API routes."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, TokenResponse, ChangePasswordRequest, StudentRegisterRequest
from app.schemas.user import UserResponse
from app.models.user import User
from app.models.student import Student
from app.core.security import hash_password

router = APIRouter()


@router.post("/login")
def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate user and return JWT token."""
    try:
        auth_service = AuthService(db)
        ip_address = request.client.host if request.client else "unknown"
        result = auth_service.authenticate(
            username=login_data.username,
            password=login_data.password,
            ip_address=ip_address,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/register")
def register(
    data: StudentRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new student."""
    # Check if user already exists
    if db.query(User).filter((User.username == data.student_id) | (User.email == data.email)).first():
        raise HTTPException(status_code=400, detail="User with this ID or email already exists")

    # Check if student ID exists
    if db.query(Student).filter(Student.student_id == data.student_id).first():
        raise HTTPException(status_code=400, detail="Student ID already exists")

    user = User(
        username=data.student_id,
        email=data.email,
        password_hash=hash_password(data.password),
        role='student',
        full_name=data.full_name,
        is_active=True
    )
    db.add(user)
    db.flush()

    student = Student(
        user_id=user.id,
        student_id=data.student_id,
        roll_number=data.roll_number,
        full_name=data.full_name,
        email=data.email,
        course_id=data.course_id,
        department_id=data.department_id,
        semester=data.semester,
        section=data.section,
        status='active'
    )
    db.add(student)
    db.commit()
    return {"message": "Registration successful"}


@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout current user."""
    auth_service = AuthService(db)
    ip_address = request.client.host if request.client else "unknown"
    auth_service.logout(user_id=current_user.id, ip_address=ip_address)
    return {"message": "Successfully logged out"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


@router.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change current user's password."""
    try:
        auth_service = AuthService(db)
        auth_service.change_password(
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
        )
        return {"message": "Password updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))