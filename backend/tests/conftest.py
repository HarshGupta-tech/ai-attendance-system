import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.session import Base
from app.main import app
from app.core.dependencies import get_db
from app.core.security import hash_password
from app.models.user import User
from app.models.department import Department
from app.models.course import Course
from app.models.student import Student
from app.models.subject import Subject

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db_session):
    """Create an admin user."""
    user = User(
        username="testadmin",
        email="admin@test.com",
        password_hash=hash_password("Admin@123"),
        full_name="Test Admin",
        role="super_admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def teacher_user(db_session):
    user = User(
        username="testteacher",
        email="teacher@test.com",
        password_hash=hash_password("Teacher@123"),
        full_name="Test Teacher",
        role="teacher",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, admin_user):
    """Get authentication headers for admin user."""
    response = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "Admin@123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def teacher_headers(client, teacher_user):
    response = client.post("/api/auth/login", json={
        "username": "testteacher",
        "password": "Teacher@123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_department(db_session):
    dept = Department(code="CS", name="Computer Science")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept

@pytest.fixture
def sample_course(db_session, sample_department):
    course = Course(code="MCA", name="Master of Computer Applications", department_id=sample_department.id)
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course

@pytest.fixture
def sample_student(db_session, sample_course, sample_department):
    student = Student(
        student_id="MCA001",
        roll_number="2024MCA001",
        full_name="Test Student",
        email="student@test.com",
        phone="9876543210",
        course_id=sample_course.id,
        department_id=sample_department.id,
        semester=3,
        section="A",
        status="active"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student

@pytest.fixture
def sample_subject(db_session, sample_course, sample_department, teacher_user):
    subject = Subject(
        code="ML101",
        name="Machine Learning",
        course_id=sample_course.id,
        department_id=sample_department.id,
        semester=3,
        credits=4,
        teacher_id=teacher_user.id
    )
    db_session.add(subject)
    db_session.commit()
    db_session.refresh(subject)
    return subject
